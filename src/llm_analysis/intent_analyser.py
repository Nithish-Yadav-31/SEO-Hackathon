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

def analyze_intent(keywords):
    template = """
        You are a specialized intent analyzer. Given the following keywords extracted from a website, 
        your SOLE TASK is to identify the PRIMARY INTENT of the webpage. 
        Return ONLY the identified intent.

        Keywords: {keywords}
    """
    output_parser = StrOutputParser()
    prompt = PromptTemplate.from_template(template)
    chain = prompt | llm | output_parser

    response = chain.invoke({"keywords":keywords})
    return response