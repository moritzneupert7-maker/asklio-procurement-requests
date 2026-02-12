from pydantic import BaseModel
from openai import OpenAI

client = OpenAI()


class CommodityPrediction(BaseModel):
    commodity_group_id: str  # must be one of the IDs you provide in the prompt


def predict_commodity_group_id(title: str, department: str, vendor_name: str, lines_text: str, groups_text: str) -> str:
    completion = client.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a procurement commodity classifier. "
                    "Choose exactly one commodity group ID from the provided list."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Commodity groups (ID | Category | Name):\n{groups_text}\n\n"
                    f"Request title: {title}\n"
                    f"Department: {department}\n"
                    f"Vendor: {vendor_name}\n"
                    f"Order lines: {lines_text}\n"
                ),
            },
        ],
        response_format=CommodityPrediction,
    )

    msg = completion.choices[0].message
    if msg.parsed:
        return msg.parsed.commodity_group_id

    raise RuntimeError(msg.refusal or "Model did not return a parsed commodity group.")
