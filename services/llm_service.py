from openai import OpenAI
from config import Config

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=Config.OPENROUTER_API_KEY
)

def generate_answer(question, context_chunks):
    # Combine retrieved chunks into context
    context = "\n\n".join(context_chunks)

    prompt = f"""Answer the question based only on the context below. 
If the answer isn't in the context, say you don't have enough information.

Context:
{context}

Question: {question}

Answer:"""

    response = client.chat.completions.create(
    model="anthropic/claude-haiku-4.5",  # fast, cheap, great for RAG Q&A
    messages=[{"role": "user", "content": prompt}],
    max_tokens=500
)

    return response.choices[0].message.content