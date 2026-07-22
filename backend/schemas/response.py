from pydantic import BaseModel
from typing import Generic, TypeVar, Optional

T = TypeVar('T')

class APIEnvelope(BaseModel, Generic[T]):
    success: bool = True
    message: str = "Operation completed successfully"
    data: Optional[T] = None
    error: Optional[str] = None
