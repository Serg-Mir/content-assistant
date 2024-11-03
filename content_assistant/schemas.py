from pydantic import BaseModel


class TextGenerationRequest(BaseModel):
    keywords: list[str]
    domain: str
    word_count: int
    audience: str
    tone: str


class TextGenerationResponse(BaseModel):
    generated_text: str  # Base64 encoded UTF-16

    class Config:
        json_schema_extra = {"example": {"generated_text": "BASE64_ENCODED_STRING_HERE"}}
