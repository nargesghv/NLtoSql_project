from typing import TypedDict, Optional, List, Any

class NL2SQLState(TypedDict):

    question: str

    selected_department: str

    sql: Optional[str]

    validation_error: Optional[str]

    repair_count: int

    headers: Optional[List[str]]

    rows: Optional[List[Any]]

    answer: Optional[str]