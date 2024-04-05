function EndScreen({ data, ws }) {
	const handleSave = () => {
		ws.send("SAVE");
	};
	const handleClose = () => {
		ws.send("CLOSE");
	};

	return (
		<div>
			<h2>Fin del Juego</h2>
			{/* Muestra los resultados finales aquí */}
			<button onClick={handleSave}>Guardar Resultados</button>
			<button onClick={handleClose}>Cerrar</button>
		</div>
	);
}

export default EndScreen;
