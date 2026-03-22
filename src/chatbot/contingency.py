# contingency_rag.py

import os
import chromadb
from docx import Document
from docx.oxml.ns import qn

def get_blocks_in_order(doc):
    """Returns paragraphs and table rows in document reading order."""
    blocks = []
    for block in doc.element.body:
        if block.tag == qn("w:p"):
            text = "".join(node.text or "" for node in block.iter() if node.tag == qn("w:t")).strip()
            style = block.style if block.style is not None else ""
            if text:
                blocks.append({"type": "paragraph", "text": text, "style": style})

        elif block.tag == qn("w:tbl"):
            for row in block.findall(".//" + qn("w:tr")):
                cells = row.findall(".//" + qn("w:tc"))
                row_text = " | ".join(
                    "".join(node.text or "" for node in cell.iter() if node.tag == qn("w:t"))
                    for cell in cells
                ).strip()
                if row_text:
                    blocks.append({"type": "table_row", "text": row_text, "style": ""})
    return blocks


def ingest_documents(docs_folder="src/data/contingency_plans"):
    client = chromadb.PersistentClient(path="./chroma_db")
    client.delete_collection("railway_contingency")
    collection = client.create_collection("railway_contingency")

    for filename in os.listdir(docs_folder):
        if filename.endswith(".docx"):
            station_name = filename.replace(".docx", "")
            doc = Document(f"{docs_folder}/{filename}")
            blocks = get_blocks_in_order(doc)

            # Split into chunks at every heading
            chunks = []
            current_heading = "General"
            current_text = []

            for block in blocks:
                is_heading = "Heading" in block["style"] or block["text"].isupper()
                if is_heading and current_text:
                    chunks.append({
                        "heading": current_heading,
                        "text": " ".join(current_text)
                    })
                    current_heading = block["text"]
                    current_text = []
                else:
                    current_text.append(block["text"])

            # Don't forget the last section
            if current_text:
                chunks.append({
                    "heading": current_heading,
                    "text": " ".join(current_text)
                })

            for i, chunk in enumerate(chunks):
                collection.add(
                    documents=[f"{chunk['heading']}: {chunk['text']}"],
                    ids=[f"{filename}_chunk_{i}"],
                    metadatas=[{
                        "source": filename,
                        "station": station_name,
                        "section": chunk["heading"],
                        "chunk": i
                    }]
                )
            print(f"Ingested: {filename} ({len(chunks)} chunks)")

def search_contingency(query: str, station: str = None, n_results=1):
    client = chromadb.PersistentClient(path="./chroma_db")
    collection = client.get_collection("railway_contingency")
    where = {"station": station} if station else None

    results = collection.query(
        query_texts=[query],
        n_results=n_results,
        where=where
    )
    chunks = results["documents"][0]
    sources = [m["source"] for m in results["metadatas"][0]]
    return chunks, sources


if __name__ == "__main__":
    # ingest_documents()
    while True:
        query = input("Enter your contingency query (or 'quit' to exit): ").strip()
        if query.lower() == 'quit':
            break
        
        chunks, sources = search_contingency(query,"Poole",1)
        for i, (chunk, source) in enumerate(zip(chunks, sources)):
            print(f"--- Result {i+1} from {source} ---")
            print(chunk)
            print()