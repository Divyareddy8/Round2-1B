import os
import json
from datetime import datetime
from pdf_util import extract_sections_from_jsons
from llm_util import LLM_Summarizer
from embedding_util import rank_headings, EmbeddingModel
from HeadingClassifier import classifyHeadings

INPUT_JSON = "input/input.json"
OUTPUT_JSON = "output/output.json"
PHI_MODEL_PATH = "models/phi-1.5.Q4_0.gguf"
PDF_DIR = "input/PDFs"
JSON_DIR = "input/PDFs"

for filename in os.listdir(PDF_DIR):
    if filename.lower().endswith(".pdf"):
        base_name = os.path.splitext(filename)[0]
        pdf_path = os.path.join(PDF_DIR, filename)
        json_path = os.path.join(JSON_DIR, base_name + ".json")

        classifyHeadings(pdf_path, json_path)

def main():
    with open(INPUT_JSON) as f:
        data = json.load(f)

    persona = data["persona"]["role"]
    task = data["job_to_be_done"]["task"]
    pdf_files = data["documents"]  # List of { "filename": "xyz.pdf" }

    full_context = f"{persona}. Task: {task}"

    #  Extract sections from existing .json files corresponding to each PDF
    all_sections = extract_sections_from_jsons(pdf_files, PDF_DIR, JSON_DIR)

    #  Rank headings using embeddings
    model = EmbeddingModel()
    headings = [s["title"] for s in all_sections]
    ranked_headings = rank_headings(headings, full_context, model, top_k=5)

    #  Pick top sections based on ranked heading indexes
    top_sections = [all_sections[idx] for (_, _, idx) in ranked_headings]

    #  Summarize top sections using Phi model
    summarizer = LLM_Summarizer(PHI_MODEL_PATH)
    summarized = []
    for sec in top_sections:
        summary = summarizer.summarize(sec["text"])
        summarized.append({
            "document": sec["document"],
            "page_number": sec["page"],  # Already 0-based
            "refined_text": summary
        })

    #  Format output JSON
    output = {
        "metadata": {
            "input_documents": [d["filename"] for d in pdf_files],
            "persona": persona,
            "job_to_be_done": task,
            "processing_timestamp": datetime.utcnow().isoformat()
        },
        "extracted_sections": [
            {
                "document": s["document"],
                "section_title": s["title"],
                "importance_rank": i + 1,
                "page_number": s["page"]  # Already 0-based
            }
            for i, s in enumerate(top_sections)
        ],
        "subsection_analysis": summarized
    }

    with open(OUTPUT_JSON, "w") as f:
        json.dump(output, f, indent=2)

    print(" Output written to:", OUTPUT_JSON)

if __name__ == "__main__":
    main()
