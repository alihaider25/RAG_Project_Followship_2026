import chromadb
from sentence_transformers import SentenceTransformer

client = chromadb.PersistentClient(path="chroma_db")
collection = client.get_or_create_collection(name="documents")

model = SentenceTransformer("all-MiniLM-L6-v2")  # small, fast, free embedding model


def add_document_chunks(doc_id, chunks):
    embeddings = model.encode(chunks).tolist()
    ids = [f"{doc_id}_{i}" for i in range(len(chunks))]
    metadatas = [{"doc_id": doc_id, "chunk_index": i} for i in range(len(chunks))]

    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=chunks,
        metadatas=metadatas
    )


def delete_document_chunks(doc_id):
    collection.delete(where={"doc_id": doc_id})


def search_chunks(query, top_k=3, doc_ids=None):
    query_embedding = model.encode([query]).tolist()

    kwargs = {
        "query_embeddings": query_embedding,
        "n_results": top_k
    }

    if doc_ids:
        kwargs["where"] = {"doc_id": {"$in": doc_ids}}

    results = collection.query(**kwargs)
    return results