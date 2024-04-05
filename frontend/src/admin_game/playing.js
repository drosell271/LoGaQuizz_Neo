function PlayingScreen({ data, ws }) {
	const handleSkip = () => {
		ws.send("SKIP");
	};

	return (
		<div>
			<h2>
				Jugando: {data.question_current + 1}/{data.question_total}
			</h2>
			{/* Renderiza la pregunta y las respuestas aquí */}
			<button onClick={handleSkip}>Saltar a Resultados</button>
		</div>
	);
}

export default PlayingScreen;
