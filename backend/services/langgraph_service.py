
import os
import csv
import logging
from typing import Dict, Any
from datetime import datetime

from langgraph.graph import StateGraph, END

from services.openai_service import openai_service
from schemas.dataclasses.categories import CATEGORIES
from services.pinecone_service import pinecone_service
from schemas.dataclasses.langgraph_state import LanggraphState



class LanggraphService:
    def __init__(self):
        self.graph = self._create_workflow()
        self.escalation_file = "escalation.csv"
        self._ensure_escalation_file_exists()





    def _ensure_escalation_file_exists(self):
        """Ensure the escalation CSV file exists with proper headers."""
        if not os.path.exists(self.escalation_file):
            with open(self.escalation_file, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow([
                    'timestamp', 'subject', 'description', 'category', 
                    'review_attempts', 'issues', 'draft_response'
                ])





    def _create_workflow(self) -> StateGraph:
        """Create and configure the LangGraph workflow."""

        workflow = StateGraph(LanggraphState)

        # Add nodes
        workflow.add_node("classify", self._classify_ticket)
        workflow.add_node("retrieve", self._retrieve_documents)
        workflow.add_node("draft", self._draft_response)
        workflow.add_node("review", self._review_response)
        workflow.add_node("refine", self._refine_context)
        workflow.add_node("escalate", self._escalate_ticket)
        workflow.add_node("finalize", self._finalize_response)

        # Add edges
        workflow.add_edge("classify", "retrieve")
        workflow.add_edge("retrieve", "draft")
        workflow.add_edge("draft", "review")

        # Conditional edges from review
        workflow.add_conditional_edges(
            "review",
            self._determine_next_step,
            {
                "refine": "refine",
                "escalate": "escalate",
                "finalize": "finalize"
            }
        )

        workflow.add_edge("refine", "draft")
        workflow.add_edge("escalate", END)
        workflow.add_edge("finalize", END)

        # Set entry point
        workflow.set_entry_point("classify")

        return workflow.compile()





    async def process_ticket(self, subject: str, description: str) -> Dict[str, Any]:
        """Process a ticket through the complete workflow."""
        try:
            # Initialize state
            initial_state = LanggraphState(
                subject=subject,
                description=description,
                category="",
                retrieved_docs=[],
                draft_response="",
                review_result={},
                escalated=False,
                review_attempts=0,
                final_response=""
            )

            # Run the workflow
            final_state = await self.graph.ainvoke(initial_state)
            
            # Check if ticket was escalated
            if final_state.get('escalated', False):
                return {
                    "status": "success",
                    "message": "This ticket has been escalated to human support due to complexity or policy concerns."
                }
            else:
                return {"status": "success", "message": final_state['final_response']}
            
        except Exception as e:
            logging.error(f"Workflow execution error: {e}")
            return {
                "status": "error",
                "message": f"An error occurred while processing the ticket: {str(e)}"
            }





    @staticmethod
    async def _classify_ticket(state: LanggraphState) -> LanggraphState:
        """Classify the ticket into one of the predefined categories."""
        
        try:
            llm_response = await openai_service.classify_ticket(
                text=state["description"],
                technical=CATEGORIES["technical"],
                billing=CATEGORIES["billing"],
                security=CATEGORIES["security"],
                general=CATEGORIES["general"],
                subject=state["subject"],
                description=state["description"]
            )
            
            if llm_response['status'] == 'error':
                logging.error(f"Classification error: {llm_response['message']}")
                state["category"] = "general"
                return state
            
            ticket_classification = llm_response.get("message", "")
            state["category"] = ticket_classification.category

            logging.info(f"Ticket classified as: {state['category']} with reasoning: {ticket_classification.reasoning}")
            return state

        except Exception as e:
            logging.error(f"Classification error: {e}")
            state["category"] = "general"
            return state





    @staticmethod
    async def _retrieve_documents(state: LanggraphState) -> LanggraphState:
        """Retrieve relevant documents from vector store based on category and content."""
        
        try:
            # Create search query
            query_text = f"{state['subject']} {state['description']}"
            
            # Get embedding for the query
            query_embedding = await openai_service.embed_query(query_text)
            
            # Store the query embedding for later use in refinement
            state["query_embedding"] = query_embedding

            # Search in the relevant namespace
            namespace = state["category"]
            search_response = await pinecone_service.search(
                query_vector=query_embedding,
                namespace=namespace,
                top_k=5
            )
            if search_response["status"] == "error":
                logging.error(f"Document retrieval error: {search_response['message']}")
                state["retrieved_docs"] = []
                return state
            
            retrieved_docs = search_response["data"]
            state["retrieved_docs"] = retrieved_docs

            logging.info(f"Retrieved {len(retrieved_docs)} documents from {namespace} namespace")
            return state
            
        except Exception as e:
            logging.error(f"Document retrieval error: {e}")
            state["retrieved_docs"] = []
            return state





    @staticmethod
    async def _draft_response(state: LanggraphState) -> LanggraphState:
        """Draft an initial response using retrieved context."""
        
        # Prepare context from retrieved documents
        context = ""
        for doc in state["retrieved_docs"]:
            context += f"{doc['content']}\n\n\n"

        try:
            llm_response = await openai_service.draft_response(
                category=state["category"],
                subject=state["subject"],
                description=state["description"],
                context=context
            )            
            if llm_response['status'] == 'error':
                logging.error(f"Drafting error: {llm_response['message']}")
                state["draft_response"] = "I apologize, but I'm unable to process your request at this time. Please contact our support team directly."
                return state

            draft_response = llm_response.get("message", {})
            state["draft_response"] = draft_response

            logging.info("Draft response generated successfully")
            return state

        except Exception as e:
            logging.error(f"Drafting error: {e}")
            state["draft_response"] = "I apologize, but I'm unable to process your request at this time. Please contact our support team directly."
            return state





    @staticmethod
    async def _review_response(state: LanggraphState) -> LanggraphState:
        """Review the draft response against company policies."""
        
        # Increment review attempts at the start of review
        state["review_attempts"] = state.get("review_attempts", 0) + 1
        
        try:
            llm_response = await openai_service.draft_reviewer(
                category=state["category"],
                subject=state["subject"],
                description=state["description"],
                draft_response=state["draft_response"]
            )

            if llm_response['status'] == 'error':
                logging.error(f"Review error: {llm_response['message']}")
                state["review_result"] = {
                    "approved": True,
                    "issues": [],
                    "refinement_needed": ""
                }
                return state

            review_result = llm_response.get("message", {})
            state["review_result"] = {
                "approved": review_result.approved,
                "issues": review_result.issues,
                "refinement_needed": review_result.refinement_needed
            }

            logging.info(f"Review completed - Approved: {review_result.approved}, Attempt: {state['review_attempts']}")
            return state

        except Exception as e:
            logging.error(f"Review error: {e}")
            # Default to approved if review fails
            state["review_result"] = {
                "approved": True,
                "issues": [],
                "refinement_needed": ""
            }
            return state





    @staticmethod
    async def _refine_context(state: LanggraphState) -> LanggraphState:
        """Refine the context based on review feedback."""
        
        try:
            if state['review_attempts'] == 1:
                top_k = 10
            else:
                top_k = 15

            search_response = await pinecone_service.search(
                query_vector=state["query_embedding"],
                namespace=state["category"],
                top_k=top_k
            )

            if search_response["status"] == "error":
                logging.error(f"Search error: {search_response['message']}")
                return state

            state['retrieved_docs'] = search_response["data"]

            logging.info("Context refined based on review feedback")
            return state
            
        except Exception as e:
            logging.error(f"Context refinement error: {e}")
            return state





    def _escalate_ticket(self, state: LanggraphState) -> LanggraphState:
        """Escalate the ticket by storing it in escalation.csv file."""
        
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Prepare escalation data
            escalation_data = [
                timestamp,
                state.get("subject", ""),
                state.get("description", ""),
                state.get("category", ""),
                state.get("review_attempts", 0),
                "; ".join(state.get("review_result", {}).get("issues", [])),
                state.get("draft_response", "")
            ]
            
            # Write to CSV file
            with open(self.escalation_file, 'a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(escalation_data)
            
            state["escalated"] = True
            state["final_response"] = "This ticket has been escalated to human support for further review."
            
            logging.info(f"Ticket escalated after {state['review_attempts']} attempts")
            return state
            
        except Exception as e:
            logging.error(f"Escalation error: {e}")
            # If escalation fails, provide a fallback response
            state["escalated"] = True
            state["final_response"] = "This ticket requires human support attention."
            return state





    @staticmethod
    def _determine_next_step(state: LanggraphState) -> str:
        """Determine the next step based on review results and attempts."""
        
        review_attempts = state.get("review_attempts", 0)
        is_approved = state.get("review_result", {}).get("approved", False)
        
        if is_approved:
            return "finalize"
        elif review_attempts >= 2:
            return "escalate"
        else:
            return "refine"





    @staticmethod
    def _finalize_response(state: LanggraphState) -> LanggraphState:
        """Finalize the response."""
        
        state["final_response"] = state["draft_response"]
        logging.info("Response finalized")
        
        return state



langgraph_service = LanggraphService()
graph = langgraph_service.graph
