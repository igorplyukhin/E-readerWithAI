from pydantic import BaseModel

class CompressionUpdateRequest(BaseModel):
    compressionLevel: int
