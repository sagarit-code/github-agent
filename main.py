from langchain_groq import ChatGroq
from langgraph.graph import StateGraph
from typing import Dict,TypedDict
import os
from typing import TypedDict, Optional
from dotenv import load_dotenv
import json
import requests

load_dotenv()
token=os.getenv("GITHUB_TOKEN")
model = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.getenv("GROQ_API_KEY")
)
class Intent(TypedDict):
    intent: str
    query: str
    count: Optional[int]

class GitState(TypedDict):
    message: str
    intent: Optional[Intent]
    answer:str




def finding_the_intent(state: GitState) -> GitState:
    user_message = state["message"]

    prompt = f"""
You are an intent classification engine for GitHub search.

Your task is to analyze the user query and output a STRICT JSON object.
Do not include explanations or extra text.

The intent must be one of:
- "repositories"
- "topics"
- "users"
- "code"
- "none"

Rules:
1. If the user asks for projects, repos, libraries, frameworks → repositories
2. If the user asks for categories, trends, popular areas → topics
3. If the user asks for people, developers, maintainers → users
4. If the user asks for implementation details or code → code
5. If unclear or unrelated → none

Extract:
- "intent"
- "query": cleaned search phrase
- "count": number of results requested, or null

User query:
\"\"\"{user_message}\"\"\"

Output JSON only.
"""

    response = model.invoke(prompt)

    try:
        intent_json = json.loads(response.content)
    except Exception:
        intent_json = {
            "intent": "none",
            "query": "",
            "count": None
        }

    state["intent"] = intent_json
    return state


#main hub for calling all the other function that we defined
def main_hub(state:GitState) -> GitState:
    if state["intent"]["intent"]=="users":
        return search_user()
    



def search_user(state:GitState):
    url="https://api.github.com/search/users"
    parameters={
        "q":state["intent"]["query"],
        "sort":"followers",
        "order":"desc"
    }
    headers={
        "Authorization":f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-Github-Api-Version" : "2022-11-28",
        "User-Agent": "sagarit-github-agent"


    }

    response=requests.get(url=url,params=parameters,headers=headers)

    answers=response.json()
    return answers