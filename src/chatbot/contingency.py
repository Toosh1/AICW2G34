# contingency_rag.py

import os
import chromadb
from docx import Document
from docx.oxml.ns import qn

def ingest_documents(docs_folder="src/data/contingency_plans"):
    client = chromadb.PersistentClient(path="./chroma_db")
    client.delete_collection("railway_contingency")
    collection = client.create_collection("railway_contingency")

    files_processed = 0
    chunk_count = 0
    
    for filename in os.listdir(docs_folder):
        if filename.endswith(".docx"):
            station_name = filename.replace(".docx", "").title()
            
            doc = Document(f"{docs_folder}/{filename}")
            paragraphs = []
            for block in doc.element.body:
                # Normal paragraph
                if block.tag == qn("w:p"):
                    text = block.text_content() if hasattr(block, "text_content") else "".join(
                        node.text or "" for node in block.iter() if node.tag == qn("w:t")
                    )
                    if text.strip():
                        paragraphs.append(text.strip())

                # Table
                elif block.tag == qn("w:tbl"):
                    for row in block.findall(".//" + qn("w:tr")):
                        cells = row.findall(".//" + qn("w:tc"))
                        row_text = " | ".join(
                            "".join(node.text or "" for node in cell.iter() if node.tag == qn("w:t"))
                            for cell in cells
                        ).strip()
                        if row_text:
                            paragraphs.append(row_text)

            chunk_size = 10
            chunks = [
                " ".join(paragraphs[i:i+chunk_size])
                for i in range(0, len(paragraphs), chunk_size)
            ]

            for i, chunk in enumerate(chunks):
                collection.add(
                    documents=[chunk],
                    ids=[f"{filename}_chunk_{i}"],
                    metadatas=[{
                        "source": filename,
                        "station": station_name,
                        "chunk": i
                    }]
                )
            
            files_processed += 1
            chunk_count += len(chunks)
            print(f"Processing: {filename} ({len(chunks)} chunks)")

    print(f"Ingestion complete. Files processed: {files_processed}, Total chunks: {chunk_count}")

def search_contingency(query: str, station: str = None, n_results=3):
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
        
        chunks, sources = search_contingency(query,"Poole",3)
        for i, (chunk, source) in enumerate(zip(chunks, sources)):
            print(f"--- Result {i+1} from {source} ---")
            print(chunk)
            print()