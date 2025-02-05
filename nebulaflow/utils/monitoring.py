# nebulaflow/utils/monitoring.py
import logging
import time
from typing import Callable, Any
import asyncio

class PipelineMonitor:
    """Monitoring utility for tracking pipeline performance"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.metrics = {
            'total_documents': 0,
            'processed_documents': 0,
            'failed_documents': 0,
            'processing_time': 0,
        }
    
    async def track_processing_time(self, func: Callable) -> Callable:
        """Decorator to track processing time of a method"""
        async def wrapper(*args: Any, **kwargs: Any):
            start_time = time.time()
            result = await func(*args, **kwargs)
            processing_time = time.time() - start_time
            
            self.metrics['processing_time'] += processing_time
            self.metrics['total_documents'] += 1
            
            return result
        return wrapper
    
    def get_metrics(self):
        """Retrieve current metrics"""
        return self.metrics
    
    def reset_metrics(self):
        """Reset all metrics"""
        self.metrics = {
            'total_documents': 0,
            'processed_documents': 0,
            'failed_documents': 0,
            'processing_time': 0,
        }

# nebulaflow/utils/config.py
from dataclasses import dataclass

@dataclass
class PipelineConfig:
    """Configuration for document processing pipeline"""
    batch_size: int = 10
    max_workers: int = 5
    max_document_size: int = 10 * 1024 * 1024  # 10MB
    allowed_mime_types: list = None
    
    def __post_init__(self):
        if self.allowed_mime_types is None:
            self.allowed_mime_types = [
                'text/plain', 
                'application/pdf', 
                'image/png', 
                'image/jpeg'
            ]