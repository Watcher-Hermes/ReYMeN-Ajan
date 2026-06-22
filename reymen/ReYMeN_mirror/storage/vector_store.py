"""
vector_store.py — Vektor veritabani (ChromaDB).

Semantik arama icin raporlari vektor DB'de indexler.
"""

import chromadb
from chromadb.utils import embedding_functions
from loguru import logger

# Yerel Chroma DB (dosyaya yazar)
client = chromadb.PersistentClient(path="./chroma_db")

# Embedding — ucretsiz, yerel model
ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

collection = client.get_or_create_collection(
    name="reymen_reports",
    embedding_function=ef,
    metadata={"hnsw:space": "cosine"},
)


def store_report(report_id: int, query: str, summary: str, sources: list) -> None:
    """Raporu vektor DB'ye ekle (semantik arama icin)."""
    try:
        collection.upsert(
            ids=[str(report_id)],
            documents=[summary],
            metadatas=[{
                "query": query,
                "sources": ", ".join(sources[:5]),
                "report_id": report_id,
            }],
        )
        logger.info(f"Vektor kaydedildi: ID:{report_id}")
    except Exception as e:
        logger.error(f"Vektor hata: {e}")


def semantic_search(query: str, top_k: int = 5) -> list[dict]:
    """Anlamsal benzerlik ile rapor ara."""
    results = collection.query(
        query_texts=[query],
        n_results=top_k,
    )

    hits = []
    for i, doc in enumerate(results["documents"][0]):
        hits.append({
            "summary": doc,
            "metadata": results["metadatas"][0][i],
            "score": round(1 - results["distances"][0][i], 3),
        })

    return hits
