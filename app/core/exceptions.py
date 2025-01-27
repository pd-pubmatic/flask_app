class AdWiseException(Exception):
    """Base exception for AdWise application"""
    pass

class VideoProcessingError(AdWiseException):
    """Raised when video processing fails"""
    pass

class AIProcessingError(AdWiseException):
    """Raised when AI processing fails"""
    pass

class StorageError(AdWiseException):
    """Raised when storage operations fail"""
    pass

class CallbackError(AdWiseException):
    """Raised when callback operations fail"""
    pass 