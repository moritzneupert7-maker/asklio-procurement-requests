from decimal import Decimal
from typing import Optional, List
import os
import re
import logging

from openai import OpenAI
from pydantic import BaseModel, Field, field_validator

from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger(__name__)


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
        default="Unknown Product",
        description=(
            "The SHORT product name or title — this is the first prominent line/heading of the line item, "
            "NOT the full description. In German quotes, this is typically the bold or first line in the "
            "'Bezeichnung' column that appears BEFORE detailed specifications begin. "
            "Examples from real documents: "
            "'13\" MacBook Air: Apple M2 Chip – Space Grau', "
            "'Moosbild \"70:30\" mit Schriftzug \"askLio\"', "
            "'Moosbild Mix-Moos 160x80 cm', "
            "'Logointegration \"asklio\" horizontal', "
            "'Adobe Photoshop License'. "
            "IMPORTANT: This must be a SHORT name (typically 3-10 words), NOT the full description. "
            "If the line item text starts with a short product title followed by detailed specs, "
            "extract ONLY the short title as the product. "
            "This field must NEVER be empty, null, or '-'."
        )
    )
    description: str = Field(
        default="",
        description=(
            "The detailed description and specifications that follow AFTER the product name. "
            "This includes dimensions, materials, configurations, colours, technical specs, "
            "and any other details. Do NOT repeat the product name in the description. "
            "For example, if the product is 'Moosbild Mix-Moos 160x80 cm', the description would be "
            "'Moosart: Mix-Moos, Außenabmessungen: ca. 160x80 cm, Rahmen: Holzrahmen MDF, "
            "Rahmenfarbe: Weiß oder Schwarz, inkl. Befestigungsmittel'."
        )
    )
    unit_price: Decimal = Field(
        default=Decimal("0.00"),
        description=(
            "The unit price per single item as stated on the document. "
            "Return as a plain decimal number without currency symbols (e.g., 150.00 not €150,00)."
        )
    )
    amount: int = Field(
        default=1,
        description="The quantity or amount of this item being ordered."
    )
    unit: Optional[str] = Field(
        default=None,
        description=(
            "The unit of measurement for the amount (e.g., 'pcs', 'licenses', 'hours', 'kg', 'm²'). "
            "Return null if not specified."
        )
    )
    total_price: Decimal = Field(
        default=Decimal("0.00"),
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
        default="Procurement Request",
        description=(
            "Generate a concise, descriptive procurement request title that summarizes "
            "the purpose of the offer. Examples: 'Office Furniture Purchase', "
            "'Annual IT Support Contract', 'Marketing Materials Order', "
            "'Moosbild Installation and Maintenance'."
        )
    )
    vendor_name: str = Field(
        default="Unknown Vendor",
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
        default=None,
        description=(
            "The vendor's VAT identification number. Look for common German labels such as: "
            "'USt-IdNr.', 'USt-IdNr', 'Umsatzsteuer-ID', 'UID-Nr.', 'Steuernummer', 'VAT ID', "
            "or 'MwSt-Nr.'. The format is typically 'DE' followed by 9 digits for German companies "
            "(e.g., 'DE198570491'). This information is usually found in the header, footer, or "
            "company details section of the document. Return null if not present."
        )
    )
    department: Optional[str] = Field(
        default=None,
        description=(
            "The department this procurement request belongs to, if identifiable from the document. "
            "Return null if not present."
        )
    )
    order_lines: List[ExtractedOrderLine] = Field(
        default_factory=list,
        description=(
            "The list of individual line items from the offer, each representing a product or service. "
            "IMPORTANT: If the document lists shipping or transport costs as a separate line or position "
            "(e.g., 'Versandkosten netto: €113.85', 'Transport, Verpackung und Versand', 'Frachtkosten'), "
            "these MUST be extracted as their own order line item. "
            "Common German shipping cost labels: 'Versandkosten', 'Versand', 'Transport', 'Lieferkosten', "
            "'Frachtkosten', 'Speditionskosten', 'Verpackung und Versand', 'Porto'. "
            "Use the shipping label as the product name (e.g., 'Versandkosten', 'Transport, Verpackung und Versand')."
        )
    )
    total_cost: Decimal = Field(
        default=Decimal("0.00"),
        description=(
            "The TOTAL NET cost (before tax/VAT) as explicitly stated on the document. "
            "This must ALWAYS be the NET total, NEVER the gross total. "
            "\n"
            "German labels for NET total (USE THESE): "
            "'Nettosumme', 'Nettobetrag', 'Summe netto', 'Positionen netto', 'Zwischensumme', "
            "'Gesamtbetrag netto', 'Summe (netto)', 'Subtotal'. "
            "\n"
            "German labels for GROSS total (NEVER USE THESE): "
            "'Gesamtsumme', 'Endsumme', 'Bruttobetrag', 'Summe brutto', 'Gesamtbetrag brutto', "
            "'Rechnungsbetrag', 'Total inkl. MwSt.'. "
            "\n"
            "CRITICAL: If you see both 'Nettosumme' and 'Gesamtsumme' on the same document, "
            "ALWAYS use the Nettosumme. The Gesamtsumme includes tax and must be ignored. "
            "\n"
            "The total_cost should equal the sum of all order line net prices PLUS any separately "
            "listed shipping costs (Versandkosten netto), but EXCLUDING all tax/VAT amounts. "
            "\n"
            "Do NOT calculate this by summing line items — read the stated NET value from the document. "
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

3. NET vs. GROSS TOTAL (CRITICAL):
   - The total_cost field MUST ALWAYS be the NET total (before tax/VAT), NEVER the gross total.
   - German labels for NET total (USE THESE):
     * 'Nettosumme', 'Nettobetrag', 'Summe netto', 'Positionen netto', 'Zwischensumme'
     * 'Gesamtbetrag netto', 'Summe (netto)', 'Subtotal'
   - German labels for GROSS total (NEVER USE THESE — they include tax):
     * 'Gesamtsumme', 'Endsumme', 'Bruttobetrag', 'Summe brutto'
     * 'Gesamtbetrag brutto', 'Rechnungsbetrag', 'Total inkl. MwSt.'
   - If you see BOTH 'Nettosumme' and 'Gesamtsumme' on the same document, ALWAYS use the Nettosumme.
   - NEVER use the Gesamtsumme, Endsumme, or Bruttobetrag — these include tax.
   - Read the net total exactly as stated on the document.
   - Do NOT compute by summing line items. The document's stated NET total takes precedence.

4. SHIPPING COSTS AS SEPARATE LINE ITEMS (CRITICAL):
   - If the document lists shipping or transport costs as a separate line or position, these MUST be extracted as their own order line item.
   - Common German shipping cost labels: 'Versandkosten', 'Versand', 'Transport', 'Lieferkosten', 'Frachtkosten', 'Speditionskosten', 'Verpackung und Versand', 'Porto'.
   - Use the shipping label as the product name (e.g., 'Versandkosten', 'Transport, Verpackung und Versand').
   - Extract the NET shipping cost (e.g., 'Versandkosten netto: €113.85'), NOT the gross amount with tax.
   - The total_cost should equal: sum of all order line net prices + net shipping costs, EXCLUDING all tax/VAT.

5. PRODUCT NAMES (CRITICAL — must not be empty):
   - Each line item in a German quote has TWO parts: a SHORT product name/title, and a longer description.
   - The PRODUCT NAME is the first prominent line or heading of the line item — typically bold text,
     or the first line in the 'Bezeichnung'/'Produkt' column before specs begin.
   - The product name is typically 3-10 words long. It is NOT the full specification text.
   - NEVER return an empty product name, '-', or null for the product field.
   - Real examples of correct product names:
     * '13" MacBook Air: Apple M2 Chip – Space Grau' (NOT the full configuration bullet list)
     * 'Moosbild "70:30" mit Schriftzug "askLio"' (NOT the paragraph about Waldmoos etc.)
     * 'Moosbild Mix-Moos 160x80 cm' (NOT 'Moosart: Mix-Moos, Außenabmessungen...')
     * 'Logointegration "asklio" horizontal' (NOT 'Gesamtgröße 105 cm Breite...')
     * 'Versandkosten' (when shipping is a separate line)
   - The DESCRIPTION field gets everything AFTER the product name (specs, dimensions, materials, etc.).
   - If you cannot clearly distinguish a product name from the description, use the first meaningful
     phrase (first line or first ~5-8 words) as the product name.

6. MONETARY VALUES:
   - Return all monetary values as plain decimals without currency symbols (e.g., 1767.26 not €1.767,26).

7. NULL VALUES:
   - If a field is genuinely not present in the document, use null.

8. TITLE:
   - Always generate a concise, descriptive procurement request title.
   - If unsure, use a generic title like 'Procurement Request'.

EXAMPLE:
Given a document from 'Gärtner Gregg' addressed to customer 'Lio Technologies GmbH' with USt-IdNr. DE198570491 in the vendor's details section, showing:
- Positionen netto: €1,186.14
- Versandkosten netto: €113.85
- Nettosumme: €1,299.99
- Umsatzsteuer 19%: €247.00
- Gesamtsumme: €1,546.99

Extraction should be:
- title: 'Procurement Order from Gärtner Gregg'
- vendor_name: 'Gärtner Gregg' (NOT 'Lio Technologies GmbH')
- vendor_vat_id: 'DE198570491'
- order_lines: [...product lines..., {product: 'Versandkosten', total_price: 113.85, ...}]
- total_cost: 1299.99 (the Nettosumme, NOT the Gesamtsumme of 1546.99)"""


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
    
    # Truncate very long texts to avoid exceeding context window
    MAX_CHARS = 15000  # ~4000 tokens, plenty for any offer
    if len(text) > MAX_CHARS:
        logger.warning(f"Offer text too long ({len(text)} chars), truncating to {MAX_CHARS}")
        text = text[:MAX_CHARS]
    
    logger.info(f"Sending {len(text)} chars to OpenAI for extraction")
    
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

    refusal = message.refusal or "Model did not return a parsed extraction."
    logger.error(f"OpenAI refused/failed extraction: {refusal}")
    raise RuntimeError(refusal)