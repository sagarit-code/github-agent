Say less 😤
Here’s the **same README**, but **properly formatted as code (Markdown)** so you can **directly paste it into `README.md`**.

Just copy–paste. No thinking. No fixing.

````md
# 🚀 GitHub AI Agent (v1)

A **graph-based GitHub AI Agent** that understands user intent and intelligently searches **repositories** or **users** using the GitHub API.

This is **version 1** — simple, functional, and intentionally minimal.  
Built as a foundation for more advanced AI-agent workflows.

---

## ✨ What it does (v1)

- 🧠 **Intent Detection**  
  Understands whether the user wants:
  - GitHub repositories  
  - GitHub users  

- 🔀 **Graph-based Routing**  
  Uses a state graph to route queries to the correct tool automatically.

- 🔍 **Repository Search**
  - Sorts by stars
  - Cleans noisy GitHub API responses
  - Returns only relevant fields

- 👤 **User Search**
  - Searches GitHub users by relevance
  - Returns structured JSON output

---

## 🧩 Architecture (Simple Overview)

```text
User Query
   ↓
Intent Classifier
   ↓
Graph Router
   ├── Repository Search
   ├── User Search
   └── End
````

Built using:

* **LangGraph** for workflow orchestration
* **LangChain + Groq (LLM)** for intent classification
* **GitHub REST API** for real-time data

---

## 🛠 Tech Stack

* Python
* LangGraph
* LangChain
* Groq (LLM)
* GitHub REST API
* Requests
* python-dotenv

---

## ⚙️ Setup & Run

### 1️⃣ Clone the repository

```bash
git clone https://github.com/your-username/github-ai-agent.git
cd github-ai-agent
```

### 2️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

### 3️⃣ Environment Variables

Create a `.env` file:

```env
GITHUB_TOKEN=your_github_token
GROQ_API_KEY=your_groq_api_key
```

### 4️⃣ Run the agent

```bash
python main.py
```

Example usage:

```python
result = app.invoke({"message": "find 1 repository on ai agent"})
print(result["answer"])
```

---

## 📦 Output Example

```json
[
  {
    "name": "owner/repo",
    "stars": 1234,
    "language": "Python",
    "description": "AI agent using graphs",
    "url": "https://github.com/owner/repo"
  }
]
```

Clean. Minimal. No noisy junk.

---

## 🧪 Current Limitations (v1)

* Only basic tools (repository & user search)
* Tools are not yet composed into complex workflows
* No memory or multi-step reasoning (yet)

---

## 🔮 Roadmap (Next Versions)

* 🛠 Tool decorators & better tool composition
* 🔁 Multi-tool reasoning
* 🧠 Smarter intent expansion
* 🗂 Advanced filtering & ranking
* 🧪 More complex LangGraph workflows

This project is built **incrementally**, focusing on architecture, clarity, and learning.

---

## 🤝 Contributions

This is an early-stage project.
Issues, ideas, and pull requests are welcome.

---

## ⭐ Final Note

> It works.
> And that’s how every engineering project begins.

```
