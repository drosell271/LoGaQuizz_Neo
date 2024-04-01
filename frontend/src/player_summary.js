import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";

function PlayerResults() {
	const [results, setResults] = useState([]);
	const { id } = useParams();
	const navigate = useNavigate();
	const token = localStorage.getItem("token");

	useEffect(() => {
		async function fetchResults() {
			try {
				const response = await fetch(
					`http://localhost:8000/results/player/${id}/all/token=${token}`
				);
				if (!response.ok) {
					throw new Error("Network response was not ok");
				}
				const data = await response.json();
				setResults(data);
			} catch (error) {
				console.error("Error:", error);
			}
		}

		fetchResults();
	}, [id, token]);

	const handleMoreClick = (playerId, gameId) => {
		navigate(`/menu/player/${playerId}/game/${gameId}`);
	};

	const handleLogout = () => {
		localStorage.removeItem("token");
		navigate("/login");
	};

	return (
		<div className="container-fluid">
			<nav className="navbar navbar-expand-lg navbar-light bg-light">
				<div className="container-fluid">
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
				</div>
			</nav>

			<div className="container mt-4">
				<h2>Resultados del Jugador</h2>
				<div className="row">
					{results.map((result) => (
						<div key={result.id} className="col-md-4 mb-3">
							<div className="card h-100">
								<img
									src={result.image}
									className="card-img-top"
									alt={`Test ${result.title}`}
								/>
								<div className="card-body">
									<h5 className="card-title">
										{result.title}
									</h5>
									{result.games.map((game) => (
										<div key={game.id}>
											<p className="card-text">
												Jugado:{" "}
												{new Date(
													game.playedAt
												).toLocaleDateString()}
											</p>
											{game.results.map((gameResult) => (
												<p
													key={gameResult.id}
													className="card-text"
												>
													Puntuación:{" "}
													{gameResult.score}
												</p>
											))}
											<button
												className="btn btn-primary"
												onClick={() =>
													handleMoreClick(id, game.id)
												}
											>
												Más
											</button>
										</div>
									))}
								</div>
							</div>
						</div>
					))}
				</div>
			</div>
		</div>
	);
}

export default PlayerResults;
