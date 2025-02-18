from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

def calculate_paragraph_similarity(paragraph1, paragraph2):
    """
    Calculates the cosine similarity between two paragraphs using Sentence Transformers.

    Args:
        paragraph1: The first paragraph (a string).
        paragraph2: The second paragraph (a string).

    Returns:
        The cosine similarity score (a float between 0 and 1).
    """

    # Load a pre-trained Sentence Transformer model.  "all-MiniLM-L6-v2".
    # Other models available: https://www.sbert.net/docs/pretrained_models.html
    model = SentenceTransformer("all-MiniLM-L6-v2")

    # Encode the paragraphs into vectors.
    embedding1 = model.encode(paragraph1)
    embedding2 = model.encode(paragraph2)

    # Reshape the embeddings to be 2D arrays for cosine_similarity
    embedding1 = embedding1.reshape(1, -1)
    embedding2 = embedding2.reshape(1, -1)

    # Calculate the cosine similarity.
    similarity = cosine_similarity(embedding1, embedding2)[0][0]

    return similarity
