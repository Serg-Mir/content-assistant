from transformers import AutoTokenizer, AutoModel
import torch
import numpy as np

# Initialize tokenizer and model for embeddings
tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
model = AutoModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")


def embed_text(text: str) -> np.ndarray:
    """
    Embeds text using a transformer model.
    Args:
        text (str): Text to be embedded.
    Returns:
        np.ndarray: The text embedding.
    """
    # Tokenize the text
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True)

    # Generate embeddings with the model
    with torch.no_grad():
        model_output = model(**inputs)

    # Use mean pooling to get a single vector representation of the text
    # Take the average of the last hidden state across the sequence length axis
    embeddings = model_output.last_hidden_state.mean(dim=1)

    # Convert the embeddings to a NumPy array and return
    return embeddings.cpu().numpy().flatten()
