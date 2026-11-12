"""In this lab there is no AI model in the attack path: the 'agent' is the developer's web browser.
browser.py stands in for it (deterministic, offline). The chat on the left is the address bar."""
from . import browser


def model_label():
    return "simulated browser (browser.py)"


def chat(messages, tools):
    return browser.chat(messages, tools)
