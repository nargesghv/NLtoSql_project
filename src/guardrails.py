import re

BLOCKED_KEYWORDS = [
    "INSERT",
    "UPDATE",
    "DELETE",
    "DROP",
    "ALTER",
    "CREATE",
    "PRAGMA",
    "ATTACH",
    "DETACH",
    "REPLACE",
    "TRUNCATE"
]

ALLOWED_TABLES = {
    "Employee",
    "Certification",
    "Benefits"
}


def clean_sql(sql: str) -> str:
    sql = sql.strip()

    sql = sql.replace("```sql", "")
    sql = sql.replace("```", "")

    sql = sql.strip()

    return sql.rstrip(";") + ";"


def has_department_guardrail(
    sql: str,
    department: str
) -> bool:

    patterns = [

        rf"Department\s*=\s*'{department}'",

        rf"\w+\.Department\s*=\s*'{department}'",

        rf"Department\s*=\s*\"{department}\"",

        rf"\w+\.Department\s*=\s*\"{department}\"",
    ]

    for pattern in patterns:

        if re.search(
            pattern,
            sql,
            re.IGNORECASE
        ):
            return True

    return False


def contains_only_allowed_tables(
    sql: str
) -> tuple[bool, str]:

    matches = re.findall(
        r"(?:FROM|JOIN)\s+([A-Za-z_][A-Za-z0-9_]*)",
        sql,
        re.IGNORECASE
    )

    for table in matches:

        if table not in ALLOWED_TABLES:

            return (
                False,
                f"Unauthorized table: {table}"
            )

    return (
        True,
        "Tables valid"
    )


def validate_sql(
    sql: str,
    selected_department: str
) -> tuple[bool, str]:

    upper_sql = sql.upper()

    if not upper_sql.strip().startswith(
        "SELECT"
    ):
        return (
            False,
            "Only SELECT queries are allowed."
        )

    for keyword in BLOCKED_KEYWORDS:

        if re.search(
            rf"\b{keyword}\b",
            upper_sql
        ):
            return (
                False,
                f"Blocked keyword: {keyword}"
            )

    if "EMPLOYEE" not in upper_sql:
        return (
            False,
            "Employee table must be used."
        )

    if not has_department_guardrail(
        sql,
        selected_department
    ):
        return (
            False,
            f"Missing department filter: {selected_department}"
        )

    ok, message = contains_only_allowed_tables(
        sql
    )

    if not ok:
        return (
            False,
            message
        )

    if "CROSS JOIN" in upper_sql:
        return (
            False,
            "Cross joins are not allowed."
        )

    return (
        True,
        "SQL validation passed."
    )