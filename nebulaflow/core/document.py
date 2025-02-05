from dataclasses import dataclass, field, asdict
from enum import Enum, auto
from uuid import uuid4, UUID
from datetime import datetime
import hashlib
from typing import Any, Dict, Optional



class DocumentStatus(Enum):
    """Comprehensive document processing status"""
    PENDING = auto()
    QUEUED = auto()
    PROCESSING = auto()
    PARTIAL = auto()
    COMPLETED = auto()
    FAILED = auto()
    RETRY = auto()
    SKIPPED = auto()

@dataclass
class Document:
    """Enhanced document representation"""
    id: UUID = field(default_factory=uuid4)
    content: Any = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    status: DocumentStatus = DocumentStatus.PENDING
    created_at: datetime = field(default_factory=datetime.utcnow)
    processed_at: Optional[datetime] = None
    error: Optional[str] = None
    
    def __post_init__(self):
        """Post-initialization validations and enrichments"""
        if not self.metadata:
            self.metadata = {}
        
        # Generate content hash for tracking
        if self.content:
            self.metadata['content_hash'] = self._generate_content_hash()
    
    def _generate_content_hash(self) -> str:
        """Generate a consistent hash for document content"""
        content_str = str(self.content).encode('utf-8')
        return hashlib.md5(content_str).hexdigest()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert document to dictionary"""
        doc_dict = asdict(self)
        doc_dict['status'] = self.status.name
        doc_dict['id'] = str(self.id)
        return doc_dict
    
    def update_status(self, status: DocumentStatus, error: Optional[str] = None):
        """Update document status with optional error"""
        self.status = status
        if error:
            self.error = error
        if status in [DocumentStatus.COMPLETED, DocumentStatus.FAILED]:
            self.processed_at = datetime.utcnow()
