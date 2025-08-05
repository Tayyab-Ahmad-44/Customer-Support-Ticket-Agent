
from fastapi import APIRouter

from schemas.routes.query import QueryRequest
from services.langgraph_service import langgraph_service


router = APIRouter()



@router.post("/query")
async def query(request: QueryRequest):
    """Handle query requests and process them through the LangGraph workflow."""

    subject = request.subject
    description = request.description


    return await langgraph_service.process_ticket(subject, description)
