# Multimodal RAG Pipeline for Educational Content

A fully functional Retrieval-Augmented Generation (RAG) system for querying complex, multimodal PDF content using LangChain, Ollama (Qwen2-VL), and Qdrant.

## 🎯 Features

- **Multimodal Processing**: Extracts and processes both text and images from PDFs
- **Vision Model Integration**: Uses Qwen2-VL to convert images/diagrams into searchable text descriptions
- **Intelligent Chunking**: Preserves context during text chunking
- **Vector Search**: Qdrant-based semantic search
- **RAG Pipeline**: Complete retrieval-augmented generation workflow
- **Caching**: Supports both prompt caching and conversational memory
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

<!-- qwen3-vl:2b             1.9 GB -->
mistral:7b              4.4 GB
llava:latest            4.7 GB
nomic-embed-text        274 MB

# Quick Start Guide

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
# Ubuntu/Debian
sudo apt-get install docker.io

# macOS
brew install docker

# Windows: Download from docker.com
```

#### Install Ollama
```bash
# Linux
curl -fsSL https://ollama.com/install.sh | sh

# macOS
brew install ollama

# Windows: Download from ollama.com
```

### 2. Clone and Setup Project

```bash
# Clone repository
git clone <your-repo-url>
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
ollama pull mistral:7b 
ollama pull llava
ollama pull nomic-embed-text
```

### 4. Download PDF

```bash
# Create data directory
mkdir -p data

# Download the PDF from Google Drive link:
# https://drive.google.com/file/d/1J9LBK7I5-eMVcJPnqGDNBrndS6_bcyd5/view

# Save as: data/Maths_Grade_10.pdf
```

### 5. Verify Setup

```bash
# Run verification script
python verify_setup.py
```

**Expected output:**
```
✓ All checks passed! Ready to run setup_pipeline.py
```

### 6. Index the PDF

```bash
python setup_pipeline.py
```

This will:
- Extract text and images from PDF (~2 min)
- Process images with Qwen2-VL (~5-10 min for 40 images)
- Generate embeddings (~1 min)
- Index into Qdrant (~30 sec)

**Total time: ~10-15 minutes**

### 7. Test with Queries

```bash
# Simple test
python rag_query.py --question "What is a quadratic equation?"

# Test multimodal retrieval
python rag_query.py --question "Describe the trapezoid diagram"

# Test with caching
python rag_query.py --question "What is Pythagoras theorem?" --cache

# Run full test suite
bash test_pipeline.sh
```

## Common Issues & Solutions

### Issue: "Ollama connection refused"
**Solution:**
```bash
# Start Ollama service
ollama serve

# Or on Linux with systemd:
sudo systemctl start ollama
```

### Issue: "Qdrant connection refused"
**Solution:**
```bash
# Check if Qdrant container is running
docker ps | grep qdrant

# Restart if needed
docker-compose restart
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

### Issue: "PDF not found"
**Solution:**
```bash
# Verify PDF location
ls -lh data/Maths_Grade_10.pdf

# Should show file size (e.g., 15-50 MB)
```

## Quick Commands Reference

```bash
# Verify setup
python verify_setup.py

# Index PDF
python setup_pipeline.py

# Basic query
python rag_query.py -q "your question"

# Query with options
python rag_query.py -q "your question" --summarize --cache

# Run all tests
bash test_pipeline.sh

# Check Qdrant status
curl http://localhost:6333/

# Check Ollama status
curl http://localhost:11434/api/tags
```

## Testing the 5 Required Demonstrations

```bash
# 1. Indexing
python setup_pipeline.py

# 2. Standard RAG query
python rag_query.py -q "Explain solving quadratic equations"

# 3. Multimodal retrieval
python rag_query.py -q "What does the trapezoid diagram show?"

# 4. Caching proof
python rag_query.py -q "What is Pythagoras theorem?" --cache
python rag_query.py -q "What is Pythagoras theorem?" --cache  # Faster!

# 5. Summarization
python rag_query.py -q "What is arithmetic progression?" --summarize
```

## Next Steps

1. ✅ Setup complete? Try custom questions!
2. 📖 Read full README.md for advanced features
3. 🔧 Customize config in `.env` file
4. 🎯 Experiment with different PDFs
5. 📊 Monitor performance and optimize

## Performance Tips

- **GPU**: If available, Ollama will automatically use it (10x faster)
- **Batch processing**: Process multiple images at once
- **Cache**: Enable `--cache` for repeated queries
- **Chunk size**: Adjust in `.env` for better/worse context

## Getting Help

- Check `README.md` for detailed documentation
- Run `python rag_query.py --help` for all options
- Review logs in `outputs/` directory
- Open GitHub issue for bugs

---

**Ready to query your educational content! 🚀**
