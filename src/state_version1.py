from typing import TypedDict, Optional, List, Any, Dict


class NL2SQLState(TypedDict):
    # user input
    question: str
    selected_department: str

    # question understanding
    question_analysis: Optional[Dict]

    # schema
    schema: Optional[str]

    # generated sql
    sql: Optional[str]

    # validation
    validation_error: Optional[str]
    repair_count: int

    # execution results
    headers: Optional[List[str]]
    rows: Optional[List[Any]]

    # final answer
    answer: Optional[str]