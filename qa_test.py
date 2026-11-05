from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_groq import ChatGroq

from company_data import get_structured_company_context

load_dotenv()

emb = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
store = Chroma(persist_directory="chroma_db", embedding_function=emb)
llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0)

SYSTEM_PROMPT = """You are the assistant of TechNova Solutions, an IT services company.
Answer ONLY using the approved sources below. Keep answers short and friendly.
For service details, prices, timelines, project process, and company policies,
the structured company records are authoritative if sources disagree.
Use knowledge-base excerpts for explanations and FAQs not covered by those records.
If the answer is not in the context, reply with ONLY the word NO_ANSWER and nothing else.
Answer only what the sources explicitly state. If the question is about something the sources do not mention (a service, technology or policy that is not listed), reply with ONLY NO_ANSWER.
Never say that TechNova does not offer, build or support something.
Never write handoff messages or offer to connect the user to anyone yourself.

Approved sources:
{structured_context}

Knowledge-base excerpts:
{knowledge_context}
"""

def get_knowledge_context(question, k=6):
    docs = store.similarity_search(question, k=k)
    return "\n\n".join(d.page_content for d in docs)

def answer_question(question, k=6):
    structured_context = get_structured_company_context()
    knowledge_context = get_knowledge_context(question, k)
    reply = llm.invoke([
        (
            "system",
            SYSTEM_PROMPT.format(
                structured_context=structured_context,
                knowledge_context=knowledge_context,
            ),
        ),
        ("human", question),
    ])
    text = reply.content.strip()
    if "NO_ANSWER" in text:
        return {"answer": None, "found": False}
    return {"answer": text, "found": True}


if __name__ == "__main__":
    for q in ["do you provide hosting?", "do you build video games?", "what's the weather today?"]:
        print(q, "->", answer_question(q))