from __future__ import annotations

from typing import Any, Callable

from .chunking import _dot
from .embeddings import _mock_embed
from .models import Document


class EmbeddingStore:
    """
    A vector store for text chunks.

    Tries to use ChromaDB if available; falls back to an in-memory store.
    The embedding_fn parameter allows injection of mock embeddings for tests.
    """

    def __init__(
        self,
        collection_name: str = "documents",
        embedding_fn: Callable[[str], list[float]] | None = None,
    ) -> None:
        self._embedding_fn = embedding_fn or _mock_embed
        self._collection_name = collection_name
        self._use_chroma = False
        self._store: list[dict[str, Any]] = []
        self._collection = None
        self._next_index = 0

        try:
            import chromadb  # noqa: F401
            self._use_chroma = True
            client = chromadb.Client()
            if hasattr(client, "get_or_create_collection"):
                self._collection = client.get_or_create_collection(name=collection_name)
            else:
                self._collection = client.create_collection(name=collection_name)
        except Exception:
            self._use_chroma = False
            self._collection = None

    def _make_record(self, doc: Document) -> dict[str, Any]:
        embedding = self._embedding_fn(doc.content)
        return {
            "id": doc.id,
            "content": doc.content,
            "metadata": dict(doc.metadata or {}),
            "embedding": embedding,
        }

    def _search_records(self, query: str, records: list[dict[str, Any]], top_k: int) -> list[dict[str, Any]]:
        query_embedding = self._embedding_fn(query)
        scored_records = []
        for record in records:
            score = _dot(query_embedding, record["embedding"])
            scored_records.append(
                {
                    "id": record["id"],
                    "content": record["content"],
                    "metadata": record["metadata"],
                    "score": score,
                }
            )

        scored_records.sort(key=lambda item: item["score"], reverse=True)
        return scored_records[:top_k]

    def add_documents(self, docs: list[Document]) -> None:
        if self._use_chroma and self._collection is not None:
            ids: list[str] = []
            documents: list[str] = []
            embeddings: list[list[float]] = []
            metadatas: list[dict[str, Any]] = []
            for doc in docs:
                ids.append(doc.id)
                documents.append(doc.content)
                embeddings.append(self._embedding_fn(doc.content))
                metadatas.append(dict(doc.metadata or {}))
                self._store.append(self._make_record(doc))
            try:
                self._collection.add(
                    ids=ids,
                    documents=documents,
                    embeddings=embeddings,
                    metadatas=metadatas,
                )
            except Exception:
                pass
        else:
            for doc in docs:
                self._store.append(self._make_record(doc))

    def search(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        if self._use_chroma and self._collection is not None:
            try:
                result = self._collection.query(
                    query_embeddings=[self._embedding_fn(query)],
                    n_results=top_k,
                )
                ids = result.get("ids", [[]])[0]
                documents = result.get("documents", [[]])[0]
                metadatas = result.get("metadatas", [[]])[0]
                distances = result.get("distances", [[]])[0]
                output: list[dict[str, Any]] = []
                for idx, doc_id in enumerate(ids):
                    score = 1.0 - distances[idx] if distances and len(distances) > idx else 0.0
                    output.append(
                        {
                            "id": doc_id,
                            "content": documents[idx],
                            "metadata": metadatas[idx] if metadatas and len(metadatas) > idx else {},
                            "score": score,
                        }
                    )
                return output
            except Exception:
                pass

        return self._search_records(query, self._store, top_k)

    def get_collection_size(self) -> int:
        return len(self._store)

    def search_with_filter(self, query: str, top_k: int = 3, metadata_filter: dict = None) -> list[dict]:
        if not metadata_filter:
            return self.search(query, top_k=top_k)

        filtered_records = [
            record for record in self._store
            if all(record["metadata"].get(key) == value for key, value in metadata_filter.items())
        ]
        return self._search_records(query, filtered_records, top_k)

    def delete_document(self, doc_id: str) -> bool:
        original_count = len(self._store)
        self._store = [record for record in self._store if record["id"] != doc_id]
        deleted = len(self._store) < original_count
        if deleted and self._use_chroma and self._collection is not None:
            try:
                self._collection.delete(ids=[doc_id])
            except Exception:
                pass
        return deleted
