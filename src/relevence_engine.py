import numpy as np
from embedding_util import EmbeddingModel, remove_verbs, format_query

class RelevanceRanker:
    def __init__(self):
        self.embedder = EmbeddingModel()

    def rank(self, sections, query, top_k=5):
        cleaned_query = format_query(remove_verbs(query))
        section_texts = [remove_verbs(s["title"] + " " + s["text"]) for s in sections]
        section_embs = self.embedder.encode(section_texts)
        query_emb = self.embedder.encode([cleaned_query])[0]

        scores = np.dot(section_embs, query_emb)
        top_indices = np.argsort(scores)[::-1][:top_k]

        return [sections[i] for i in top_indices]
