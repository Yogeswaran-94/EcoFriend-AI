from app.core_logic import load_model, load_documents, build_faiss_index, chat_with_ecofriend
from datetime import datetime

# === Load Model + Embeddings ===
print("🧠 Loading EcoFriend model...")
llm = load_model()

print("📚 Loading documents...")
doc_chunks = load_documents("docs")
embedder, index, chunks = build_faiss_index(doc_chunks)

# === Choose Eco Level ===
print("\n🌱 Welcome to EcoFriend CLI!")
print("Choose your sustainability level:")
print("1 - Beginner\n2 - Explorer\n3 - Eco-Warrior")
level_map = {"1": "beginner", "2": "explorer", "3": "eco-warrior"}
level_input = input("Enter your choice (1/2/3): ").strip()
eco_level = level_map.get(level_input, "beginner")
print(f"\n🧠 EcoFriend is now in **{eco_level.title()}** mode!")

# === Open Log File ===
log_file = "eco_log.txt"
with open(log_file, "a", encoding="utf-8") as f:
    f.write(f"\n\n--- New Chat Session: {datetime.now()} [Level: {eco_level.title()}] ---\n")

# === Chat Loop ===
while True:
    user_input = input("You: ")
    if user_input.lower() in ["exit", "quit"]:
        print("🌿 EcoFriend: Stay green! Catch you later 💚")
        try:
            llm.__del__()
        except Exception:
             print("🔒 Cleanup skipped (already handled).")

        break

    response = chat_with_ecofriend(user_input, eco_level, llm, embedder, index, chunks)

    print(f"EcoFriend ({eco_level.title()}) 🌿:", response)

    # Save to log
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"\n[Level: {eco_level.title()}]\n")
        f.write(f"You: {user_input}\n")
        f.write(f"EcoFriend: {response}\n")
