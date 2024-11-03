import numpy as np
import faiss
from transformers import pipeline
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from content_assistant.core.generator import embed_text
from content_assistant.core.models import TextEntry
import logging
import random
import base64
from content_assistant.core.db.database import get_db

logger = logging.getLogger("content_assistant_app")

# FAISS index initialization for vector similarity search
INDEX_DIMENSION = 384
index = faiss.IndexFlatIP(INDEX_DIMENSION)

generator = pipeline("text2text-generation", model="google/flan-t5-base", device=-1)


async def fetch_similar_texts_from_db(db: AsyncSession, domain: str, audience: str, tone: str):
    """
    Fetch similar texts from the database based on the given domain, audience, and tone.

    Args:
        db (AsyncSession): The database session for async operations.
        domain (str): The domain of the text (e.g., e-commerce, advertising).
        audience (str): The target audience for the text (e.g., consumer, business).
        tone (str): The tone of the text (e.g., informal, formal).

    Returns:
        list: A list of TextEntry objects matching the criteria.

    Raises:
        RuntimeError: If the database query fails.
    """
    try:
        result = await db.execute(
            select(TextEntry).where(
                TextEntry.domain == domain, TextEntry.audience == audience, TextEntry.tone == tone
            )
        )
        return result.scalars().all()
    except Exception as e:
        logger.error(f"Database query error: {str(e)}")
        raise RuntimeError("Database query failed.") from e


def search_similar_texts_in_faiss(query_embedding, db_texts):
    """
    Search for similar texts in the FAISS index using the given query embedding.

    Args:
        query_embedding (np.ndarray): The embedding of the query keywords.
        db_texts (list): A list of TextEntry objects from the database.

    Returns:
        str or None: The content of the most similar text if found, otherwise None.

    Raises:
        RuntimeError: If an error occurs during FAISS index operations.
    """
    if db_texts:
        try:
            db_embeddings = np.array([embed_text(text.content) for text in db_texts]).astype(
                "float32"
            )
            if db_embeddings.size > 0:
                index.reset()
                index.add(db_embeddings)
                logger.debug(f"Added {db_embeddings.shape[0]} embeddings to the FAISS index.")

                logger.info("Performing similarity search...")
                search_results = index.search(np.array([query_embedding]), k=1)

                if len(search_results) == 2:
                    distances, closest_indices = search_results
                    if closest_indices.size > 0 and distances[0][0] > 0.8:
                        return db_texts[closest_indices[0][0]].content
                    else:
                        logger.debug("No close enough match found, generating new text.")
                else:
                    logger.error("Unexpected format from FAISS search result.")
        except Exception as e:
            logger.error(f"Error during FAISS index operations: {str(e)}")
            raise RuntimeError("FAISS index operation failed.") from e
    else:
        logger.info("No relevant entries found in the database.")
    return None


def prepare_prompt(keywords, domain, word_count, audience, tone, retrieved_text=None):
    """
    Prepare the prompt for the text generation model.

    Args:
        keywords (list): A list of keywords to include in the generated text.
        domain (str): The domain of the text.
        word_count (int): The expected number of words in the generated text.
        audience (str): The target audience for the generated text.
        tone (str): The tone of the generated text.
        retrieved_text (str, optional): The retrieved text to improve upon, if any.

    Returns:
        str: The prepared prompt for text generation.
    """
    if retrieved_text:
        improvement_instruction = random.choice(
            [
                "improve it or make it more unique",
                "Rewrite the following to make it more compelling for the target audience",
                "Paraphrase and expand the text while keeping the tone consistent",
            ]
        )
        prompt = (
            f"{improvement_instruction}. "
            f'Current text: "{retrieved_text}". '
            f"Make sure the tone remains {tone} and suitable for a {audience}. "
            f"Keywords to include: {', '.join(keywords)}. It should be around {word_count} words long."
        )
    else:
        prompt = (
            f"As a professional, write a text in a {tone} tone. "
            f"Target audience: {audience}. Domain: {domain}. Keywords: {', '.join(keywords)}. "
            f"It should be exactly {word_count} words long."
        )
    return prompt


async def generate_text(
    keywords: list[str], domain: str, word_count: int, audience: str, tone: str
) -> str:
    """
    Generate or improve text based on keywords, domain, audience, and tone.

    Args:
        keywords (list[str]): A list of keywords to include in the generated text.
        domain (str): The domain of the text (e.g., e-commerce, advertising).
        word_count (int): The expected number of words in the generated text.
        audience (str): The target audience for the generated text (e.g., consumer, business).
        tone (str): The tone of the generated text (e.g., informal, formal).

    Returns:
        str: The generated text encoded in UTF-16 and Base64.

    Raises:
        ValueError: If the keywords are empty or embedding fails.
        RuntimeError: If database queries or text generation fails.
    """

    # Validate input keywords
    keyword_string = " ".join(keywords).strip()
    if not keyword_string:
        raise ValueError("Keywords cannot be empty.")

    # Embed the keywords into a single vector for query
    try:
        query_embedding = embed_text(keyword_string).astype("float32")
        if query_embedding.shape[0] != INDEX_DIMENSION:
            raise ValueError(
                f"Unexpected embedding dimension: {query_embedding.shape[0]}. Expected {INDEX_DIMENSION}."
            )
    except Exception as e:
        logger.error(f"Error embedding keywords: {str(e)}")
        raise ValueError("Failed to embed keywords.") from e

    # Fetch similar texts from the database
    async with get_db() as db:
        db_texts = await fetch_similar_texts_from_db(db, domain, audience, tone)

    attempt = 0
    max_retries = 5

    while attempt < max_retries:
        # Search for similar texts using FAISS
        retrieved_text = search_similar_texts_in_faiss(query_embedding, db_texts)

        # Prepare the prompt for text generation
        prompt = prepare_prompt(keywords, domain, word_count, audience, tone, retrieved_text)
        logger.info("Prepared prompt to generate is: %s" % prompt)

        # Generate a response with sampling settings to avoid repetitive outputs
        try:
            response = generator(
                prompt,
                max_new_tokens=int(word_count * 2),  # Adjust for expected word length
                temperature=0.7,  # Controls randomness. Higher values generate more random text
                top_p=0.9,  # Controls nucleus sampling. Adjust for more focused output
                do_sample=True,  # Enables sampling for more diverse outputs
            )
            generated_text = response[0]["generated_text"]
        except Exception as e:
            logger.error(f"Error during text generation: {str(e)}")
            raise RuntimeError("Text generation failed.") from e

        # Convert to UTF-16 before returning as Base64
        try:
            generated_text_utf16 = generated_text.encode("utf-16")
            base64_encoded_text = base64.b64encode(generated_text_utf16).decode("utf-8")
        except Exception as e:
            logger.error(f"Error encoding text to UTF-16 and Base64: {str(e)}")
            raise RuntimeError("Failed to encode text to UTF-16.") from e

        # Check if the generated text already exists in the database before saving
        if not any(text.content == generated_text for text in db_texts):
            async with get_db() as db:
                try:
                    new_text_entry = TextEntry(
                        content=generated_text, domain=domain, audience=audience, tone=tone
                    )
                    db.add(new_text_entry)
                    await db.commit()
                    logger.info(f"Generated text saved to database: {generated_text}")
                    break
                except Exception as e:
                    logger.error(f"Error saving generated text to the database: {str(e)}")
                    raise RuntimeError("Failed to save generated text.") from e
        else:
            logger.info(
                "Generated text already exists in the database. Retrying with adjusted prompt."
            )
            attempt += 1

    if attempt == max_retries:
        raise RuntimeError(f"Failed to generate a unique text after {max_retries} attempts.")

    return base64_encoded_text
