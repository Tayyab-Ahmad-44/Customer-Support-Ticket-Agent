
import json
import logging
from typing import Any

from pydantic import BaseModel
from langchain.schema import HumanMessage, SystemMessage
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter

from core.config import settings
from schemas.structured_outputs.ticket_reviewer import TicketReviewerSchema
from schemas.structured_outputs.ticket_classification import TicketClassificationSchema
from services.prompt_templates import TICKET_CLASSIFICAION_PROMPT, DRAFT_RESPONSE_PROMPT, REVIEW_PROMPT, REFINEMENT_PROMPT



class OpenAIService:
    def __init__(self):
        """Initialize OpenAI service""" 

        self.llm = ChatOpenAI(model=settings.MODEL_NAME, api_key=settings.OPENAI_API_KEY)
        self.embeddings = OpenAIEmbeddings(model=settings.EMBEDDING_MODEL_NAME, openai_api_key=settings.OPENAI_API_KEY)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=2000,
            chunk_overlap=200,
            length_function=len,
        )





    async def generate_embeddings(self, texts: list) -> list:
        """Generate embeddings for a list of texts"""
        
        if not texts:
            return []
        
        try:
            embeddings = self.embeddings.embed_documents(texts)
            return embeddings

        except Exception as e:
            logging.error(f"Failed to generate embeddings: {str(e)}")
            return []




    async def embed_query(self, query: str) -> list:
        """Generate embedding for a single query"""
        
        try:
            embedding = self.embeddings.embed_query(query)
            return embedding

        except Exception as e:
            logging.error(f"Failed to embed query: {str(e)}")
            return []





    async def classify_ticket(self, text: str, technical, billing, security, general, subject, description, schema=None) -> dict:
        """Classify a support ticket into a predefined category."""
        
        prompt = self._replacer(
            TICKET_CLASSIFICAION_PROMPT,
            technical=technical,
            billing=billing,
            security=security,
            general=general,
            subject=subject,
            description=description
        )

        return self._process_request(prompt, text, schema=TicketClassificationSchema)





    async def draft_response(self, category: str, subject: str, description: str, context: str) -> dict:
        """Draft a response to a support ticket based on the category."""
        
        prompt = self._replacer(
            DRAFT_RESPONSE_PROMPT,
            category=category,
            subject=subject,
            description=description,
            context=context
        )

        return self._process_request(prompt, text="", schema=None)





    async def draft_reviewer(self, category: str, subject: str, description: str, draft_response: str) -> dict:
        """Review a draft response for compliance and quality."""
        
        prompt = self._replacer(
            REVIEW_PROMPT,
            category=category,
            subject=subject,
            description=description,
            draft_response=draft_response
        )

        return self._process_request(prompt, text="", schema=TicketReviewerSchema)





    async def refine_context(self, context: str, issues: list[str], refinement_needed: str) -> dict:
        """Refine a draft response based on identified issues."""
        
        prompt = self._replacer(
            REFINEMENT_PROMPT,
            context=context,
            issues=issues,
            refinement_needed=refinement_needed
        )

        return self._process_request(prompt, text="", schema=None)





    def _replacer(self, prompt: str, **kwargs: Any) -> str:
        """Replaces placeholders in a prompt with actual serialized values."""

        for key, value in kwargs.items():
            placeholder = f"{{{key}}}"

            if placeholder not in prompt:
                continue 

            if isinstance(value, str):
                replacement = value
            elif isinstance(value, (dict, list)):
                replacement = json.dumps(value, ensure_ascii=False, indent=4)
            elif isinstance(value, BaseModel):
                replacement = json.dumps(value.model_dump(), ensure_ascii=False, indent=4)
            else:
                try:
                    replacement = json.dumps(value, ensure_ascii=False, indent=4)
                except TypeError:
                    replacement = str(value)

            prompt = prompt.replace(placeholder, replacement)

        return prompt





    def _process_request(
        self, prompt: str, text: str, schema=None
    ):
        """Generic method to handle requests to OpenAI"""

        try:
            messages = [
                SystemMessage(content=prompt),
                HumanMessage(content=text)
            ]


            # Initialize llm_instance with structured output if schema is provided else use simple llm to invoke.
            llm_instance = self.llm.with_structured_output(schema) if schema else self.llm  
            response = llm_instance.invoke(messages)


            return {"status": "success", "message": response.content if not schema else response}

        except Exception as e:
            return {"status": "error", "message": f"Error processing request: {e}"}



openai_service = OpenAIService()
