from decimal import Decimal
from typing import Optional, List
import os
import re

from openai import OpenAI
from pydantic import BaseModel, Field, field_validator

from dotenv import load_dotenv
load_dotenv()


def clean_monetary_value(v):
    """
    Clean monetary values by removing currency symbols and handling European number formats.
    
    This validator is designed for German/European documents where:
    - Dots are thousands separators: 1.767,26 = 1767.26
    - Commas are decimal separators: 150,00 = 150.00
    
    Note: This will NOT work correctly for US-formatted numbers like "1,234.56".
    The system is designed for German procurement documents as per EXTRACTION_SYSTEM_PROMPT.
    """
    if isinstance(v, (int, float)):
        return v
    if isinstance(v, str):
        # Strip currency symbols
        v = re.sub(r'[€$£]', '', v)
        # Strip currency text
        v = re.sub(r'\s*(EUR|USD|GBP|CHF)\s*', '', v, flags=re.IGNORECASE)
        v = v.strip()
        # Handle European number format: 1.767,26 → 1767.26
        if ',' in v and '.' in v:
            v = v.replace('.', '').replace(',', '.')
        # Handle comma-only decimal: 150,00 → 150.00
        elif ',' in v:
            v = v.replace(',', '.')
        return v
    return v


class ExtractedOrderLine(BaseModel):
    product: str = Field(
        description=(
            "The product name or title. Product names are often displayed as bold headings, "
            "article names, or short labels that appear above detailed descriptions. "
            "Examples include: 'Moosbild Mix-Moos 160x80', 'Adobe Photoshop License', "
            "'Office Chair Model XY-200'. If no distinct product name exists, use the first "
            "few meaningful words of the description (e.g., 'Printer paper A4')."
        )
    )
    description: str = Field(
        description=(
            "The full description and details of the product or service, including "
            "specifications, dimensions, materials, colours, quantities, or any other "
            "relevant information stated in the line item."
        )
    )
    unit_price: Decimal = Field(
        description=(
            "The unit price per single item as stated on the document. "
            "Return as a plain decimal number without currency symbols (e.g., 150.00 not €150,00)."
        )
    )
    amount: int = Field(
        description="The quantity or amount of this item being ordered."
    )
    unit: Optional[str] = Field(
        description=(
            "The unit of measurement for the amount (e.g., 'pcs', 'licenses', 'hours', 'kg', 'm²'). "
            "Return null if not specified."
        )
    )
    total_price: Decimal = Field(
        description=(
            "The net total price for this specific line item as stated on the document. "
            "Return as a plain decimal number without currency symbols. "
            "This should be the line item's stated total, not a calculated value."
        )
    )

    @field_validator("unit_price", "total_price", mode="before")
    @classmethod
    def validate_monetary_value(cls, v):
        """Validate and clean monetary values."""
        return clean_monetary_value(v)


class OfferExtraction(BaseModel):
    title: str = Field(
        description=(
            "Generate a concise, descriptive procurement request title that summarizes "
            "the purpose of the offer. Examples: 'Office Furniture Purchase', "
            "'Annual IT Support Contract', 'Marketing Materials Order', "
            "'Moosbild Installation and Maintenance'."
        )
    )
    vendor_name: str = Field(
        description=(
            "The name of the company that SENT or ISSUED this offer — the SELLER or SUPPLIER. "
            "This is NOT the customer or recipient. Look for the vendor's name in the letterhead, "
            "header area, logo section, or footer of the document. "
            "The customer is typically identified by labels like 'Kunde', 'Kundennummer', "
            "'Kundenadresse', 'An', 'Empfänger', or 'Rechnungsadresse' — these are NOT the vendor. "
            "For example, in a quote from 'Gärtner Gregg' sent to 'Lio Technologies GmbH', "
            "the vendor_name should be 'Gärtner Gregg', NOT 'Lio Technologies GmbH'."
        )
    )
    vendor_vat_id: Optional[str] = Field(
        description=(
            "The vendor's VAT identification number. Look for common German labels such as: "
            "'USt-IdNr.', 'USt-IdNr', 'Umsatzsteuer-ID', 'UID-Nr.', 'Steuernummer', 'VAT ID', "
            "or 'MwSt-Nr.'. The format is typically 'DE' followed by 9 digits for German companies "
            "(e.g., 'DE198570491'). This information is usually found in the header, footer, or "
            "company details section of the document. Return null if not present."
        )
    )
    department: Optional[str] = Field(
        description=(
            "The department or organizational unit requesting the procurement. "
            "This information is usually NOT present on vendor offers. Return null if not found."
        )
    )
    order_lines: List[ExtractedOrderLine] = Field(
        description="The list of individual line items from the offer, each representing a product or service."
    )
    total_cost: Decimal = Field(
        description=(
            "The TOTAL NET cost as explicitly stated on the document. "
            "Look for labels such as: 'Nettobetrag', 'Summe netto', 'Zwischensumme', "
            "'Gesamtbetrag netto', 'Summe (netto)', or 'Subtotal'. "
            "Do NOT calculate this by summing line items — read the stated value from the document. "
            "The document's stated net total takes precedence over any calculations. "
            "Return as a plain decimal number without currency symbols (e.g., 1767.26 not €1.767,26)."
        )
    )

    @field_validator("total_cost", mode="before")
    @classmethod
    def validate_monetary_value(cls, v):
        """Validate and clean monetary values."""
        return clean_monetary_value(v)


EXTRACTION_SYSTEM_PROMPT = """You are a procurement document analyst specializing in extracting structured data from vendor quotes, offers, and invoices — primarily in German but also English.

CRITICAL RULES:

1. VENDOR vs. CUSTOMER DISTINCTION:
   - The document is a quote SENT BY the vendor TO a customer.
   - The VENDOR is the company issuing the document — found in the letterhead, header, logo area, or footer.
   - The CUSTOMER is the recipient — identified by labels like 'Kunde', 'Kundennummer', 'Kundenadresse', 'An', 'Empfänger', 'Rechnungsadresse'.
   - The customer is NOT the vendor. Always extract the vendor's name, not the customer's name.

2. VAT ID EXTRACTION:
   - Look for German VAT labels: 'USt-IdNr.', 'USt-IdNr', 'Umsatzsteuer-ID', 'UID-Nr.', 'Steuernummer', 'VAT ID', 'MwSt-Nr.'
   - Usually found in the header, footer, or company details section.
   - German format: 'DE' followed by 9 digits (e.g., 'DE198570491').

3. TOTAL COST:
   - Read the net total (Nettobetrag/Summe netto/Zwischensumme) exactly as stated on the document.
   - Do NOT compute by summing line items. The document's stated total takes precedence.
   - Common labels: 'Nettobetrag', 'Summe netto', 'Zwischensumme', 'Gesamtbetrag netto', 'Summe (netto)', 'Subtotal'.

4. PRODUCT NAMES:
   - Extract short product names or titles — often bold headings, article numbers with names, or short labels before detailed descriptions.
   - Examples: 'Moosbild Mix-Moos 160x80', 'Adobe Photoshop License', 'Office Chair Model XY-200'.
   - If no distinct product name exists, use the first few meaningful words of the description.

5. MONETARY VALUES:
   - Return all monetary values as plain decimals without currency symbols (e.g., 1767.26 not €1.767,26).

6. NULL VALUES:
   - If a field is genuinely not present in the document, use null.

EXAMPLE:
Given a document from 'Gärtner Gregg' addressed to customer 'Lio Technologies GmbH' with USt-IdNr. DE198570491 in the vendor's details section and a Nettobetrag of €1767.26:
- vendor_name should be 'Gärtner Gregg' (NOT 'Lio Technologies GmbH')
- vendor_vat_id should be 'DE198570491'
- total_cost should be 1767.26"""


# Only initialize OpenAI client if API key is available
client = None
if os.getenv("OPENAI_API_KEY"):
    client = OpenAI()


def extract_offer_text(text: str) -> OfferExtraction:
    if not client:
        raise RuntimeError(
            "OpenAI API key is not configured. "
            "Please set OPENAI_API_KEY in your .env file or environment variables."
        )
    
    completion = client.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": EXTRACTION_SYSTEM_PROMPT,
            },
            {"role": "user", "content": text},
        ],
        response_format=OfferExtraction,
    )

    message = completion.choices[0].message
    if message.parsed:
        return message.parsed

    raise RuntimeError(message.refusal or "Model did not return a parsed extraction.")
