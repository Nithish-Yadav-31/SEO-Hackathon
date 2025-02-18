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

def compare_intents(keywords1, keywords2):
    template = """
        You are a specialized intent analyzer. Given intents from one website and corresponding competitor website, 
        your SOLE TASK is to identify the OVERALL INTENT BETWEEN one website and competitor website.

        Website intent: {keywords1} 
        Competitor Intent: {keywords2}
    """
    output_parser = StrOutputParser()
    prompt = PromptTemplate.from_template(template)
    chain = prompt | llm | output_parser

    response = chain.invoke({"keywords1":keywords1, "keywords2":keywords2})
    return response