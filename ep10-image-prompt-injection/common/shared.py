"""Shared pieces: the claims queue, the OCR step and the side panels."""
import os

import pytesseract
from PIL import Image

from .server import calls_panel

HERE = os.path.dirname(os.path.abspath(__file__))
RECEIPTS = os.path.join(HERE, "..", "web", "receipts")
CLAIMS = {"Anita": ("anita-lunch-receipt.png", "Client lunch"), "Ravi": ("ravi-cab-receipt.png", "Cab to office")}
AUTO_APPROVE_LIMIT = 5000      # company policy: claims up to Rs 5,000 can be approved without a manager

TOOLS = [
    {"name": "read_receipt", "description": "Read the text on a claim's receipt image.",
     "parameters": {"type": "object", "properties": {"employee": {"type": "string"}}, "required": ["employee"]}},
    {"name": "submit_expense", "description": "File the claim. status is 'approved' (paid out) or 'pending'.",
     "parameters": {"type": "object", "properties": {"employee": {"type": "string"}, "amount": {"type": "integer"},
                                                     "status": {"type": "string"}},
                    "required": ["employee", "amount", "status"]}},
]


def ocr(employee):
    """Read the image the way receipt pipelines do: boost contrast, then OCR every line of text."""
    im = Image.open(os.path.join(RECEIPTS, CLAIMS[employee][0])).convert("L").point(lambda v: 0 if v < 245 else 255)
    return pytesseract.image_to_string(im, config="--psm 6").strip()


def new_state():
    return {"claims": {}, "read": []}


def panels(state):
    rows = [[f"{e} · {CLAIMS[e][1]}", state["claims"].get(e, ("not filed", ""))[0],
             state["claims"].get(e, ("", ""))[1]] for e in CLAIMS]
    return [{"id": "claims", "title": "Expense claims (what the app recorded)", "kind": "table", "rows": rows, "fit": True},
            {"id": "ocr", "title": "Text the AI read from the receipt image", "kind": "items", "empty": "Nothing read yet.",
             "items": [{"head": f"{e}'s receipt", "body": t, "status": st} for e, t, st in state["read"]]},
            calls_panel(state, risky=("submit_expense",))]
