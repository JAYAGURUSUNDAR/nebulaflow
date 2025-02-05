# nebulaflow/core/pipeline.py
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, AsyncIterator, Optional
from enum import Enum
from datetime import datetime
import asyncio
import logging
import uuid

class DocumentStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class Document:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content: bytes = field(default_factory=bytes)
    metadata: dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    status: DocumentStatus = DocumentStatus.PENDING
    error: Optional[str] = None

class PipelineError(Exception):
    """Base exception for pipeline-related errors"""
    pass

class ProcessingError(PipelineError):
    """Raised when document processing fails"""
    pass

class Pipeline:
    def __init__(self, batch_size: int = 10, max_workers: int = 5):
        self.batch_size = batch_size
        self.max_workers = max_workers
        self.processors = []
        self.logger = logging.getLogger(__name__)
        
    def add_processor(self, processor):
        """Add a processing step to the pipeline"""
        self.processors.append(processor)
    
    async def process_document(self, doc: Document) -> Document:
        """Process a single document through all processors"""
        try:
            doc.status = DocumentStatus.PROCESSING
            
            for processor in self.processors:
                doc = await processor.process(doc)
                
            doc.status = DocumentStatus.COMPLETED
            return doc
            
        except Exception as e:
            doc.status = DocumentStatus.FAILED
            doc.error = str(e)
            self.logger.error(f"Failed to process document {doc.id}: {e}")
            raise ProcessingError(f"Processing failed for document {doc.id}") from e

    async def process_batch(self, docs: List[Document]) -> List[Document]:
        """Process a batch of documents in parallel"""
        semaphore = asyncio.Semaphore(self.max_workers)
        
        async def process_with_semaphore(doc):
            async with semaphore:
                return await self.process_document(doc)
        
        tasks = [process_with_semaphore(doc) for doc in docs]
        
        results = []
        errors = []
        
        for task in asyncio.as_completed(tasks):
            try:
                doc = await task
                results.append(doc)
            except ProcessingError as e:
                errors.append(e)
                self.logger.error(f"Batch processing error: {e}")
        
        if errors:
            self.logger.warning(f"Batch completed with {len(errors)} errors")
            
        return results

    async def process_stream(self, docs: List[Document]) -> AsyncIterator[Document]:
        """Process a stream of documents in batches"""
        for i in range(0, len(docs), self.batch_size):
            batch = docs[i:i+self.batch_size]
            processed_batch = await self.process_batch(batch)
            
            for doc in processed_batch:
                yield doc

# Example of a base processor
class BaseProcessor:
    """Base class for document processors"""
    
    async def process(self, document: Document) -> Document:
        """Process a single document"""
        raise NotImplementedError("Processors must implement process()")