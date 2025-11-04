import base64
import json
import os
import re
from typing import List

import fitz
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_community.vectorstores import Qdrant
from langchain_core.documents import Document
from langchain_ollama import OllamaEmbeddings, OllamaLLM
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.prompts import SYSTEM_PROMPT, diagram_prompt, page_prompt


def extract_pdf_text(pdf_path):
    loader = PyMuPDFLoader(pdf_path)
    docs = loader.load()
    print(f"\n🔹 Extracted {len(docs)} text segments from PDF.")
    return docs


def filter_to_minimal_docs(docs):
    """
    Given a list of Document objects, return a new list of Document objects
    containing only 'source' in metadata and the original page_content.
    """
    minimal_docs: List[Document] = []
    for doc in docs:
        src = doc.metadata.get("source")
        sub = doc.metadata.get("subject")
        page = doc.metadata.get("page")

        minimal_docs.append(
            Document(
                page_content=doc.page_content,
                metadata={"source": src, "subject": sub, "page": page},
            )
        )
    return minimal_docs


def extract_pdf_images(
    pdf_path, output_dir="images", min_width=40, min_height=40, min_pixels=1000, dpi=300
):
    """Extract images but skip tiny/mask/duplicate images.
    Adjust min_width/min_height/min_pixels to tune filtering.
    """
    print("\n🔹 Extracting images from PDF...\n")
    os.makedirs(output_dir, exist_ok=True)

    doc = fitz.open(pdf_path)
    tot_embedded_imgs = 0
    seen_xrefs = set()
    captions = {}

    for page_num in range(2):
        page = doc[page_num]
        image_list = page.get_images(
            full=True
        )  # tuples include (xref, smask, w, h, bpc, cs, ...)
        if not image_list:
            continue

        for img_idx, img in enumerate(image_list):
            xref = img[0]
            smask = img[1] if len(img) > 1 else 0

            # skip derived mask images or duplicates
            if smask:
                # print(f"Skipping mask image xref={xref} (smask={smask})")
                continue
            if xref in seen_xrefs:
                # same image reused on multiple pages; skip duplicates
                continue
            seen_xrefs.add(xref)

            try:
                base_image = doc.extract_image(xref)
            except Exception as e:
                print(f"Failed to extract xref={xref}: {e}")
                continue

            w = base_image.get("width", 0)
            h = base_image.get("height", 0)
            pixels = w * h

            # filter tiny images
            if w < min_width or h < min_height or pixels < min_pixels:
                # print(f"Skipping small image xref={xref} size={w}x{h} ({pixels} px)")
                continue

            image_bytes = base_image.get("image")
            image_ext = base_image.get("ext", "png")
            image_path = f"{output_dir}/page{page_num + 1}_xref{xref}.{image_ext}"
            with open(image_path, "wb") as f:
                f.write(image_bytes)

            print(f"Saved: {image_path}", end="  &  ")
            tot_embedded_imgs += 1
            caption = run_qwen_caption(image_path, short=True)
            captions[image_path] = caption
    # Method 2: Render each page as image (captures vector graphics)

    print("\n🔹📝 Rendering each page as image...\n")

    zoom = dpi / 72
    mat = fitz.Matrix(zoom, zoom)

    for page_num in range(2):
        page = doc[page_num]
        pix = page.get_pixmap(matrix=mat)
        image_path = f"{output_dir}/page{page_num + 1}_full.png"
        pix.save(image_path)
        print(f"  Saved: {image_path}", end="  &  ")

        caption = run_qwen_caption(image_path)
        captions[image_path] = caption

    # Save all captions for reuse
    with open("captions.json", "w", encoding="utf-8") as f:
        json.dump(captions, f, ensure_ascii=False, indent=2)

    print(
        f"\n♾️ Extracted {tot_embedded_imgs} images from {len(doc)} pages successfully. ✅"
    )
    print(f"♾️ Rendered {len(doc)} full pages")
    print(f"♾️ {len(captions)} Captions generated for  images and diagrams.")

    return captions


def run_qwen_caption(image_path, short=False, model="llava"):
    """Generate caption for image using an Ollama vision LLM with a system prompt."""
    if short:
        user_prompt = diagram_prompt
    else:
        user_prompt = page_prompt

    # Combine the system-level instruction with the user's request
    final_prompt = SYSTEM_PROMPT + user_prompt

    with open(image_path, "rb") as img_file:
        image_b64 = base64.b64encode(img_file.read()).decode("utf-8")

    llm = OllamaLLM(model=model)
    llm_with_image_context = llm.bind(images=[image_b64])

    # Invoke model with the combined prompt
    caption = llm_with_image_context.invoke(final_prompt)

    print(f"[Captioned] {image_path.split('/')[-1]} -> {caption[:80]}...")
    return caption


def chunk_documents(minimal_docs, captions):
    print("\n🔹 Creating text chunks and attaching image captions to nearest page...")

    # Step 1: Split all pages into smaller text chunks
    splitter = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=100)
    chunks = splitter.split_documents(minimal_docs)

    # Step 2: Group chunks by page number for quick lookup
    page_map = {}
    for doc in chunks:
        page = doc.metadata.get("page")
        if page is not None:
            page_map.setdefault(page + 1, []).append(doc)

    # Step 3: Attach each image caption to the last chunk from that page
    for path, caption in captions.items():
        match = re.search(r"page(\d+)", path)
        if not match:
            continue
        page_num = int(match.group(1))

        if page_num in page_map:
            target_chunk = page_map[page_num][-1]
            target_chunk.page_content += f"[Related Image Caption]: {caption}"

    print(f"🖼️ Created {len(chunks)} text chunks with attached image captions.")
    return chunks


def index_to_qdrant(chunks):
    print("Indexing embeddings to Qdrant...")
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    qdrant = Qdrant.from_documents(
        documents=chunks,
        embedding=embeddings,
        url="http://localhost:6333",
        collection_name="edu_content",
    )
    print("✅ Qdrant collection 'edu_content' created and indexed.")


# MAIN EXECUTION


def main():
    pdf_path = "./data/jemh109.pdf"

    # Step 1: Extract text from PDF
    docs = extract_pdf_text(pdf_path)
    minimal_docs = filter_to_minimal_docs(docs)

    # Step 2: Extract images and generate captions
    captions = extract_pdf_images(pdf_path)

    # Step 3: Chunk documents and attach image captions
    chunks = chunk_documents(minimal_docs, captions)

    # Step 4: Indexing embeddings to Qdrant
    index_to_qdrant(chunks)


if __name__ == "__main__":
    main()
