from pypdf import PdfReader

from backend.config import (
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    COLLECTION_NAME,
    PDF_PATH,
    SPECIES_ALIASES,
    SPECIES_TO_CATEGORY,
)
from backend.vector_store import get_client, get_collection


def clean_text(text):
    return "\n".join(line.strip() for line in text.splitlines() if line.strip())


def detect_species(text):
    lower = text.lower()
    species = []
    seen = set()
    for alias, canonical in sorted(SPECIES_ALIASES.items(), key=lambda item: len(item[0]), reverse=True):
        if alias in lower and canonical not in seen:
            species.append(canonical)
            seen.add(canonical)
    return species


def detect_section(text):
    lower = text.lower()
    sections = []
    if "keys to id" in lower or "keys to identification" in lower:
        sections.append("Keys to ID")
    if "identification" in lower:
        sections.append("Identification")
    if "lifecycle" in lower or "life cycle" in lower:
        sections.append("Life Cycle")
    if "control" in lower or "herbicide" in lower:
        sections.append("Control Methods")
    return ", ".join(sections) if sections else "General"


def chunk_page(text, page_num):
    chunks = []
    start = 0
    while start < len(text):
        end = start + CHUNK_SIZE
        chunk_text = text[start:end]
        species = detect_species(chunk_text)
        categories = sorted({SPECIES_TO_CATEGORY.get(name.lower(), "general") for name in species})
        metadata = {
            "page": page_num,
            "section": detect_section(chunk_text),
        }
        if species:
            metadata["species"] = ", ".join(species)
        if categories:
            metadata["category"] = ", ".join(categories)
        chunks.append((f"page_{page_num}_chunk_{len(chunks)}", chunk_text, metadata))
        start += CHUNK_SIZE - CHUNK_OVERLAP
    return chunks


def reset_collection():
    client = get_client()
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass
    return get_collection()


def ingest():
    reader = PdfReader(PDF_PATH)
    all_chunks = []

    for page_num, page in enumerate(reader.pages, start=1):
        text = clean_text(page.extract_text() or "")
        if not text:
            continue
        all_chunks.extend(chunk_page(text, page_num))

    if not all_chunks:
        print("No text extracted from PDF.")
        return

    collection = reset_collection()
    collection.add(
        ids=[chunk_id for chunk_id, _, _ in all_chunks],
        documents=[document for _, document, _ in all_chunks],
        metadatas=[metadata for _, _, metadata in all_chunks],
    )

    species_found = sorted(
        {
            species.strip()
            for _, _, metadata in all_chunks
            for species in metadata.get("species", "").split(",")
            if species.strip()
        }
    )
    print(f"Ingested {len(all_chunks)} chunks from {len(reader.pages)} pages.")
    if species_found:
        print(f"Species detected: {', '.join(species_found)}")


if __name__ == "__main__":
    ingest()
