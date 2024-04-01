import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";

function GameDetail() {
	const [gameData, setGameData] = useState(null);
	const navigate = useNavigate();
	const { testid, gameid } = useParams();
	const token = localStorage.getItem("token");

	useEffect(() => {
		const fetchGameData = async () => {
			try {
				const response = await fetch(
					`http://localhost:8000/results/test/${testid}/game/${gameid}/token=${token}`
				);
				if (!response.ok) {
					throw new Error("Network response was not ok");
				}
				const data = await response.json();
				setGameData(data);
			} catch (error) {
				console.error("Error:", error);
			}
		};

		fetchGameData();
	}, [testid, gameid, token]);

	// Función para contar respuestas de jugadores por pregunta y respuesta
	const countAnswers = (questionId, answerId) => {
		if (!gameData || !gameData.games) return 0;

		return gameData.games.flatMap((game) =>
			game.results.flatMap((result) =>
				result.solutions.filter(
					(solution) =>
						solution.question_id === questionId &&
						solution.answer_id === answerId
				)
			)
		).length;
	};

	const handleDeleteGame = async () => {
		if (window.confirm("¿Estás seguro de querer eliminar este juego?")) {
			try {
				const response = await fetch(
					`http://localhost:8000/results/${gameid}/delete/token=${token}`,
					{
						method: "DELETE",
					}
				);
				if (!response.ok) {
					throw new Error("Error al eliminar el juego");
				}
				alert("Juego eliminado con éxito");
				navigate("/menu/test");
			} catch (error) {
				console.error("Error:", error);
				alert("Error al eliminar el juego: " + error.message);
			}
		}
	};

	const navigateToPlayer = (playerId) => {
		navigate(`/menu/player/${playerId}`);
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
				{gameData ? (
					<div>
						<h2>{gameData.title}</h2>
						<img
							src={gameData.image}
							alt={gameData.title}
							className="img-fluid"
						/>
						<h3>Preguntas:</h3>
						{gameData.questions.map((question) => (
							<div key={question.id} className="mb-3">
								<h4>{question.title}</h4>
								<img
									src={question.image}
									alt={question.title}
									className="img-fluid"
								/>
								<p>
									Tiempo asignado: {question.allocatedTime}s,
									Peso: {question.weight}
								</p>
								<ul>
									{question.answers.map((answer) => (
										<li
											key={answer.id}
											className={
												answer.isCorrect
													? "text-success"
													: ""
											}
										>
											{answer.title} - Respuestas:{" "}
											{countAnswers(
												question.id,
												answer.id
											)}
										</li>
									))}
								</ul>
							</div>
						))}
						<h3>Jugadores:</h3>
						{gameData.games.map((game) => (
							<div key={game.id} className="mb-3">
								{game.results.map((result) => (
									<p
										key={result.id}
										onClick={() =>
											navigateToPlayer(result.player_id)
										}
									>
										{result.player_name} - Puntuación:{" "}
										{result.score}
									</p>
								))}
							</div>
						))}
						<button
							className="btn btn-danger mt-3"
							onClick={handleDeleteGame}
						>
							Eliminar Juego
						</button>
					</div>
				) : (
					<p>Cargando datos del juego...</p>
				)}
			</div>
		</div>
	);
}

export default GameDetail;
