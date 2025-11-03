from langchain_qdrant import QdrantVectorStore
from langchain_classic.chains import RetrievalQA
from langchain_ollama import OllamaEmbeddings
from langchain_ollama import OllamaLLM
from qdrant_client import QdrantClient
import argparse

def build_rag_chain():
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    client = QdrantClient(url="http://localhost:6333")
    qdrant_store = QdrantVectorStore(client=client, collection_name="edu_content", embedding=embeddings)
    retriever = qdrant_store.as_retriever(search_kwargs={"k": 3})

    llm = OllamaLLM(model="mistral")
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        chain_type="stuff"
    )
    return qa_chain

def run_query(question, summarize=False):
    chain = build_rag_chain()

    if summarize:
        print("\n ⚙️.. Summarizing retrieved content before final generation...")
        summary_prompt = f"Summarize the context for this query: {question}"
        summary = chain.invoke(summary_prompt)
        print("\n 📌 [Retrieved Summary]:", summary)
        final_prompt = f"Based on this summary, answer the query: {question}"
        answer = chain.invoke(final_prompt)
    else:
        answer = chain.invoke(question)

    print("\n📝 [Final Answer]:", answer)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--question", required=True)
    parser.add_argument("--summarize", action="store_true")
    args = parser.parse_args()

    run_query(args.question, args.summarize)

if __name__ == "__main__":
    main()
