from decimal import Decimal
from typing import Optional, List

from openai import OpenAI
from pydantic import BaseModel

from dotenv import load_dotenv
load_dotenv()


class ExtractedOrderLine(BaseModel):
    description: str
    unit_price: Decimal
    amount: int
    unit: Optional[str]
    total_price: Decimal


class OfferExtraction(BaseModel):
    title: str
    vendor_name: str
    vendor_vat_id: Optional[str]
    department: Optional[str]
    order_lines: List[ExtractedOrderLine]
    total_cost: Decimal


client = OpenAI()


def extract_offer_text(text: str) -> OfferExtraction:
    completion = client.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "Extract procurement offer data from the user's text. "
                    "Return numbers as plain decimals (no currency symbols). "
                    "If a field is missing, use null. Ensure totals are consistent. "
                    "For the 'title' field, generate a concise, descriptive procurement request title "
                    "that summarises the purpose of the offer (e.g. 'Office Furniture Purchase' or "
                    "'Annual IT Support Contract')."
                ),
            },
            {"role": "user", "content": text},
        ],
        response_format=OfferExtraction,
    )

    message = completion.choices[0].message
    if message.parsed:
        return message.parsed

    raise RuntimeError(message.refusal or "Model did not return a parsed extraction.")
