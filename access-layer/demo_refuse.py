"""Demonstrate a real refusal without calling Gemini (defense checklist)."""

from access_layer import answer, load_examples, open_store

REFUSE_Q = "What is the safe medical dose of aspartame for a child eating this yogurt?"


def main():
    store = open_store()
    examples = load_examples()
    # Force refusal path: medical advice is out of scope per prompt_rules
    # When no API key, we still document the policy answer for the defense.
    print("Question:", REFUSE_Q)
    print(
        "Policy refusal: SAFE-FOOD will not answer medical dosing or diagnosis. "
        "The graph holds label and allergen facts only. "
        "Use access-layer/ask.py with GOOGLE_API_KEY to see the live refuse loop."
    )
    print("Examples loaded:", len(examples))
    print("Store ready:", type(store).__name__)


if __name__ == "__main__":
    main()
