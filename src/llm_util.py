from llama_cpp import Llama

class LLM_Summarizer:
    def __init__(self, model_path):
        self.llm = Llama(model_path=model_path, n_threads=4, n_ctx=1048)
        self.cache = {}

    def summarize(self, text):
        key = hash(text)
        if key in self.cache:
            return self.cache[key]

        max_output_tokens = 150
        max_total_tokens = 1024
        max_input_tokens = max_total_tokens - max_output_tokens

        prompt = f"Summarize the following section for a user with a specific goal:\n\n{text}\n\nSummary:"

        # Truncate input text based on token length
        text_tokens = self.llm.tokenize(prompt.encode("utf-8"), add_bos=False)

        # Truncate if necessary
        allowed_tokens = max_input_tokens
        if len(text_tokens) > allowed_tokens:
            text_tokens = text_tokens[:allowed_tokens]

        truncated_text = self.llm.detokenize(text_tokens).decode("utf-8", errors="ignore")
        response = self.llm(prompt=truncated_text, max_tokens=150)
        summary = response["choices"][0]["text"].strip()
        self.cache[key] = summary
        return summary
