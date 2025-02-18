import os
from dotenv import load_dotenv
load_dotenv()
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
os.environ['GOOGLE_API_KEY'] = GOOGLE_API_KEY
from langchain_google_genai import ChatGoogleGenerativeAI
llm = ChatGoogleGenerativeAI(model = "gemini-2.0-flash")

def search_query_writer(keywords):
    template = """ 
        You are a specialized query generator. Given the following keywords, 
        your sole task is to formulate a concise and effective search query for finding comprehensive information on the web,
        covering a broad range of topics mentioned.  Do not overly focus on one specific topic; aim for a balanced and general query.
        Return ONLY the search query itself.

        Keywords: {keywords}
    """
    output_parser = StrOutputParser()
    prompt = PromptTemplate.from_template(template)
    chain = prompt | llm | output_parser

    response = chain.invoke({"keywords":keywords})
    return response