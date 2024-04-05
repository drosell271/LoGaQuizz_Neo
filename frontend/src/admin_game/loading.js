import React from "react";

function LoadingScreen({ data }) {
	return (
		<div className="loading-screen">
			<h2>Cargando...</h2>
			<p>La siguiente pregunta comenzará en {data.countdown} segundos.</p>
		</div>
	);
}

export default LoadingScreen;
