import random

from graph import build_graph

from config import (
    ALLOWED_DEPARTMENTS
)


def main():

    selected_department = random.choice(
        ALLOWED_DEPARTMENTS
    )

    print(
        f"[INFO] Department selected: "
        f"{selected_department}"
    )

    print(
        "[INFO] Type exit or quit to stop.\n"
    )

    app = build_graph()

    while True:

        question = input(
            "Ask a question: "
        ).strip()

        if question.lower() in [
            "exit",
            "quit"
        ]:
            break

        if not question:
            continue

        state = {

            "question": question,

            "selected_department":
                selected_department,

            "sql": None,

            "validation_error": None,

            "repair_count": 0,

            "headers": None,

            "rows": None,

            "answer": None,
        }

        try:

            result = app.invoke(
                state
            )

            print(
                "\n"
                + result["answer"]
                + "\n"
            )

        except Exception as e:

            print(
                f"\n[ERROR] {e}\n"
            )


if __name__ == "__main__":
    main()