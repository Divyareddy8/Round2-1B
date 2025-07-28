import nltk
import string
import torch
import spacy
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sentence_transformers import SentenceTransformer, util

# Download NLTK data
nltk.download('stopwords')
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('omw-1.4')

stop_words = set(stopwords.words('english'))
nlp = spacy.load("en_core_web_sm")

class EmbeddingModel:
    def __init__(self):
        self.model = SentenceTransformer('BAAI/bge-small-en')

    def encode(self, texts, convert_to_tensor=False):
        return self.model.encode(texts, convert_to_tensor=convert_to_tensor, normalize_embeddings=True)

def remove_stopwords(text):
    tokens = word_tokenize(text.lower())
    return ' '.join([
        word for word in tokens 
        if word not in stop_words and word not in string.punctuation
    ])

def remove_verbs(text):
    doc = nlp(text)
    return " ".join([token.text for token in doc if token.pos_ != "VERB"])

def format_query(query):
    cleaned_query = remove_stopwords(query)
    return "Represent this sentence for searching relevant passages: " + cleaned_query

def rank_headings(headings, query, model, top_k=5):
    formatted_query = format_query(query)
    cleaned_headings = [remove_stopwords(h) for h in headings]

    query_embedding = model.encode([formatted_query], convert_to_tensor=True)[0]
    heading_embeddings = model.encode(cleaned_headings, convert_to_tensor=True)

    scores = util.cos_sim(query_embedding, heading_embeddings)[0]
    top_results = torch.topk(scores, k=min(top_k, len(headings)))

    ranked = []
    for score, idx in zip(top_results[0], top_results[1]):
        ranked.append((headings[idx], float(score), int(idx)))

    return ranked
