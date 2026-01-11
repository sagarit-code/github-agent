from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Optional
import os
from dotenv import load_dotenv
import json
import requests

# basic setup

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

model = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=GROQ_API_KEY
)

# state

class Intent(TypedDict):
    intent: str
    query: str
    count: Optional[int]

class GitState(TypedDict):
    message: str
    intent: Optional[Intent]
    answer: str

# nodes

def clean_repositories(raw_json, limit=5):
    cleaned = []

    for repo in raw_json.get("items", [])[:limit]:
        cleaned.append({
            "name": repo.get("full_name"),
            "stars": repo.get("stargazers_count"),
            "language": repo.get("language"),
            "description": repo.get("description"),
            "url": repo.get("html_url")
        })

    return cleaned


def finding_the_intent(state: GitState) -> GitState:
    prompt = f"""
Return STRICT JSON only.

Allowed intents:
- repositories
- users
- none

JSON format:
{{
  "intent": "",
  "query": "",
  "count": null
}}

User query:
{state["message"]}
"""

    response = model.invoke(prompt)

    try:
        raw = response.content.strip()
        if raw.startswith("```"):
            raw = raw.strip("`").replace("json", "").strip()

        intent_json = json.loads(raw)
    except Exception:
        intent_json = {
            "intent": "none",
            "query": "",
            "count": None
        }

    state["intent"] = intent_json
    return state


def search_repo(state: GitState) -> GitState:
    url = "https://api.github.com/search/repositories"

    limit = state["intent"].get("count") or 5

    params = {
        "q": state["intent"]["query"],
        "sort": "stars",
        "order": "desc",
        "per_page": limit
    }

    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "langgraph-agent"
    }

    response = requests.get(url, params=params, headers=headers)
    raw = response.json()

    cleaned = clean_repositories(raw, limit)

    state["answer"] = json.dumps(cleaned, indent=2)
    return state



def search_user(state: GitState) -> GitState:
    url = "https://api.github.com/search/users"

    params = {
        "q": state["intent"]["query"],
        "sort": "followers",
        "order": "desc",
        "per_page": state["intent"].get("count") or 10
    }

    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "langgraph-agent"
    }

    response = requests.get(url, params=params, headers=headers)

    state["answer"] = json.dumps(response.json(), indent=2)
    return state

#conditional router

def route_by_intent(state: GitState) -> str:
    intent = state["intent"]["intent"]

    if intent == "repositories":
        return "repo"
    elif intent == "users":
        return "user"
    else:
        return "end"


#graph logic
graph=StateGraph(GitState)

graph.add_node("intent_classifier", finding_the_intent)
graph.add_node("searching_repos",search_repo)
graph.add_node("searching_the_user",search_user)

graph.add_edge(START,"intent_classifier")
graph.add_conditional_edges(
    "intent_classifier",
    route_by_intent,
    {
        "repo":"searching_repos",
        "user":"searching_the_user",
        "end":END
    }

)
graph.add_edge("searching_repos",END)
graph.add_edge("searching_the_user",END)

app=graph.compile()

result=app.invoke({"message":"find 1 repository on ai agent"})
print(result["answer"][-1])