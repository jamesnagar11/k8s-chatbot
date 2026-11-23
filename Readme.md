## K8s Chatbot 

- It is a simple kubernetes docs chatbot for beginners.
- It has been made without using langchain and langgraph to provide more control over functional behaviours.

It is made for demonstration purposes for a production ready rag, but with a very basic skeleton.

### Pre-requisites
- `python shouled be installed`
- `uv should be installed`

### Steps to clone
- Clone
```
git clone https://github.com/jamesnagar11/k8s-chatbot
cd k8s-chatbot
```

- Install dependencies
```
uv venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate

uv add -r requirements.txt
```

- Ingest pipeline


- 

```
uvicorn app.main:app --reload --port 8080
```