from fastapi import FastAPI
from typing import List
import pickle
import pandas as pd

app = FastAPI()

# Load rules from pickled files
with open(r"C:\Users\vigne\OneDrive\Desktop\Viggu\sem8\mini_proj\recommendations\frequent_itemsets.pkl", "rb") as f:
    frequent_itemsets = pickle.load(f)

with open(r"C:\Users\vigne\OneDrive\Desktop\Viggu\sem8\mini_proj\recommendations\rules.pkl", "rb") as f:
    rules = pickle.load(f)

def recommend_items(cart_items, rules, top_n=5, alpha=0.7):
    cart_items = frozenset(cart_items)

    matching_rules = rules[rules['antecedents'].map(lambda x: cart_items & x == x)]

    if matching_rules.empty:
        return []

    matching_rules = matching_rules.copy()  # avoid SettingWithCopyWarning
    matching_rules['score'] = alpha * matching_rules['confidence'] + (1 - alpha) * matching_rules['lift']
    matching_rules = matching_rules.sort_values(by='score', ascending=False)

    recommended_items = []
    seen_items = set()

    for _, rule in matching_rules.iterrows():
        for item in rule['consequents']:
            if item not in cart_items and item not in seen_items:
                recommended_items.append(item)
                seen_items.add(item)
            if len(recommended_items) == top_n:
                return recommended_items
    return recommended_items

@app.post("/recommend/")
def recommend(cart: List[str]):
    recommendations = recommend_items(cart, rules, top_n=5)
    if recommendations:
        return {"status": "success", "recommended_items": recommendations}
    return {"status": "error", "message": "No recommendations available"}
