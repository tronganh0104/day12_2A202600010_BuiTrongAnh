"""
Mock LLM shared by the final project.
Keeps the final project self-contained for local runs and Docker builds.
"""
import random
import time


MOCK_RESPONSES = {
    "default": [
        "Day 12 final agent is running with a mock LLM response.",
        "The production-ready agent is healthy and answered your request.",
        "This is a mock answer that stands in for a real LLM response.",
    ],
    "docker": [
        "Docker packages the app and its dependencies so it can run consistently."
    ],
    "deploy": [
        "Deployment moves your application from development into a usable environment."
    ],
    "health": [
        "The service is healthy and ready to receive traffic."
    ],
}


def ask(question: str, delay: float = 0.1) -> str:
    time.sleep(delay + random.uniform(0, 0.05))
    question_lower = question.lower()
    for keyword, responses in MOCK_RESPONSES.items():
        if keyword in question_lower:
            return random.choice(responses)
    return random.choice(MOCK_RESPONSES["default"])


def ask_stream(question: str):
    response = ask(question)
    for word in response.split():
        time.sleep(0.05)
        yield word + " "
