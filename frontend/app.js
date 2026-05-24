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
            "https://769f-142-114-87-87.ngrok-free.app/ask",
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
