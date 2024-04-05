function ResultsScreen({ data, ws }) {
	const handleNext = () => {
		ws.send("NEXT");
	};
	const handleEnd = () => {
		ws.send("END");
	};

	return (
		<div>
			<h2>Resultados de la Pregunta</h2>
			{/* Muestra los resultados aquí */}
			<button onClick={handleNext}>Siguiente Pregunta</button>
			<button onClick={handleEnd}>Finalizar Partida</button>
		</div>
	);
}

export default ResultsScreen;
