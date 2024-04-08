import React from "react";

function PlayingScreen({ data, ws }) {
	const questionInfo = data.question[0]; // Asumiendo que 'data.question' es un array con un elemento que contiene las preguntas y sus respuestas.
	const colors = ["#FF7043", "#FFCA28", "#29B6F6", "#66BB6A"];

	const handleSubmit = (answerId) => {
		const response = {
			question_id: questionInfo.question_id,
			answer_id: answerId,
		};

		if (ws && ws.readyState === WebSocket.OPEN) {
			ws.send(JSON.stringify(response));
		} else {
			console.error("WebSocket no está abierto.");
		}
	};

	return (
		<div className="container-fluid h-100 justify-content-center align-items-center flex-column">
			<div className="row h-50">
				{questionInfo.question_answers.map((answer, index) => (
					<div className="col-6 p-2" key={answer.answers_id}>
						<button
							className="btn w-100 h-100"
							style={{
								backgroundColor: colors[index % colors.length],
								height: `100px`, // Ajusta la altura aquí
							}}
							onClick={() => handleSubmit(answer.answers_id)}
						>
							{answer.answers_title}
						</button>
					</div>
				))}
			</div>
		</div>
	);
}

export default PlayingScreen;
