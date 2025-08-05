
from pydantic import BaseModel, Field


class TicketReviewerSchema(BaseModel):
    """Schema for Ticket Reviewer"""
    
    approved: bool = Field(
        description="Indicates whether the draft response is approved or not."
    )
    
    issues: list[str] = Field(
        description="List of issues identified in the draft response."
    )

    refinement_needed: str = Field(
        description="Indicates whether refinement is needed or not."
    )
