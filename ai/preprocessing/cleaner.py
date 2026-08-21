"""
preprocessing/cleaner.py

WHAT THIS DOES:
Cleans raw incoming text reports (from social media / news) before
they are sent to the AI model. Removes noise like URLs, extra
whitespace, mentions, hashtags symbols (keeps the word), etc.

WHY:
Social media text is messy. Cleaning it makes the model's job
easier and more consistent.
"""

import re


def clean_text(raw_text: str) -> str:
    """
    Clean a single raw report string.

    Steps:
    1. Strip leading/trailing whitespace
    2. Remove URLs
    3. Remove @mentions
    4. Convert '#hashtag' -> 'hashtag' (keep the word, drop the symbol)
    5. Collapse multiple spaces/newlines into one space
    6. Remove non-printable / weird characters

    Args:
        raw_text: the raw report text

    Returns:
        cleaned text (string). Returns "" if input is empty/None.
    """
    if not raw_text:
        return ""

    text = raw_text.strip()

    # Remove URLs (http, https, www)
    text = re.sub(r"http\S+|www\.\S+", " ", text)

    # Remove @mentions
    text = re.sub(r"@\w+", " ", text)

    # Convert hashtags to plain words
    text = re.sub(r"#(\w+)", r"\1", text)

    # Remove non-printable characters
    text = re.sub(r"[^\x20-\x7E]", " ", text)

    # Collapse whitespace
    text = re.sub(r"\s+", " ", text).strip()

    return text


def clean_batch(raw_texts: list) -> list:
    """
    Clean a list of raw report strings.

    Args:
        raw_texts: list of raw text strings

    Returns:
        list of cleaned strings (same order, same length)
    """
    return [clean_text(t) for t in raw_texts]


if __name__ == "__main__":
    # Quick manual test when running this file directly:
    # COMMAND PROMPT:  python preprocessing/cleaner.py
    sample = "  Heavy flooding reported near Vijayawada!! Check http://news.com/xyz #flood @newsdesk  "
    print("BEFORE:", repr(sample))
    print("AFTER :", repr(clean_text(sample)))
