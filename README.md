# 📘 Round 1B – Persona-Driven Document Intelligence  
**Connecting the Dots Challenge**

## 🧠 Overview

In Round 1B, we build an intelligent document analyst that extracts and ranks the most relevant sections from a collection of PDFs based on a specific **persona** and a **job-to-be-done**. This solution personalizes reading by surfacing content that truly matters to the user.

The pipeline combines structured outline extraction (from Round 1A), sentence embeddings for relevance ranking, and lightweight local summarization using an offline LLM.

---

## 🚀 Architecture & Components

1. **Input PDFs** — A folder of 3–10 PDFs related to a task.
2. **Round 1A Outline Extractor** — Extracts document structure (Title, H1, H2, H3) with page numbers.
3. **Embedding-based Relevance Ranking**
   - Uses **BAAI bge-small-en** sentence embedding model.
   - Computes cosine similarity between heading text and persona+job.
4. **Lightweight LLM Summarization**
   - Uses **Phi 1.5 (GGUF format)** — a 1GB quantized model running offline.
   - Summarizes top-ranked sections.

---


## 🐳 Docker Instructions

### 🔧 Build the Docker Image (Requires Internet)

```bash
docker build --platform linux/amd64 -t headingclassifier:1b .
```

Of course, Divya! Here's a clean, ready-to-copy **README snippet** you can include in your project:

---

## 🚀 Running the Docker Container

Depending on your terminal and operating system, use one of the following commands to run the Docker container:

### ✅ PowerShell (Windows)

```powershell
docker run --rm ^
  -v "$(Get-Location)\input:/app/input" ^
  -v "$(Get-Location)\output:/app/output" ^
  --network none ^
  headingclassifier:1b
```

### ✅ WSL / Git Bash / Linux / macOS

```bash
docker run --rm \
  -v $(pwd)/input:/app/input \
  -v $(pwd)/output:/app/output \
  --network none \
  headingclassifier:1b
```
* 📂 All PDFs in `/input` are automatically processed.
* 📄 JSON output will be saved to `/output`.

---

## ✅ Requirements & Constraints Met

| Constraint              | Status      |
| ----------------------- | ----------- |
| CPU-only                | ✅           |
| Model size ≤ 1GB        | ✅           |
| No internet at runtime  | ✅           |
| Execution time ≤ 60s    | ✅           |
| Multilingual extensible |✅           |

---

## 📌 

* BAAI bge-small-en model is used for embedding-based ranking.
* Phi 1.5 LLM (quantized GGUF) runs fully offline using `ggml` or `ctransformers`.
* No hardcoded file logic. Fully generalizable across domains and personas.

---
