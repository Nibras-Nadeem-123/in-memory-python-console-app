"""Specification generation API endpoints."""

from datetime import datetime
from typing import Dict

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field, ValidationError

from app.core.engine import Engine
from app.models.intent import UserIntent
from app.models.spec import StructuredSpec

router = APIRouter(prefix="/api/v1", tags=["spec"])

# Initialize engine
engine = Engine()


class IntentRequest(BaseModel):
    """Request model for intent submission."""

    text: str = Field(
        ...,
        min_length=50,
        max_length=5000,
        description="Natural language description of desired system (50-500 words)",
    )


class ErrorResponse(BaseModel):
    """Standard error response model."""

    error: str = Field(..., description="Error message")
    details: str = Field(..., description="Detailed explanation")
    code: str = Field(..., description="Error code for programmatic handling")


class AmbiguousIntentError(ErrorResponse):
    """Error response for ambiguous intent."""

    suggestions: list[str] = Field(
        default_factory=list,
        description="Suggestions for clarifying intent",
    )


class HealthResponse(BaseModel):
    """Health check response model."""

    status: str = Field(..., description="Service health status")
    version: str = Field(..., description="API version")
    timestamp: str = Field(..., description="Current server time")


@router.post(
    "/spec",
    response_model=StructuredSpec,
    status_code=status.HTTP_200_OK,
    responses={
        400: {
            "model": ErrorResponse,
            "description": "Invalid input - validation failed",
        },
        422: {
            "model": AmbiguousIntentError,
            "description": "Ambiguous intent - unable to generate complete spec",
        },
        500: {
            "model": ErrorResponse,
            "description": "Internal server error",
        },
    },
    summary="Generate structured specification from user intent",
    description="""
    Accepts natural language description and returns structured specification.

    **Processing Steps**:
    1. Validate input (word count, encoding)
    2. Extract goal and entities
    3. Identify constraints and assumptions
    4. Calculate confidence score
    5. Return structured spec with metadata
    """,
)
async def generate_spec(request: IntentRequest) -> StructuredSpec:
    """
    Generate structured specification from user intent.

    Args:
        request: Intent request with text

    Returns:
        Complete structured specification

    Raises:
        HTTPException: 400 for validation errors, 422 for ambiguous intent, 500 for server errors
    """
    try:
        # Validate word count
        words = len(request.text.split())
        if words < 50:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "Invalid input",
                    "details": f"Intent text must contain at least 50 words. Received: {words} words.",
                    "code": "VALIDATION_ERROR",
                },
            )
        if words > 500:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "Invalid input",
                    "details": f"Intent text must contain at most 500 words. Received: {words} words.",
                    "code": "VALIDATION_ERROR",
                },
            )

        # Create UserIntent model
        intent = UserIntent(text=request.text)

        # Generate specification
        spec = engine.execute(intent)

        return spec

    except ValidationError as e:
        # Pydantic validation error
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "Invalid input",
                "details": str(e),
                "code": "VALIDATION_ERROR",
            },
        )

    except ValueError as e:
        # Ambiguous intent - couldn't extract required information
        error_msg = str(e)

        suggestions = []
        if "goal" in error_msg.lower():
            suggestions = [
                "Specify the main purpose or problem this system should solve",
                "Describe what users should be able to accomplish",
            ]
        elif "entities" in error_msg.lower() or "entity" in error_msg.lower():
            suggestions = [
                "Describe the key things users will interact with",
                "List the main data types or resources in the system",
            ]

        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error": "Ambiguous intent",
                "details": error_msg,
                "code": "AMBIGUOUS_INTENT",
                "suggestions": suggestions,
            },
        )

    except Exception as e:
        # Internal server error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Internal server error",
                "details": f"An unexpected error occurred during spec generation: {str(e)}",
                "code": "INTERNAL_ERROR",
            },
        )


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Health check endpoint",
    description="Returns service health status and version information",
)
async def health_check() -> Dict[str, str]:
    """
    Health check endpoint.

    Returns:
        Service health status and version
    """
    return {
        "status": "healthy",
        "version": "0.1.0",
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }
