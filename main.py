import os
import glob
from dotenv import load_dotenv
import streamlit as st
from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.tools.tavily_search import TavilySearchResults
from style import apply_custom_theme, render_footer

st.set_page_config(page_title="Nexus Lab | Assistant",layout="centered")
apply_custom_theme()
load_dotenv()

os.environ["LANGCHAIN_API_KEY"]=os.getenv("LANGCHAIN_API_KEY")
os.environ["LANGCHAIN_TARCING_V2"]="true"
os.environ["LANGCHAIN_PROJECT"]="Q&A Chatbot"

@st.cache_resource
def load_research_folder(folder_path="research"):
    pdf_files=glob.glob(os.path.join(folder_path,"*.pdf"))
    if not pdf_files:
        return None,0
    docs=[]
    for pdf in pdf_files:
        docs.extend(PyPDFLoader(pdf).load())
    chunks=RecursiveCharacterTextSplitter(chunk_size=1000,chunk_overlap=150).split_documents(docs)
    embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2")
    return FAISS.from_documents(chunks, embeddings), len(pdf_files)


prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful AI assistant by Nexus Lab. Use the provided context if relevant.\n\nContext:\n{context}"),
    MessagesPlaceholder(variable_name="history"),
    ("user", "{question}")
])

with st.sidebar:
    st.markdown("### ⚙️ Settings & Keys")
    api_key = st.text_input("Groq API Key", type="password", placeholder="gsk_...")
    tavily_key = st.text_input("Tavily API Key (Optional)", type="password", placeholder="tvly-...")
    engine = st.selectbox("Groq Model", ["openai/gpt-oss-120b", "openai/gpt-oss-20b", "qwen/qwen3.8-27b"])
    temperature = st.slider("Temperature", 0.0, 1.0, 0.5)
    max_tokens = st.slider("Max Tokens", 100, 2000, 800)
    use_web = st.toggle("🌐 Enable Tavily Web Search", value=False)
    st.divider()
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

st.markdown('<div class="hero-title">Nexus Lab AI</div>', unsafe_allow_html=True)

vectorstore, pdf_count = load_research_folder("research")
if pdf_count > 0:
    st.caption(f"📚 Loaded {pdf_count} PDF(s) from `research/` folder")

if "messages" not in st.session_state:
    st.session_state.messages = []

for role, content in st.session_state.messages:
    with st.chat_message(role):
        st.markdown(content)

if user_input := st.chat_input("Ask about your research PDFs or live web..."):
    if not api_key:
        st.warning("Please enter your Groq API Key in the sidebar.")
    else:
        with st.chat_message("user"):
            st.markdown(user_input)
        with st.chat_message("assistant"):
            try:
                context_parts = []
                if vectorstore:
                    hits = vectorstore.similarity_search(user_input, k=3)
                    context_parts.append("PDF Context:\n" + "\n".join(d.page_content for d in hits))
                if use_web and tavily_key:
                    os.environ["TAVILY_API_KEY"] = tavily_key
                    web_hits = TavilySearchResults(max_results=3).invoke(user_input)
                    context_parts.append("Web Context:\n" + str(web_hits))
                context = "\n\n".join(context_parts) if context_parts else "No external context."
                llm = ChatGroq(model=engine, api_key=api_key, temperature=temperature, max_tokens=max_tokens)
                response = st.write_stream(
                    (prompt | llm | StrOutputParser()).stream({"question": user_input, "history": st.session_state.messages, "context": context})
                )
                st.session_state.messages.extend([("user", user_input), ("assistant", response)])
            except Exception as e:
                st.error(f"Error: {e}")

render_footer()
