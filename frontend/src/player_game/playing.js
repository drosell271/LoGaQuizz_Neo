import React from "react";

function PlayingScreen({ data, ws }) {
	const questionInfo = data.question[0]; // Asumiendo que 'data.question' es un array con un elemento que contiene las preguntas y sus respuestas.
	const colors = ["#FF7043", "#FFCA28", "#29B6F6", "#66BB6A"];
	const [responsed, setResponsed] = React.useState(false);
	const handleSubmit = (answerId) => {
		const response = {
			question_id: questionInfo.question_id,
			answer_id: answerId,
		};

		if (ws && ws.readyState === WebSocket.OPEN) {
			ws.send(JSON.stringify(response));
			setResponsed(true);
		} else {
			console.error("WebSocket no está abierto.");
		}
	};

	return (
		<div>
			{responsed ? (
				<div
					className="vh-100 d-flex justify-content-center align-items-center flex-column"
					style={{ fontSize: "30px", textAlign: "center" }}
				>
					{" "}
					Ya has respondido
				</div>
			) : (
				<div className="container-fluid h-100 d-flex flex-wrap align-items-stretch justify-content-center">
					{questionInfo.question_answers.map((answer, index) => (
						<div
							className="col-6 px-2 py-2"
							key={answer.answers_id}
						>
							{" "}
							{/* Añade padding en lugar de margen a las columnas */}
							<button
								className="btn w-100 h-100"
								style={{
									backgroundColor:
										colors[index % colors.length],
									fontSize: "1.5em", // Tamaño de fuente grande para facilidad de lectura
									minHeight: "40vh", // Ajuste la altura mínima para cada botón
								}}
								onClick={() => handleSubmit(answer.answers_id)}
							>
								{answer.answers_title}
							</button>
						</div>
					))}
				</div>
			)}
		</div>
	);
}

export default PlayingScreen;
