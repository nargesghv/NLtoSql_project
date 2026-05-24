async function askQuestion() {

    const question =
        document.getElementById(
            "question"
        ).value;

    const answerDiv =
        document.getElementById(
            "answer"
        );

    answerDiv.innerHTML =
        "Thinking...";

    const response =
        await fetch(
            "http://localhost:8000/ask",
            {
                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body: JSON.stringify({
                    question
                })
            }
        );

    const data =
        await response.json();

    answerDiv.innerHTML =
        data.answer;
}