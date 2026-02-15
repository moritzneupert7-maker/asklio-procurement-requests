import os
from decimal import Decimal
from typing import Optional, List
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field

load_dotenv()
client = OpenAI()

class TestExtraction(BaseModel):
    vendor_name: str
    total_cost: Decimal

try:
    completion = client.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Extract vendor name and total cost from this text."},
            {"role": "user", "content": "Invoice from ACME Corp. Total: 500.00 EUR"},
        ],
        response_format=TestExtraction,
    )
    print("SUCCESS:", completion.choices[0].message.parsed)
except Exception as e:
    print(f"ERROR TYPE: {type(e).__name__}")
    print(f"ERROR: {e}")