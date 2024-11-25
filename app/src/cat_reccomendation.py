from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import json

class CatetgoryReccomendation():
    def __init__(self, top_k:int=6, model_name:str='all-MiniLM-L6-v2',category_file:str='service_types_subtypes_data_export.json'):
        self.category_file= category_file
        self.model_name = model_name
        self.top_k = top_k
    def get_similar_categories(self,query:str):
        with open(self.category_file, "r") as file:
            cat_dict = json.load(file)

        model = SentenceTransformer(self.model_name)

        categories = list(cat_dict.keys())
        category_embeddings = model.encode(categories)

        query_embedding = model.encode([query])
        similarities = cosine_similarity(query_embedding, category_embeddings)[0]
        top_indices = np.argsort(similarities)[::-1][:self.top_k]
        return [categories[i] for i in top_indices]