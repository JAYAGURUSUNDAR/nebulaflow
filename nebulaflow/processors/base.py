# nebulaflow/processors/base.py
from ..core.pipeline import BaseProcessor, Document
import magic  # for file type detection
import hashlib
from datetime import datetime

class MetadataProcessor(BaseProcessor):
    """Processor to extract and enrich document metadata"""
    
    async def process(self, document: Document) -> Document:
        """Enhance document metadata"""
        # Generate content hash
        document.metadata['content_hash'] = hashlib.md5(document.content).hexdigest()
        
        # Detect file type
        document.metadata['mime_type'] = self._detect_mime_type(document.content)
        
        # Add processing timestamp
        document.metadata['processed_at'] = datetime.utcnow()
        
        return document
    
    def _detect_mime_type(self, content: bytes) -> str:
        """Detect MIME type using python-magic"""
        try:
            return magic.from_buffer(content, mime=True)
        except Exception:
            return 'application/octet-stream'

class SizeProcessor(BaseProcessor):
    """Processor to add size-related metadata"""
    
    async def process(self, document: Document) -> Document:
        """Add size-related metadata"""
        document.metadata['size_bytes'] = len(document.content)
        document.metadata['size_kb'] = round(len(document.content) / 1024, 2)
        
        return document

class ContentAnalyzer(BaseProcessor):
    """Basic content analysis processor"""
    
    async def process(self, document: Document) -> Document:
        """Analyze document content"""
        # Simple word count for text content
        if document.metadata.get('mime_type', '').startswith('text/'):
            try:
                word_count = len(document.content.decode('utf-8').split())
                document.metadata['word_count'] = word_count
            except Exception:
                document.metadata['word_count'] = 0
        
        return document

class ErrorHandlingProcessor(BaseProcessor):
    """Processor with advanced error handling"""
    
    async def process(self, document: Document) -> Document:
        """Validate document and add error metadata if needed"""
        # Example validation - you can expand this
        if not document.content:
            document.metadata['validation_error'] = 'Empty document'
        
        # Maximum document size check (e.g., 10MB)
        max_size = 10 * 1024 * 1024  # 10MB
        if len(document.content) > max_size:
            document.metadata['size_warning'] = f'Document exceeds {max_size} bytes'
        
        return document