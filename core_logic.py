from llama_cpp import Llama
from sentence_transformers import SentenceTransformer
from datetime import datetime
import faiss
import numpy as np
import os
import fitz

# 🔹 Emoji Enhancer
def add_eco_emojis(text):
    emoji_map = {
        "recycle": "♻️",
        "carbon footprint": "🦶🌍",
        "plant": "🌱",
        "tree": "🌳",
        "green": "💚",
        "solar": "☀️",
        "energy": "⚡",
        "electric": "🔌",
        "bike": "🚲",
        "compost": "🍂",
        "plastic": "🚯",
        "eco": "🌿",
        "earth": "🌍",
        "climate": "🔥🌎",
        "reuse": "🔁",
        "sustainable": "🔋",
    }
    for keyword, emoji in emoji_map.items():
        text = text.replace(keyword, f"{keyword} {emoji}")
    return text

# 🔹 Document Loader
def load_documents(folder="docs"):
    docs = []
    sources = []
    for filename in os.listdir(folder):
        path = os.path.join(folder, filename)
        if filename.endswith(".txt"):
            with open(path, "r", encoding="utf-8") as f:
                text = f.read()
        elif filename.endswith(".pdf"):
            doc = fitz.open(path)
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
        else:
            continue
        chunks = [text[i:i+500] for i in range(0, len(text), 500)]
        docs.extend(chunks)
        sources.extend([filename] * len(chunks))
    return docs, sources

# 🔹 Embedding and Indexing
def build_faiss_index(chunks):
    embedder = SentenceTransformer("all-MiniLM-L6-v2")
    embeddings = embedder.encode(chunks)
    index = faiss.IndexFlatL2(embeddings[0].shape[0])
    index.add(np.array(embeddings))
    return embedder, index, chunks

# 🔹 Load LLM
def load_model():
    return Llama(
        model_path="C:/Users/sabar/Documents/llama-local/mistral-7b-instruct-v0.1.Q4_K_M.gguf",
        n_gpu_layers=40,
        n_ctx=2048,
        use_mlock=False,
        chat_format="llama-2",
    )

# 🔹 Load All Together
def load_model_and_index(doc_folder="docs"):
    llm = load_model()
    doc_chunks, _ = load_documents(doc_folder)
    embedder, index, chunks = build_faiss_index(doc_chunks)
    return llm, embedder, index, chunks

# 🔹 Level Prompts
def get_level_prompt(level):
    levels = {
        "beginner": "You are EcoFriend, an AI assistant for beginners in sustainability. Explain things simply and be very encouraging. Focus on easy eco-friendly habits and everyday actions.",
        "explorer": "You are EcoFriend, an AI for intermediate users who already follow some green habits. Give slightly advanced tips, eco challenges, and explain the impact of actions.",
        "eco-warrior": "You are EcoFriend, an AI for advanced users deeply committed to sustainability. Provide expert-level advice, deep insights, and promote high-impact lifestyle changes."
    }
    return levels.get(level, levels["beginner"])

# 🔹 Chat Function (Core)
def chat_with_ecofriend(user_input, eco_level, model, embedder, index, chunks):
    query_vec = embedder.encode([user_input])
    D, I = index.search(np.array(query_vec), k=3)
    context = "\n".join([chunks[i] for i in I[0]])

    messages = [
        {"role": "system", "content": get_level_prompt(eco_level)},
        {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {user_input}"}
    ]

    output = model.create_chat_completion(
        messages=messages,
        max_tokens=300,
        stop=["</s>"]
    )
    response = output["choices"][0]["message"]["content"].strip()
    return add_eco_emojis(response)