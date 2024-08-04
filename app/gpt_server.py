from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

load_dotenv()


chat = ChatGroq(temperature=0, model_name="llama3-8b-8192")

system = "You are a helpful assistant."
human = "{text}"
prompt = ChatPromptTemplate.from_messages([("system", system), ("human", human)])

chain = prompt | chat


def gpt_server(user_ques, chat_history):
    full_conversation = ""
    for q, r in chat_history:
        full_conversation += f"user question: {q}, AI answer: {r} \n"

    response = chain.invoke(
        {"text": full_conversation + " here is a new question: " + user_ques}
    ).content
    return response
