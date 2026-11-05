from llama_cpp import Llama
from langchain_community.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings


# 1️⃣ Load LLaMA model
llm = Llama(
    model_path="llama-4-7b.gguf",
    n_ctx=4096,
    n_threads=8,
    verbose=False
)

# 2️⃣ Load embedding model
embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# 3️⃣ Load FAISS index built from Q/A pairs
vector_store = FAISS.load_local(
    "faiss_index",
    embeddings=embedding_model,
    allow_dangerous_deserialization=True
)

# 4️⃣ Function to get bot response
def get_bot_response(user_input):
    try:
        # Retrieve top 5 most similar documents
        docs = vector_store.similarity_search(user_input, k=5)

        print("📚 Context documents retrieved:")
        for i, d in enumerate(docs, 1):
            print(f"\n--- Document {i} ---\n{d.page_content}")

        # Combine retrieved documents into context
        context = "\n\n".join(doc.page_content for doc in docs)

        system_prompt = (
            "You are a helpful assistant at a wine store. "
            "Use the context to answer the user's question. "
            "If the answer is not in the context, say 'I don't know'. "
            "Keep your answer concise and do not generate any additional Q&A."
        )

        # Build prompt WITHOUT any extra Q/A separators
        prompt = f"""
{system_prompt}

Context:
{context}

User Question:
{user_input}

Answer:
"""

        print("\n🧠 Prompt sent to model:\n", prompt)

        # Generate response with stop sequence
        response = llm(
            prompt=prompt,
            max_tokens=512,
            temperature=0.7,
            top_p=0.9,
            stop=["User Question:", "Answer:"]
        )

        print("\n📦 Raw response:\n", response)

        output = response["choices"][0]["text"].strip()
        return output or "Sorry, I didn't get that. Could you rephrase?"

    except Exception as e:
        print("❌ Error:", str(e))
        return "Oops! Something went wrong."

# (Optional) Test if running as a standalone script
if __name__ == "__main__":
    while True:
        question = input("\nYou: ")
        if question.lower() in ("exit", "quit"):
            break
        answer = get_bot_response(question)
        print("Bot:", answer)
