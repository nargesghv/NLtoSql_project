from langgraph.graph import StateGraph, END
from langchain_ollama import ChatOllama

import json
import re

from state import NL2SQLState

from config import (
    OLLAMA_MODEL,
    OLLAMA_BASE_URL
)

from db import (
    get_schema_text,
    execute_sql,
    format_results
)

from prompts import build_sql_prompt

from guardrails import (
    clean_sql,
    validate_sql
)

MAX_REPAIR_ATTEMPTS = 2

llm = ChatOllama(
    model=OLLAMA_MODEL,
    base_url=OLLAMA_BASE_URL,
    temperature=0
)


# --------------------------------------------------
# Question Agent
# --------------------------------------------------

def question_agent(state):

    question = state["question"]

    prompt = f"""
Extract:

1. intent
2. entities
3. needs_join
4. aggregation

Return JSON only.

Question:

{question}

Example:

{{
  "intent":"certification_lookup",
  "entities":["AWS"],
  "needs_join":true,
  "aggregation":false
}}
"""

    response = llm.invoke(prompt)

    content = response.content.strip()

    content = re.sub(
        r"^```json",
        "",
        content,
        flags=re.IGNORECASE
    )

    content = content.replace(
        "```",
        ""
    ).strip()

    try:

        state["question_analysis"] = json.loads(
            content
        )

    except Exception:

        state["question_analysis"] = {
            "intent": "unknown",
            "entities": [],
            "needs_join": False,
            "aggregation": False,
        }

    return state


# --------------------------------------------------
# Schema Agent
# --------------------------------------------------

def schema_agent(state):

    state["schema"] = get_schema_text()

    return state


# --------------------------------------------------
# SQL Generator
# --------------------------------------------------

def sql_generator_agent(state):

    prompt = build_sql_prompt(
        question=state["question"],
        schema=state["schema"],
        selected_department=state["selected_department"],
        analysis=state["question_analysis"]
    )

    response = llm.invoke(prompt)

    state["sql"] = clean_sql(
        response.content
    )

    return state


# --------------------------------------------------
# Validator
# --------------------------------------------------

def sql_validator_agent(state):

    ok, message = validate_sql(
        state["sql"],
        state["selected_department"]
    )

    state["validation_error"] = (
        None if ok else message
    )

    return state


# --------------------------------------------------
# Repair Agent
# --------------------------------------------------

def sql_repair_agent(state):

    prompt = f"""
You are a SQL repair agent.

Fix this SQL.

Requirements:

- SQLite syntax
- SELECT only

Must contain:

Department = '{state["selected_department"]}'

Fix:

- invalid columns
- invalid joins
- invalid aliases
- missing department filters

Validation Error:

{state["validation_error"]}

SQL:

{state["sql"]}

Return SQL only.
"""

    response = llm.invoke(prompt)

    state["sql"] = clean_sql(
        response.content
    )

    state["repair_count"] += 1

    return state


# --------------------------------------------------
# Executor
# --------------------------------------------------

def sql_executor_agent(state):

    try:

        headers, rows = execute_sql(
            state["sql"]
        )

        state["headers"] = headers
        state["rows"] = rows

        state["validation_error"] = None

    except Exception as e:

        state["validation_error"] = (
            f"Execution Error: {e}"
        )

    return state


# --------------------------------------------------
# Answer
# --------------------------------------------------

def answer_agent(state):

    if state["validation_error"]:

        state["answer"] = (
            f"Blocked/Error:\n"
            f"{state['validation_error']}\n\n"
            f"SQL:\n{state['sql']}"
        )

        return state

    result_table = format_results(
        state["headers"],
        state["rows"]
    )

    state["answer"] = (
        f"SQL:\n{state['sql']}\n\n"
        f"Results:\n{result_table}"
    )

    return state


# --------------------------------------------------
# Routers
# --------------------------------------------------

def validation_router(state):

    if not state["validation_error"]:
        return "execute"

    if state["repair_count"] >= MAX_REPAIR_ATTEMPTS:
        return "blocked"

    return "repair"


def execution_router(state):

    if state["validation_error"]:

        if state["repair_count"] >= MAX_REPAIR_ATTEMPTS:
            return "blocked"

        return "repair"

    return "answer"


# --------------------------------------------------
# Graph
# --------------------------------------------------

def build_graph():

    graph = StateGraph(
        NL2SQLState
    )

    graph.add_node(
        "question_agent",
        question_agent
    )

    graph.add_node(
        "schema_agent",
        schema_agent
    )

    graph.add_node(
        "sql_generator_agent",
        sql_generator_agent
    )

    graph.add_node(
        "sql_validator_agent",
        sql_validator_agent
    )

    graph.add_node(
        "sql_repair_agent",
        sql_repair_agent
    )

    graph.add_node(
        "sql_executor_agent",
        sql_executor_agent
    )

    graph.add_node(
        "answer_agent",
        answer_agent
    )

    graph.set_entry_point(
        "question_agent"
    )

    graph.add_edge(
        "question_agent",
        "schema_agent"
    )

    graph.add_edge(
        "schema_agent",
        "sql_generator_agent"
    )

    graph.add_edge(
        "sql_generator_agent",
        "sql_validator_agent"
    )

    graph.add_conditional_edges(
        "sql_validator_agent",
        validation_router,
        {
            "execute":
                "sql_executor_agent",

            "repair":
                "sql_repair_agent",

            "blocked":
                "answer_agent",
        }
    )

    graph.add_edge(
        "sql_repair_agent",
        "sql_validator_agent"
    )

    graph.add_conditional_edges(
        "sql_executor_agent",
        execution_router,
        {
            "repair":
                "sql_repair_agent",

            "answer":
                "answer_agent",

            "blocked":
                "answer_agent",
        }
    )

    graph.add_edge(
        "answer_agent",
        END
    )

    return graph.compile()