from typing import Optional

class PIEEError(Exception):
    """Base exception for all PIEE errors."""
    pass

class PIEEAPIError(PIEEError):
    """Exception raised for errors returned from the PIEE API."""
    def __init__(
        self,
        message: str,
        status: int,
        type_: str,
        code: Optional[str] = None,
        param: Optional[str] = None,
    ):
        super().__init__(message)
        self.status = status
        self.type = type_
        self.code = code
        self.param = param
