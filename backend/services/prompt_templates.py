
TICKET_CLASSIFICAION_PROMPT = """
You are a ticket classification system. Classify the following ticket into one of these categories:

Categories:
- technical: {technical}
- billing: {billing}
- security: {security}
- general: {general}

Ticket Subject: {subject}
Ticket Description: {description}

Respond with only the category name (technical, billing, security, or general) and a short reasoning of why you classified it that way.
"""





DRAFT_RESPONSE_PROMPT = """
You are a customer support assistant. Draft a helpful response to the following ticket using the provided context.

Ticket Category: {category}
Subject: {subject}
Description: {description}

Context from knowledge base:
{context}

Guidelines:
- Be professional and empathetic
- Provide specific solutions when possible
- Reference relevant documentation
- Keep the response concise but comprehensive
- If you cannot resolve the issue completely, provide next steps
"""





REVIEW_PROMPT = """
You are a policy compliance reviewer. Review the following customer support response for:

1. Professional tone and language
2. Accuracy of information provided
3. Compliance with company policies
4. Completeness of the solution
5. Appropriate level of detail

Ticket Category: {category}
Original Ticket: {subject} - {description}

Draft Response:
{draft_response}

Provide your review in the following JSON format:
{{
    "approved": true/false,
    "refinement_needed": "specific areas that need refinement"
}}
"""





REFINEMENT_PROMPT = """
Based on the review feedback, refine the context for better response generation.

Original Context:
{context}

Review Feedback:
Issues: {issues}
Refinement Needed: {refinement_needed}

Provide refined context that addresses the review feedback.
"""