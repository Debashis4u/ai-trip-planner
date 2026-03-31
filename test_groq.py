from langchain_groq import ChatGroq
import os

llm = ChatGroq(
    model_name="gpt-4",
    # groq_api_key=os.getenv("GROQ_API_KEY"),
)
response = llm.invoke("hello..")
print(response.content)