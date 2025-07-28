import os
import json
import fitz  # PyMuPDF
from langdetect import detect
from langdetect.lang_detect_exception import LangDetectException
from deep_translator import GoogleTranslator

def extract_sections_from_jsons(documents, pdf_folder, json_folder):
    sections = []

    for doc in documents:
        pdf_filename = doc["filename"]
        json_filename = os.path.splitext(pdf_filename)[0] + ".json"
        json_path = os.path.join(json_folder, json_filename)
        pdf_path = os.path.join(pdf_folder, pdf_filename)

        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        pdf_doc = fitz.open(pdf_path)
        outline = data.get("outline", [])

        for i, item in enumerate(outline):
            text = item.get("text", "").strip()
            if len(text.split()) > 5:
                start_page = item.get("page", 0)
                page = pdf_doc.load_page(start_page)
                section_text = page.get_text().strip()

                # Attempt language detection and translation
                try:
                    lang = detect(section_text)
                    if lang != "en":
                        translated_text = GoogleTranslator(source='auto', target='en').translate(section_text)
                    else:
                        translated_text = section_text
                except LangDetectException:
                    translated_text = section_text  # fallback to original if detection fails

                sections.append({
                    "document": pdf_filename,
                    "page": start_page,
                    "title": text,
                    "text": translated_text
                })

        pdf_doc.close()

    return sections