from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field
import os

load_dotenv()

# Only initialize OpenAI client if API key is available
client = None
if os.getenv("OPENAI_API_KEY"):
    client = OpenAI()


class CommodityPrediction(BaseModel):
    commodity_group_id: str = Field(pattern=r"^\d{3}$")


def predict_commodity_group_id(
    *,
    title: str,
    department: str,
    vendor_name: str,
    order_lines_text: str,
    commodity_groups_text: str,
) -> str:
    if not client:
        raise RuntimeError("OpenAI API key is not configured. Please set OPENAI_API_KEY environment variable.")
    
    completion = client.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a procurement commodity classifier.\n"
                    "Pick exactly ONE commodity_group_id from the list provided by the user.\n"
                    "Return only the JSON that matches the schema."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Commodity groups (ID | Category | Name):\n{commodity_groups_text}\n\n"
                    f"Request title: {title}\n"
                    f"Department: {department}\n"
                    f"Vendor: {vendor_name}\n"
                    f"Order lines: {order_lines_text}\n"
                ),
            },
        ],
        response_format=CommodityPrediction,
    )

    msg = completion.choices[0].message
    if msg.parsed:
        return msg.parsed.commodity_group_id

    raise RuntimeError(msg.refusal or "No parsed commodity prediction returned")
