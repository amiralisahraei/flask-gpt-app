import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.tools.retriever import create_retriever_tool
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain import hub
from langchain.agents import create_tool_calling_agent
from langchain.agents import AgentExecutor

from models import Messages, Users, db


load_dotenv()
upload_dir = os.getenv("UPLOAD_DIR")
main_dir = os.getenv("MAIN_DIR")

llm = ChatGroq(
    model="llama3-groq-70b-8192-tool-use-preview",
    temperature=0,
    max_tokens=None,
    timeout=None,
)

# search tool
search = TavilySearchResults()

if os.path.exists(f"./{main_dir}/{upload_dir}/user_info.pdf"):
    # search through the PDF
    loader = PyPDFLoader(f"./{main_dir}/{upload_dir}/user_info.pdf")
    docs = loader.load()
    documents = RecursiveCharacterTextSplitter(
        chunk_size=1000, chunk_overlap=200
    ).split_documents(docs)

    embedding_model = HuggingFaceEmbeddings()

    vector = FAISS.from_documents(documents, embedding_model)
    retriever = vector.as_retriever()

    retriever_tool = create_retriever_tool(
        retriever,
        "resume_search",
        "Search for information about The user's resume. For any questions about his/her qualifications, experience, and skills, use this tool!",
    )

    tools = [search, retriever_tool]

else:
    tools = [search]


prompt = hub.pull("hwchase17/openai-functions-agent")
agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)


def get_user_id(email):
    user = Users.query.filter_by(email=email).first()
    if user:
        return user.id
    else:
        return None


def gpt_server(user_query, email):

    user_id = get_user_id(email)
    # extract from database
    past_messages = Messages.query.filter_by(user_id=user_id).all()
    combined_history = "\n".join(
        f"{msg.sender}: {msg.message}" for msg in past_messages
    )
    query_with_chat_history = (
        f"previous messages: {combined_history} \n here is new query: {user_query}"
    )

    response = agent_executor.invoke(
        {"input": query_with_chat_history},
        config={"configurable": {"session_id": "<foo>"}},
    )

    # save in database
    user_message = Messages(user_id=user_id, sender="Human_message", message=user_query)
    gpt_message = Messages(
        user_id=user_id, sender="AI_message", message=response.get("output")
    )
    db.session.add(user_message)
    db.session.add(gpt_message)
    db.session.commit()

    return response.get("output")


def clear_chat_history(email):
    user_id = get_user_id(email)
    Messages.query.filter_by(user_id=user_id).delete()
    db.session.commit()
