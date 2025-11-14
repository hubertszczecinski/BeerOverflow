from sentence_transformers import SentenceTransformer
import pandas as pd
import numpy as np


class Matcher:
    def __init__(self, id_path):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.ids = pd.read_csv(id_path)
        self.ids["embeddings"] = self.ids["description"].apply(lambda x: self.model.encode(x))
        self.embeds = np.stack(self.ids["embeddings"].to_list(), axis=0)

    def match(self, text):
        embed = self.model.encode(text)
        similarities = self.embeds @ embed
        return self.ids.iloc[similarities.argmax()]["id"]
