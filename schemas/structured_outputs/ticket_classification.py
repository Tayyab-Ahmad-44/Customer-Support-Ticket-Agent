
from pydantic import BaseModel, Field


class TicketClassificationSchema(BaseModel):
    """Schema for ticket classification output."""
    
    category: str = Field(
        description="The category of the support ticket. Possible values: technical, billing, security, general."
    )
    reasoning: str = Field(
        description="The reason for the classification of the support ticket."
    )
