import React from "react";

function EndScreen({ data }) {
	return (
		<div className="vh-100 d-flex justify-content-center align-items-center flex-column">
			<h1 className="mb-3">Fin del Juego</h1>
			<h2 className="mb-3">{data.score} Puntos</h2>
		</div>
	);
}

export default EndScreen;
