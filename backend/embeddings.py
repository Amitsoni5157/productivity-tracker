# Ye file sirf text ko vector (numbers) me convert karne ka kaam karegi.
from langchain_huggingface import HuggingFaceEmbeddings


# Initialize local embedding model (free, downloads once and runs offline)
# Ye model 384 dimensions ka vector generate karta hai, jo humare database setup se bilkul match karta hai

embeddings_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

def get_embedding(text: str) -> list[float]:
    """Converts input text into a 384-dimensional vector embedding."""
    if not text:
        return [0.0]*384  # Return empty vector if text is empty
    return embeddings_model.embed_query(text)  # Vector convert