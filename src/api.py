from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import random

from graph import build_graph
from config import DB_PATH
from config import ALLOWED_DEPARTMENTS

app = FastAPI(
    title="NL to SQL Agent",
    version="1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

graph = build_graph()

selected_department = random.choice(
    ALLOWED_DEPARTMENTS
)

print(
    f"[INFO] Department selected: "
    f"{selected_department}"
)

class QueryRequest(BaseModel):
    question: str


@app.get("/")
def health():

    return {
        "status": "ok",
        "department": selected_department
    }


@app.post("/ask")
def ask(req: QueryRequest):

    state = {

        "question": req.question,

        "selected_department":
            selected_department,

        "sql": None,

        "validation_error": None,

        "repair_count": 0,

        "headers": None,

        "rows": None,

        "answer": None,
    }

    result = graph.invoke(state)

    return {
        "department":
            selected_department,

        "answer":
            result["answer"]
    }