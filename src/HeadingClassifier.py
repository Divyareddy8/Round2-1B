import os
import nltk
from nltk.corpus import stopwords
import joblib
import spacy
from pdfReader import read_pdf
import json
import re
import pandas as pd

# Pandas display options
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)

# Load models and data structures
stop_word_map = joblib.load('models/stop_word_map.pkl')
model = joblib.load('models/Gaussian.pkl')
rf_model = joblib.load('models/RF_Model.pkl')

nlp = spacy.load("en_core_web_sm", disable=["ner", "parser", "lemmatizer"])

POS_TO_INT = {
    "ADJ": 1, "ADP": 2, "ADV": 3, "AUX": 4, "CCONJ": 5,
    "DET": 6, "INTJ": 7, "NOUN": 8, "NUM": 9, "PART": 10,
    "PRON": 11, "PROPN": 12, "PUNCT": 13, "SCONJ": 14, "SYM": 15,
    "VERB": 16, "X": 17, "SPACE": 18
}

punctuations = [".", ",", "!", "?", ";", ":"]
BULLET_CHARS = [
    '•', '◦', '▪', '▫', '‣', '⁃', '–', '—',
    '·', '*', '-', '+', '○', '●', '□', '■',
    '►', '▶', '‧'
]

default_stop_code = stop_word_map['']

# Preprocessing helper
special_chars = punctuations + BULLET_CHARS
escaped_chars = [re.escape(ch) for ch in special_chars]
pattern = r"([" + "".join(escaped_chars) + "])"

def space_around_special_chars(sentence):
    return re.sub(pattern, r' \1 ', sentence)

# Feature extractor for RF
def extract_rf_features(block):
    font_size = block.get("size", 0)
    is_bold = int("bold" in block.get("font", "").lower())
    is_uppercase = int(block.get("text", "").isupper())
    return pd.DataFrame([{
        "font_size": font_size,
        "is_bold": is_bold,
        "is_uppercase": is_uppercase
    }])

# Heading detection using Naive Bayes
def FilterHeadings(path):
    blocks = read_pdf(path)
    texts = [block['text'] for block in blocks]
    triples = []
    for i in range(len(texts)):
        prev = texts[i - 1] if i > 0 else " "
        curr = texts[i]
        nxt = texts[i + 1] if i < len(texts) - 1 else " "
        triples.append((curr, prev, nxt))

    sents_to_process = [space_around_special_chars(sent) for triple in triples for sent in triple]

    encoded_X = []
    buffer = []
    for doc in nlp.pipe(sents_to_process, batch_size=512):
        ans = [0] * 30
        for j, token in enumerate(doc[:30]):
            word = token.lower_
            if word in stop_word_map:
                ans[j] = stop_word_map[word]
            else:
                ans[j] = default_stop_code + POS_TO_INT.get(token.pos_, 0)
        buffer.append(ans)
        if len(buffer) == 3:
            encoded_X.append(buffer[0] + buffer[1] + buffer[2])
            buffer = []

    predictions = model.predict(encoded_X)
    headings = [blocks[i] for i in range(len(predictions)) if predictions[i]]

    # Heuristic enhancement via layout styles
    headings_df = pd.DataFrame(headings)
    headings_df['text_len'] = headings_df['text'].apply(len)

    total_df = pd.DataFrame(blocks)
    total_df['text_len'] = total_df['text'].apply(len)

    headings_group = headings_df.groupby(['font', 'color', 'size', 'center'])['text_len'].sum()
    total_group = total_df.groupby(['font', 'color', 'size', 'center'])['text_len'].sum()

    qualified_styles = {
        style for style, total_len in total_group.items()
        if headings_group.get(style, 0) / total_len >= 0.7
    }

    def make_style(row):
        return (row['font'], row['color'], row['size'], row['center'])

    headings_df['style'] = headings_df.apply(make_style, axis=1)
    total_df['style'] = total_df.apply(make_style, axis=1)

    existing_texts = set(headings_df['text'])

    final_rows = []
    for _, row in total_df.iterrows():
        style = row['style']
        if (row['text'] in existing_texts) or (style in qualified_styles):
            final_rows.append(row)

    headings_df = pd.DataFrame(final_rows).reset_index(drop=True)
    final_headings = headings_df.to_dict(orient='records')
    return final_headings

# Heading classification into H1, H2, etc.
def classifyHeadings(path,output_path):
    all_headings = FilterHeadings(path)
    headings = []
    features = []
    for heading in all_headings:
        text = heading['text']
        features_for_rf = extract_rf_features(heading) 
        features.append(features_for_rf.to_dict(orient='records')[0])
        heading_level = rf_model.predict(features_for_rf)[0]

        headings.append({
            "level": heading_level,
            "text": heading["text"],
            "page": heading.get("page_no", 0) - 1
        })
    title_idx = -1
    max_h1_font = 0
    for i in range(len(all_headings)):
        if headings[i]['page'] != 0: break
        if headings[i]['level'] == 'H1':
            if max_h1_font < features[i]['font_size']:
                max_h1_font = features[i]['font_size']
                title_idx = i
    for i in range(len(all_headings)):
        if headings[i]['page'] == 0: continue
        if headings[i]['level']=='H1' and features[i]['font_size'] >= max_h1_font:
            title_idx = -1
            break
    title_text = ""
    if title_idx != -1:
        title_text = headings.pop(title_idx)['text']

    final_output = {
        "title": title_text,
        "outline": headings
    }
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(final_output, f, indent=2, ensure_ascii=False)
