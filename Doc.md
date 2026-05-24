# NL-to-SQL Data Agent

## Architecture Design, Evaluation, and Iterative Improvements

---

# Executive Summary

This project implements a Natural Language-to-SQL (NL-to-SQL) system that enables users to query employee information using natural language instead of writing SQL manually.

The solution was developed using:

- Python
- LangGraph
- LangChain
- Ollama
- Llama 3.1
- SQLite

The primary objectives were:

- Generate accurate SQL from natural language
- Enforce department-level data access restrictions
- Prevent unsafe SQL execution
- Recover from SQL generation failures
- Evaluate and improve the system through systematic testing

Rather than relying solely on prompt engineering, the solution incorporates validation and repair mechanisms to improve reliability and ensure that mandatory security guardrails are always enforced.

---

# Problem Statement

The application allows users to ask questions about:

- Employees
- Certifications
- Salaries
- Bonuses
- Benefits

Examples:

```text
Who are the software engineers?

Which employees have AWS certification?

What is the average salary?

Who has the highest remaining benefits balance?
```

The system must:

1. Translate natural language into SQL
2. Execute SQL against a SQLite database
3. Return results to the user
4. Prevent access to data outside a selected department

---

# Database Overview

The solution uses a SQLite database containing three tables:

## Employee

Stores:

- Employee information
- Department
- Role
- Salary
- Bonus
- Employment start date

## Certification

Stores:

- Employee certifications
- Certification dates

## Benefits

Stores:

- Benefits package information
- Remaining benefit balances

### Relationships

```text
Employee.EmployeeId
        |
        +---- Certification.EmployeeId

Employee.EmployeeId
        |
        +---- Benefits.EmployeeId
```

---

# Mandatory Security Requirement

A key requirement of the assignment is department-level data isolation.

When the application starts, a department is randomly selected:

```text
Sales
Marketing
Engineering
```

Example:

```text
[INFO] Department selected: Engineering
```

Every generated query must contain:

```sql
Department = 'Engineering'
```

or the corresponding selected department.

This ensures that no query can access data belonging to other departments.

---

# Initial Architecture (Version 1)

The first implementation followed a straightforward NL-to-SQL workflow.

```text
User Question
        ↓
Schema Agent
        ↓
SQL Generation Agent
        ↓
SQL Validation
        ↓
SQL Execution
        ↓
Answer
```

## Components

### Schema Agent

Responsible for:

- Reading schema metadata from SQLite
- Providing table and column information to the LLM

### SQL Generation Agent

Responsible for:

- Translating natural language into SQL
- Applying department restrictions

### SQL Validator

Responsible for:

- Enforcing SELECT-only queries
- Blocking unsafe SQL operations
- Verifying department restrictions

### SQL Executor

Responsible for:

- Running validated SQL
- Returning results

---

# Evaluation Framework

To measure quality objectively, a benchmark dataset of 20 representative business questions was created.

The evaluation dataset covers:

- Employee lookup
- Certification queries
- Salary analytics
- Benefits analytics
- Date filtering
- Aggregations
- Multi-table joins

Examples:

```text
Who are the software engineers?

Which employees have AWS certification?

What is the average salary?

How many AWS certified employees are there?
```

---

# Evaluation Metrics

The system was evaluated across four dimensions.

| Metric | Description |
|----------|-------------|
| SQL Validity | Generated SQL is syntactically correct |
| Guardrail Compliance | Department restriction is always enforced |
| Execution Success | SQL executes successfully |
| Result Accuracy | Returned results match business intent |

---

# Initial Evaluation Results

## Performance Summary

```text
Correct: 12 / 20
Partial: 4 / 20
Failed: 4 / 20
```

### Approximate Metrics

| Metric | Score |
|----------|--------|
| SQL Validity | 90% |
| Guardrail Compliance | 95% |
| Execution Success | 85% |
| Result Accuracy | 65% |

---

# Root Cause Analysis

Evaluation identified several recurring failure patterns.

| Error Type | Example | Severity |
|------------|----------|----------|
| Semantic Matching Error | `CertificationName = 'AWS'` | High |
| Missing Guardrail | Department filter omitted | Critical |
| Schema Grounding Error | Wrong column ownership | High |
| Result Shape Error | Returned EmployeeId instead of Name | Medium |
| Execution Error | Invalid column reference | High |

## Example: Semantic Matching Error

Generated:

```sql
CertificationName = 'AWS'
```

Actual values:

```text
AWS Developer Associate
AWS Solutions Architect
```

Correct SQL:

```sql
CertificationName LIKE '%AWS%'
```

---

# Architecture Improvements

Based on evaluation findings, a more advanced architecture was implemented.

## Version 2 – Multi-Agent Architecture

```text
User Question
        ↓
Question Understanding Agent
        ↓
Schema Agent
        ↓
SQL Generation Agent
        ↓
SQL Validation Agent
        ↓
SQL Repair Agent
        ↓
SQL Validation Agent
        ↓
SQL Execution Agent
        ↓
Answer Agent
```

---

# New Components

## Question Understanding Agent

Added to perform:

- Intent classification
- Entity extraction
- Join detection
- Aggregation detection

Example:

Question:

```text
Which employees have AWS certification?
```

Output:

```json
{
  "intent":"certification_lookup",
  "entities":["AWS"],
  "needs_join":true
}
```

## SQL Repair Agent

Added to automatically repair invalid SQL before execution.

Example:

Validation Error:

```text
Missing department filter
```

Generated SQL:

```sql
SELECT *
FROM Employee
```

Repaired SQL:

```sql
SELECT *
FROM Employee
WHERE Department = 'Engineering'
```

---

# Second Evaluation Results

The new architecture was evaluated using the same benchmark.

## Performance Summary

```text
Correct: 8 / 20
Partial: 4 / 20
Failed: 8 / 20
```

### Approximate Metrics

| Metric | Score |
|----------|--------|
| SQL Validity | 70% |
| Guardrail Compliance | 100% |
| Execution Success | 65% |
| Result Accuracy | 55% |

---

# Findings

Although the new architecture improved guardrail compliance, it reduced overall accuracy.

The primary issue was the Question Understanding Agent.

It introduced:

- Intent leakage
- Entity contamination
- Incorrect business logic
- Additional latency

Example:

Question:

```text
Who are the software engineers?
```

Generated SQL incorrectly included:

```sql
AWS
Azure
CISSP
```

certification filters that were never requested by the user.

---

# Error Classification Summary

| Error Type | Example | Severity | Root Cause |
|------------|----------|----------|------------|
| Intent Leakage | AWS filters added to unrelated questions | High | Question Agent |
| Schema Hallucination | Department table invented | High | Weak schema grounding |
| Entity Grounding Failure | Helen Lee ignored | High | Entity extraction not enforced |
| Temporal Reasoning Error | LIKE '%2023%' | High | Weak date reasoning |
| Aggregation Failure | COUNT query returns names | High | Intent confusion |
| Business Semantics Error | Bonus mapped to Benefits | High | Incorrect schema understanding |
| Constraint Omission | Platinum filter omitted | High | Missing business constraints |
| Ranking Query Failure | Missing LIMIT 1 | Medium | Incomplete ranking logic |

---

# Engineering Decision

Evaluation demonstrated that the additional agent increased complexity without improving quality.

The Question Understanding Agent introduced:

- Extra LLM calls
- Higher latency
- Higher token usage
- Lower accuracy

As a result, the architecture was simplified.

This decision was driven by evaluation results rather than assumptions.

---

# Final Architecture

The final production architecture prioritizes:

- Simplicity
- Low latency
- Reliability
- Security

```text
User Question
        ↓
SQL Generation Agent
        ↓
SQL Validation Agent
        ↓
SQL Repair Agent
        ↓
SQL Validation Agent
        ↓
SQL Execution Agent
        ↓
Answer Agent
```

---

# Additional Optimizations

## Schema Caching

The database schema never changes during runtime.

Instead of retrieving schema metadata for every request:

```python
get_schema_text()
```

the schema is loaded once during startup:

```python
SCHEMA_CACHE = get_schema_text()
```

Benefits:

- Reduced latency
- Fewer SQLite calls
- Simpler architecture

---

## Improved Prompt Design

Prompt engineering was simplified based on evaluation findings.

Changes:

- Removed Question Understanding Agent output
- Reduced few-shot examples
- Added stronger schema grounding
- Added certification matching rules
- Added explicit department enforcement instructions

Benefits:

- Lower token usage
- Faster generation
- Reduced intent leakage

---

## Improved Validation

Validator improvements include:

### Department Guardrail Validation

Supports:

```sql
Department='Engineering'
```

```sql
Employee.Department='Engineering'
```

```sql
e.Department='Engineering'
```

### Allowed Table Validation

Only:

```text
Employee
Certification
Benefits
```

are permitted.

### Cross Join Prevention

Blocks:

```sql
CROSS JOIN
```

### Unsafe SQL Protection

Blocks:

```sql
INSERT
UPDATE
DELETE
DROP
ALTER
CREATE
```

---

# Final Performance(Evalution Result 3)

| Metric | Final Score |
|----------|----------|
| SQL Validity | 95% |
| Guardrail Compliance | 85%  |
| Execution Success | 95% |
| Result Accuracy | 73% |

---

# Key Lessons Learned

The most important lesson from this project is:

> More agents do not automatically produce better results.

The largest improvements came from:

- Better schema grounding
- Evaluation-driven iteration
- Strong guardrails
- SQL validation
- SQL repair
- Simpler architecture

The project demonstrated that systematic evaluation and error analysis are often more impactful than increasing architectural complexity.

---

# Future Improvements

Potential future enhancements include:

- Prompt caching
- SQL result caching
- Intent-specific prompting
- Fine-tuned NL-to-SQL models
- Observability dashboards
- Human feedback collection
- Reinforcement learning from validated SQL executions
- AgentOps and tracing instrumentation

---







