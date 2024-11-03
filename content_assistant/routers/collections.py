from fastapi import APIRouter, status, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from content_assistant.schemas import TextGenerationRequest, TextGenerationResponse
from content_assistant.core.content_generator import generate_text
import logging

logger = logging.getLogger("content_assistant_app")

router = APIRouter()


@router.post(
    "/generate_text", response_model=TextGenerationResponse, status_code=status.HTTP_200_OK
)
async def generate_text_endpoint(request: TextGenerationRequest):
    """
    Endpoint to generate text based on user input.

    Args:
        request (TextGenerationRequest): The input request containing keywords, domain, audience, tone, and word count.

    Returns:
        JSONResponse: A response containing the text in UTF16 format or an error message.

    Raises:
        HTTPException: If any error occurs during processing.
    """
    try:
        logger.info(f"Received request for text generation with parameters: {request.model_dump()}")
        generated_text = await generate_text(
            keywords=request.keywords,
            domain=request.domain,
            word_count=request.word_count,
            audience=request.audience,
            tone=request.tone,
        )
        return JSONResponse(content={"generated_text": generated_text})

    except SQLAlchemyError as e:
        logger.error(f"Database error occurred: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="A database error occurred."
        )

    except ValueError as e:
        logger.warning(f"Validation error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal server error occurred.",
        )
