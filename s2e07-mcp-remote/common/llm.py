"""In this lab no AI model makes a decision in the attack path: the steps are the bridge's own
login flow. bridge.py stands in for it (deterministic, offline). The chat on the left is the AI app."""
from . import bridge


def model_label():
    return "lab bridge flow (bridge.py)"


def chat(messages, tools):
    return bridge.chat(messages, tools)
