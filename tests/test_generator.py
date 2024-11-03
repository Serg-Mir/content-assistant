import numpy as np
from unittest.mock import patch
from content_assistant.core.content_generator import search_similar_texts_in_faiss, prepare_prompt
from content_assistant.core.models import TextEntry

INDEX_DIMENSION = 384


def test_search_similar_texts_in_faiss():
    db_texts = [TextEntry(content="Existing sample text", domain="e-commerce", audience="consumer", tone="playful")]
    query_embedding = np.array([0.1] * INDEX_DIMENSION, dtype="float32")

    with patch("content_assistant.core.content_generator.embed_text", return_value=np.array([0.1] * INDEX_DIMENSION, dtype="float32")):
        result = search_similar_texts_in_faiss(query_embedding, db_texts)
        assert result == "Existing sample text"


def test_prepare_prompt():
    keywords = ["bread", "milk"]
    domain = "e-commerce"
    word_count = 100
    audience = "consumer"
    tone = "playful"
    prompt = prepare_prompt(keywords, domain, word_count, audience, tone)
    assert "Keywords: bread, milk" in prompt
    assert "Target audience: consumer" in prompt

    retrieved_text = "This is a sample retrieved text."
    prompt_with_retrieved = prepare_prompt(keywords, domain, word_count, audience, tone, retrieved_text)
    assert "Current text: \"This is a sample retrieved text.\"" in prompt_with_retrieved
    assert "Keywords to include: bread, milk" in prompt_with_retrieved
