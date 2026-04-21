from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

INTENTS = {
    "high_protein": [
        "high protein meal",
        "gym meal",
        "protein rich breakfast",
        "muscle food"
    ],
    "weight_loss": [
        "weight loss meal",
        "fat loss food",
        "light healthy meal"
    ],
    "breakfast": [
        "breakfast",
        "morning meal",
        "nashta"
    ],
    "lunch": [
        "lunch",
        "afternoon meal"
    ],
    "dinner": [
        "dinner",
        "night meal",
        "raat ka khana"
    ],
    "veg": [
        "veg meal",
        "vegetarian food"
    ]
}

intent_vectors = {
    key: model.encode(values, convert_to_tensor=True)
    for key, values in INTENTS.items()
}

def detect_intents(text):
    query = model.encode(text, convert_to_tensor=True)

    found = []

    for key, vecs in intent_vectors.items():
        score = util.cos_sim(query, vecs).max().item()

        if score > 0.55:
            found.append(key)

    return found