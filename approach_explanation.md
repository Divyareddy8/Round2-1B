# 🧠 Approach Explanation

This project is designed to understand and summarize information from multiple PDF documents, based on a **persona** and a **task** provided by the user. The goal is to find and present the most relevant and meaningful content from the documents, in a way that is customized to the user's needs.

The overall approach is divided into two main stages: **1A (Heading Extraction)** and **1B (Semantic Summarization)**.

---

## 🔍 Stage 1A: Extracting Headings from PDFs

In this stage, we give multiple PDF files as input. These files may contain large amounts of text, so the first step is to **extract all the headings** from each PDF. A heading is usually a title or sub-title in bold or large font that gives a clue about the topic of the section.

We use formatting features (like font size and boldness) to detect headings. All the headings from each PDF are saved in a structured format (`headings.json`), which is used in the next stage.

---

## 🧠 Stage 1B: Finding Relevant Headings & Summarizing

In this stage, we take the `headings.json` output from 1A and do the following:

### 1. **Ranking Headings Using BAAI Embeddings**

We use BAAI’s `bge-small-en` model to convert the persona, task, and each heading into embeddings (mathematical representations of meaning). Then, we calculate the **cosine similarity** between the persona-task input and each heading. This helps us find which headings are most relevant.

From this, we pick the **Top 5 most relevant headings**.

### 2. **Summarizing with Phi Model**

For each of the top 5 headings, we go back to the PDF and extract the text under that heading. We then pass this text along with the persona and task into the **Phi model** (phi-1.5.Q4\_0), which generates a detailed summary tailored to the user’s intent.

So, for each of the top 5 headings, we now have a relevant, meaningful summary.

---

## ✅ Final Output

The final output is a JSON file that contains:

* The **Top 5 headings** based on semantic relevance.
* A **custom summary** for each heading, generated using the Phi model.

This approach ensures that users get focused and task-specific insights from a large collection of documents — saving time and improving understanding.

---
