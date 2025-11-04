# Multimodal RAG Pipeline for Educational Content

A fully functional Retrieval-Augmented Generation (RAG) system for querying complex, multimodal PDF content using LangChain, Ollama (llava & Mistral), and Qdrant.

## 🎯 Features

- **Multimodal Processing**: Extracts and processes both text and images from PDFs
- **Vision Model Integration**: Uses llava( Large Language and Visual Assistant) to convert images/diagrams into searchable text descriptions
- **Intelligent Chunking**: Preserves context during text chunking
- **Vector Search**: Qdrant-based semantic search
- **RAG Pipeline**: Complete retrieval-augmented generation workflow
- **Summarization**: Optional context summarization before answer generation

## 📋 Prerequisites

### System Requirements
- Python 3.10+
- Docker (for Qdrant)
- 8GB+ RAM recommended
- GPU optional (for faster Ollama inference)

### Required Services

1. **Ollama** - Local LLM inference
2. **Qdrant** - Vector database

|OLLAMA MODELS  | SIZE |
|---------------|------|
|`mistral:7b`    |    4.4 GB|
|`llava:latest`   |          4.7 GB|
|`nomic-embed-text`|         274 MB|

## Quick Start Guide

Get the RAG pipeline running in 10 minutes!

## Step-by-Step Setup

### 1. Prerequisites Installation

#### Install Python 3.10+
```bash
# Check version
python --version  # Should be 3.10 or higher
```

#### Install Docker
```bash
# Windows: Download from docker.com

# macOS
brew install docker

```

#### Install Ollama
```bash
# Windows: Download from ollama.com

# macOS
brew install ollama

```

### 2. Clone and Setup Project

```bash
# Clone repository
git clone https://github.com/md-junaid79/multimodal-rag-pipeline.git
cd multimodal-rag-pipeline

# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

### 3. Start Required Services

#### Terminal 1: Start Qdrant
```bash
docker-compose up
# OR
docker run -p 6333:6333 qdrant/qdrant
```

#### Terminal 2: Verify Ollama is running
```bash
ollama serve  # If not already running as service

# In another terminal, pull models:
ollama pull mistral      #or mistral:latest
ollama pull llava
ollama pull nomic-embed-text
```

### 4. Download PDF

```bash
# Create data directory
mkdir -p data

```
> Download the PDF from Google Drive link:
[📝PDF_LINK](https://drive.google.com/file/d/1J9LBK7I5-eMVcJPnqGDNBrndS6_bcyd5/view)

> Now you are Ready to run setup_pipeline.py


### 5. Index the PDF

```bash
python setup_pipeline.py
```

This will:
- Extract text and images from PDF (~2 min)
- Process images with llava (~5-10 min for 40 images)
- Generate embeddings (~1 min)
- Index into Qdrant (~30 sec)

**Total time: ~10-15 minutes**

### 7. Testing 

```bash
# 1. Indexing
python setup_pipeline.py

# 2. Standard RAG query
python rag_query.py --question "What is a line of sight?"

python rag_query.py -question "Explain solving cos and sin equations for finding heights and distances "

# 3. Multimodal retrieval
python rag_query.py -question "What does the river diagram show?"
python rag_query.py --question "Describe heights and distances"

# 4: Summarization
# Shows both summary and final answer
python rag_query.py --question "What is angle of depression?" --summarize

python rag_query.py --question "how the height of an object or the distance between two distant objects can be determined with the help of trigonometric ratios?" --summarize

```

## 🎓 Key Components

| Component | Technology | Purpose |
|-----------|------------|---------|
| PDF Parser | PyMuPDF | Extract text & images |
| Vision Model | llava | Image→Text conversion |
| Chunking | LangChain | Context-aware splitting |
| Embeddings | nomic-embed-text | Vector generation |
| Vector DB | Qdrant | Semantic search |
| LLM | Mistral | Answer generation |
| Framework | LangChain | Pipeline orchestration |


## Common Issues & Solutions

### Issue: "Ollama connection refused"
**Solution:**
```bash
# Start Ollama service
ollama serve

```
### Issue: "Model not found"
**Solution:**
```bash
# List installed models
ollama list

# Pull missing model
ollama pull mistral:7b 
ollama pull llava
ollama pull nomic-embed-text
```

### Issue: "Out of memory during image processing"
**Solution:**
- Process fewer pages at a time
- Use a smaller vision model
- Close other applications
- Add more RAM/swap



## Quick Commands Reference

```bash

# Index PDF
python setup_pipeline.py

# Basic query
python rag_query.py -q "your question"

# Query with options
python rag_query.py -q "your question" --summarize 

# Check Qdrant status
curl http://localhost:6333/

# Check Ollama status
curl http://localhost:11434/api/tags
```

## Next Steps

1. ✅ Setup complete? Try custom questions!
2. 📖 Read full README.md for advanced features
3. 🎯 Experiment with different PDFs
4. 📊 Monitor performance and optimize


---

## 📝 License

MIT License - See LICENSE file

## 🤝 Contributing

Contributions welcome! Please open an issue or PR.

## 📧 Contact

For questions or issues, please open a GitHub issue.

---

**Built with ❤️ for educational content processing**
