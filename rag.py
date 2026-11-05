import shutil
from dotenv import load_dotenv
from pathlib import Path
load_dotenv()
from langchain_text_splitters import MarkdownHeaderTextSplitter
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings


shutil.rmtree("chroma_db", ignore_errors=True)

knowledge_base = Path(__file__).resolve().parent / "docs" / "technova_knowledge_base.md"
text = knowledge_base.read_text(encoding="utf-8")
splitter = MarkdownHeaderTextSplitter(
    headers_to_split_on=[("#", "title"), ("##", "section")],
    strip_headers=False,
)
chunks = splitter.split_text(text)
emb = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
Chroma.from_documents(chunks, emb, persist_directory="chroma_db")

print("stored:", len(chunks))
 