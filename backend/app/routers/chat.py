from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from openai import OpenAI
import os

from ..db import get_db
from .. import models, schemas

router = APIRouter(prefix="/chat", tags=["chat"])

# Initialize OpenAI client
client = None
if os.getenv("OPENAI_API_KEY"):
    client = OpenAI()


@router.post("", response_model=schemas.ChatResponse)
def chat_with_asklio(payload: schemas.ChatRequest, db: Session = Depends(get_db)):
    """
    Chat with AskLio virtual assistant about procurement requests and policies.
    """
    if not client:
        raise HTTPException(
            status_code=503,
            detail="OpenAI API key is not configured."
        )
    
    # Fetch all requests for context
    requests = db.query(models.ProcurementRequest).all()
    
    # Build context about requests
    requests_context = []
    for req in requests:
        req_summary = (
            f"Request #{req.id}: {req.title} | "
            f"Requestor: {req.requestor_name} | "
            f"Department: {req.department} | "
            f"Vendor: {req.vendor_name} | "
            f"Status: {req.current_status} | "
            f"Total Cost: €{req.total_cost}"
        )
        if req.commodity_group:
            req_summary += f" | Commodity Group: {req.commodity_group.name}"
        requests_context.append(req_summary)
    
    context_text = "\n".join(requests_context) if requests_context else "No requests in system yet."
    
    # System prompt for AskLio
    system_prompt = f"""You are AskLio, a helpful procurement assistant for a company's procurement portal.

Your role is to:
1. Answer questions about the user's procurement requests
2. Provide guidance on procurement policies and best practices
3. Help users understand their spending patterns and request statuses

Current Procurement Requests:
{context_text}

When answering:
- Be concise and helpful
- Reference specific request numbers when relevant
- If asked about policies, provide general best practices for procurement
- If you don't have information, say so clearly
"""
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": payload.message}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        reply = response.choices[0].message.content
        return {"reply": reply}
    
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Chat failed: {str(e)}")
