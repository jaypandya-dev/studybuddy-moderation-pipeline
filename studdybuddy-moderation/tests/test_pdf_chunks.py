from app.pdf_extractor import extract_text


pdf_path = "group_6.pdf"

with open(pdf_path, "rb") as f:
    file_bytes = f.read()

result = extract_text(file_bytes)

print("Pages:", result["page_count"])
print("Total characters:", result["character_count"])
print("Total chunks:", len(result["chunks"]))

print("\n--- Chunks ---")

for chunk in result["chunks"]:
    print(
        f"Page: {chunk['page']} | "
        f"Chunk: {chunk['chunk']} | "
        f"Source: {chunk['source']} | "
        f"Words: {len(chunk['text'].split())}"
    )