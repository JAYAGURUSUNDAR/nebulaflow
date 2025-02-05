import asyncio
import logging
from typing import (
    Any, Callable, Dict, List, Optional
)
from document import Document, DocumentStatus


class ProcessingContext:
    """Advanced processing context management"""
    
    def __init__(self, 
                 max_retries: int = 3, 
                 timeout: float = 60.0,
                 retry_delay: float = 1.0):
        self.max_retries = max_retries
        self.timeout = timeout
        self.retry_delay = retry_delay
        self.logger = logging.getLogger(self.__class__.__name__)
    
    async def execute(self, 
                      coroutine: Callable, 
                      *args, 
                      **kwargs) -> Any:
        """Execute a coroutine with retry and timeout mechanisms"""
        for attempt in range(self.max_retries):
            try:
                return await asyncio.wait_for(
                    coroutine(*args, **kwargs), 
                    timeout=self.timeout
                )
            except asyncio.TimeoutError:
                self.logger.warning(f"Timeout on attempt {attempt + 1}")
                if attempt == self.max_retries - 1:
                    raise
            except Exception as e:
                self.logger.error(f"Error on attempt {attempt + 1}: {e}")
                if attempt == self.max_retries - 1:
                    raise
                await asyncio.sleep(self.retry_delay * (2 ** attempt))
        
        raise RuntimeError("Max retries exceeded")

class BaseProcessor:
    """Sophisticated base processor for document transformation"""
    
    def __init__(self, 
                 name: Optional[str] = None, 
                 config: Optional[Dict[str, Any]] = None):
        self.name = name or self.__class__.__name__
        self.config = config or {}
        self.logger = logging.getLogger(f"processor.{self.name}")
        self.processing_context = ProcessingContext()
    
    async def process(self, document: Document) -> Document:
        """Process a document with comprehensive error handling"""
        try:
            document.update_status(DocumentStatus.PROCESSING)
            result = await self.processing_context.execute(
                self._transform, document
            )
            document.update_status(DocumentStatus.COMPLETED)
            return result
        except Exception as e:
            error_msg = f"Processing failed: {str(e)}"
            self.logger.error(error_msg)
            document.update_status(DocumentStatus.FAILED, error=error_msg)
            return document
    
    async def _transform(self, document: Document) -> Document:
        """Core transformation logic to be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement transformation")

class Pipeline:
    """Robust document processing pipeline"""
    
    def __init__(self, processors: Optional[List[BaseProcessor]] = None):
        self.processors = processors or []
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def add_processor(self, processor: BaseProcessor):
        """Add processor to pipeline"""
        self.processors.append(processor)
        return self
    
    async def process(self, documents: List[Document]) -> List[Document]:
        """Process multiple documents through pipeline"""
        processed_documents = []
        
        for document in documents:
            try:
                processed_doc = await self._process_single_document(document)
                processed_documents.append(processed_doc)
            except Exception as e:
                self.logger.error(f"Pipeline processing error: {e}")
                document.update_status(DocumentStatus.FAILED, str(e))
                processed_documents.append(document)
        
        return processed_documents
    
    async def _process_single_document(self, document: Document) -> Document:
        """Process a single document through all processors"""
        for processor in self.processors:
            document = await processor.process(document)
            
            if document.status == DocumentStatus.FAILED:
                break
        
        return document

# Logging Configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)