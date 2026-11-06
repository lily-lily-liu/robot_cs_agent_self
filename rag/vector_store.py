"""Build and query the project's persistent Chroma vector store."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    # ``python rag/vector_store.py`` is the documented invocation.
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from model.factory import get_embedding_model
from utils.config_handler import load_yaml
from utils.file_handler import calculate_md5, iter_documents, read_file
from utils.path_tool import project_path


CONFIG_PATH = project_path("config", "chroma.yml")
DATA_PATH = project_path("data")


def _load_config(config_path: str | Path = CONFIG_PATH) -> dict[str, Any]:
    """Load and validate the Chroma configuration."""
    config = load_yaml(config_path)
    required = ("collection_name", "persist_directory", "k", "chunk_size", "chunk_overlap")
    missing = [key for key in required if key not in config]
    if missing:
        raise ValueError(f"Missing Chroma configuration keys: {', '.join(missing)}")

    for key in ("k", "chunk_size", "chunk_overlap"):
        if not isinstance(config[key], int) or isinstance(config[key], bool) or config[key] < 1:
            raise ValueError(f"'{key}' must be a positive integer")
    if config["chunk_overlap"] >= config["chunk_size"]:
        raise ValueError("'chunk_overlap' must be smaller than 'chunk_size'")
    if not isinstance(config["collection_name"], str) or not config["collection_name"].strip():
        raise ValueError("'collection_name' must be a non-empty string")
    if not isinstance(config["persist_directory"], (str, Path)):
        raise ValueError("'persist_directory' must be a path")
    separators = config.get("separators", ["\n\n", "\n", ".", "。"])
    if not isinstance(separators, list) or not all(isinstance(item, str) for item in separators):
        raise ValueError("'separators' must be a list of strings")
    config["separators"] = separators
    return config


def _get_text_splitter(config: dict[str, Any]) -> Any:
    """Create the configured recursive text splitter."""
    try:
        from langchain_text_splitters import RecursiveCharacterTextSplitter
    except ImportError:
        try:
            from langchain.text_splitter import RecursiveCharacterTextSplitter
        except ImportError as exc:
            raise ImportError(
                "langchain-text-splitters is required to split documents"
            ) from exc
    return RecursiveCharacterTextSplitter(
        chunk_size=config["chunk_size"],
        chunk_overlap=config["chunk_overlap"],
        separators=config["separators"],
    )


def _get_chroma(config: dict[str, Any], embedding_model: Any) -> Any:
    """Create a persistent Chroma vector store using the installed integration."""
    persist_directory = Path(config["persist_directory"])
    if not persist_directory.is_absolute():
        persist_directory = project_path(persist_directory)
    persist_directory.mkdir(parents=True, exist_ok=True)

    try:
        from langchain_chroma import Chroma
    except ImportError:
        try:
            from langchain_community.vectorstores import Chroma
        except ImportError as exc:
            raise ImportError(
                "langchain-chroma or langchain-community is required for Chroma"
            ) from exc
    return Chroma(
        collection_name=config["collection_name"],
        embedding_function=embedding_model,
        persist_directory=str(persist_directory),
    )


def _stored_fingerprints(vector_store: Any) -> set[str]:
    """Return fingerprints already present in the collection."""
    result = vector_store.get(include=["metadatas"])
    metadatas = result.get("metadatas") or []
    return {
        metadata["fingerprint"]
        for metadata in metadatas
        if isinstance(metadata, dict) and isinstance(metadata.get("fingerprint"), str)
    }


def _documents_for_file(file_path: Path, fingerprint: str, splitter: Any) -> list[Any]:
    """Read and split one source file, attaching stable source metadata."""
    from langchain_core.documents import Document

    text = read_file(file_path)
    if not text.strip():
        return []
    chunks = splitter.split_text(text)
    relative_path = str(file_path.relative_to(project_path())).replace("\\", "/")
    return [
        Document(
            page_content=chunk,
            metadata={
                "source": relative_path,
                "fingerprint": fingerprint,
                "chunk": index,
            },
        )
        for index, chunk in enumerate(chunks)
        if chunk.strip()
    ]


def build_vector_store(
    data_directory: str | Path = DATA_PATH,
    config_path: str | Path = CONFIG_PATH,
) -> Any:
    """Scan, deduplicate, split, embed, and persist TXT/PDF documents."""
    config = _load_config(config_path)
    splitter = _get_text_splitter(config)
    vector_store = _get_chroma(config, get_embedding_model())
    stored_fingerprints = _stored_fingerprints(vector_store)
    documents: list[Any] = []
    skipped = 0

    for file_path in iter_documents(data_directory):
        fingerprint = calculate_md5(file_path)
        if fingerprint in stored_fingerprints:
            skipped += 1
            continue
        documents.extend(_documents_for_file(file_path, fingerprint, splitter))
        # Prevent identical files in this scan from being embedded twice.
        stored_fingerprints.add(fingerprint)

    if documents:
        ids = [
            f"{document.metadata['fingerprint']}-{document.metadata['chunk']}"
            for document in documents
        ]
        vector_store.add_documents(documents=documents, ids=ids)

    print(f"Added {len(documents)} chunks; skipped {skipped} already-indexed files.")
    return vector_store


def get_vector_store(config_path: str | Path = CONFIG_PATH) -> Any:
    """Open the configured persistent Chroma collection without indexing files."""
    config = _load_config(config_path)
    return _get_chroma(config, get_embedding_model())


def search(query: str, config_path: str | Path = CONFIG_PATH) -> list[Any]:
    """Return the configured number of most relevant documents for ``query``."""
    if not isinstance(query, str) or not query.strip():
        raise ValueError("query must be a non-empty string")
    config = _load_config(config_path)
    return get_vector_store(config_path).similarity_search(query, k=config["k"])


if __name__ == "__main__":
    build_vector_store()
