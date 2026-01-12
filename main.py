from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Optional
import os
from dotenv import load_dotenv
import json
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# basic setup

load_dotenv()
SMTP_HOST=os.getenv("SMTP_HOST")
SMTP_PORT=int(os.getenv("SMTP_PORT"))
SMTP_USER=os.getenv("SMTP_USER")
SMTP_PASS=os.getenv("SMTP_PASS")
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
    real_answer :str

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

def format_answer(cleaned):
    lines = []
    for i, repo in enumerate(cleaned, 1):
        lines.append(
            f"{i}. {repo['name']} ⭐ {repo['stars']}\n"
            f"   Language: {repo['language']}\n"
            f"   {repo['description']}\n"
            f"   {repo['url']}\n"
        )
    return "\n".join(lines)



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
    state["answer"] = format_answer(cleaned)
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

def humanizing_the_json(state:GitState) -> GitState:
    prompt=f"""

takes this json string {state['answer']} and make them into clean readable summmary of each repositories,
make it in paragraph"""
    
    clean_response = model.invoke(prompt[:4000])

    state["real_answer"]=clean_response.content
    return state

def sending_mail(state:GitState) -> GitState:
    msg=MIMEMultipart()
    msg["From"]=SMTP_USER
    msg["To"]="digiance.sagarit@gmail.com"
    msg["Subject"] = "GitHub Repository Summary"
    msg.attach(MIMEText(state["real_answer"], "plain", "utf-8"))

    server=smtplib.SMTP(SMTP_HOST,SMTP_PORT)
    server.starttls()
    server.login(SMTP_USER,SMTP_PASS)
    server.send_message(msg)
    server.quit()

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
graph.add_node("human_answer", humanizing_the_json)
graph.add_node("send_mail",sending_mail)

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

graph.add_edge("searching_repos","human_answer")
graph.add_edge("searching_the_user","human_answer")
graph.add_edge("human_answer","send_mail")
graph.add_edge("send_mail",END)

app=graph.compile()

result=app.invoke({"message":"find repositories on ai agents"})
print(result["real_answer"])