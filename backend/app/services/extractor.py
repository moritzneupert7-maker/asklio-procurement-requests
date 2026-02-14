from decimal import Decimal
from typing import Optional, List
import os

from openai import OpenAI
from pydantic import BaseModel

from dotenv import load_dotenv
load_dotenv()


class ExtractedOrderLine(BaseModel):
    product: str  # Product name
    description: str  # Full description/details
    unit_price: Decimal
    amount: int
    unit: Optional[str]
    total_price: Decimal


class OfferExtraction(BaseModel):
    vendor_name: str
    vendor_vat_id: Optional[str]
    department: Optional[str]
    order_lines: List[ExtractedOrderLine]
    total_cost: Decimal


# Only initialize OpenAI client if API key is available
client = None
if os.getenv("OPENAI_API_KEY"):
    client = OpenAI()


def extract_offer_text(text: str) -> OfferExtraction:
    if not client:
        raise RuntimeError("OpenAI API key is not configured. Please set OPENAI_API_KEY environment variable.")
    
    completion = client.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an expert at extracting procurement offer data from documents. "
                    "Extract all relevant information accurately from the provided text.\n\n"
                    "IMPORTANT INSTRUCTIONS:\n"
                    "- Return all monetary values as plain decimals without currency symbols (e.g., 150.00, not €150 or $150)\n"
                    "- Extract the vendor name (company/organization providing the offer)\n"
                    "- Extract VAT ID (Umsatzsteuer-Identifikationsnummer, USt.-ID, or similar tax identification number)\n"
                    "- Extract the department name (requestor department, offered to, customer department)\n"
                    "- For each order line/item, extract:\n"
                    "  * product: Short product name/title (e.g., 'Adobe Photoshop License', 'Moosbild Mix-Moos')\n"
                    "  * description: Complete description with all details and specifications\n"
                    "  * unit_price: Price per single unit\n"
                    "  * amount: Quantity ordered\n"
                    "  * unit: Unit of measurement (e.g., 'licenses', 'Stk.', 'pcs')\n"
                    "  * total_price: Total price for this line (unit_price × amount, after any discounts)\n"
                    "- Calculate total_cost as the sum of all order line totals\n"
                    "- Verify that total_cost matches the document's total amount\n"
                    "- If a field is not found in the document, use null\n"
                    "- Be precise with numbers - extract exact values from the document"
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
