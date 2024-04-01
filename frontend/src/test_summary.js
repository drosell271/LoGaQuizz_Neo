import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";

function TestResults() {
	const [testResults, setTestResults] = useState([]);
	const navigate = useNavigate();
	const { id } = useParams(); // id del test
	const token = localStorage.getItem("token");

	useEffect(() => {
		fetchTestResults();
	}, [id, token]);

	const fetchTestResults = async () => {
		try {
			const response = await fetch(
				`http://localhost:8000/results/test/${id}/all/token=${token}`
			);
			if (!response.ok) {
				throw new Error("Network response was not ok");
			}
			const data = await response.json();
			setTestResults(data.games || []);
		} catch (error) {
			console.error("Error:", error);
		}
	};

	const handleDelete = async (gameId) => {
		if (window.confirm("¿Estás seguro de querer eliminar este juego?")) {
			try {
				const response = await fetch(
					`http://localhost:8000/results/${gameId}/delete/token=${token}`,
					{
						method: "DELETE",
					}
				);
				if (!response.ok) {
					throw new Error("Error al eliminar el juego");
				}
				alert("Juego eliminado con éxito");
				fetchTestResults(); // Recargar los resultados
			} catch (error) {
				console.error("Error:", error);
				alert("Error al eliminar el juego: " + error.message);
			}
		}
	};

	const handleMoreClick = (gameId) => {
		navigate(`/menu/test/${id}/game/${gameId}`);
	};

	const handleLogout = () => {
		localStorage.removeItem("token");
		navigate("/login");
	};

	return (
		<div className="container-fluid">
			<nav className="navbar navbar-expand-lg navbar-light bg-light">
				<button
					className="btn btn-link"
					onClick={() => navigate("/menu/test")}
				>
					Test
				</button>
				<button
					className="btn btn-link"
					onClick={() => navigate("/menu/players")}
				>
					Jugadores
				</button>
				<button
					className="btn btn-link"
					onClick={() => navigate("/menu/games")}
				>
					Juegos
				</button>
				<button className="btn btn-link" onClick={handleLogout}>
					Logout
				</button>
			</nav>

			<div className="container mt-4">
				<h2>Resultados del Test</h2>
				<div className="row">
					{testResults.map((game) => (
						<div key={game.id} className="col-md-4 mb-3">
							<div className="card h-100">
								<div className="card-body">
									<h5 className="card-title">
										Jugado:{" "}
										{new Date(
											game.playedAt
										).toLocaleDateString()}
									</h5>
									<p className="card-text">
										Número de jugadores: {game.players}
									</p>
									<button
										className="btn btn-primary mb-2"
										onClick={() => handleMoreClick(game.id)}
									>
										Más
									</button>
									<button
										className="btn btn-danger"
										onClick={() => handleDelete(game.id)}
									>
										Borrar
									</button>
								</div>
							</div>
						</div>
					))}
				</div>
			</div>
		</div>
	);
}

export default TestResults;
