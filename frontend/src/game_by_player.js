import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";

function PlayerGameDetails() {
	const [gameDetails, setGameDetails] = useState(null);
	const { id_player, id_game } = useParams();
	const navigate = useNavigate();
	const token = localStorage.getItem("token");

	useEffect(() => {
		const fetchGameDetails = async () => {
			try {
				const url = `http://localhost:8000/results/player/${id_player}/game/${id_game}/token=${token}`;
				const response = await fetch(url);

				if (!response.ok) {
					throw new Error("Error al cargar los detalles del juego");
				}

				const data = await response.json();
				setGameDetails(data);
			} catch (error) {
				console.error("Fetch error:", error);
			}
		};

		fetchGameDetails();
	}, [id_player, id_game, token]);

	const handleDeleteGame = async () => {
		if (window.confirm("¿Estás seguro de que quieres borrar este juego?")) {
			try {
				const response = await fetch(
					`http://localhost:8000/results/${id_game}/delete/token=${token}`,
					{
						method: "DELETE",
					}
				);

				if (!response.ok) {
					throw new Error("Error al borrar el juego");
				}

				alert("Juego borrado con éxito");
				navigate("/menu/test"); // o la ruta que consideres adecuada
			} catch (error) {
				console.error("Delete error:", error);
			}
		}
	};

	const handleLogout = () => {
		localStorage.removeItem("token");
		navigate("/login");
	};

	const handlePlayerClick = (id_player) => {
		navigate(`/menu/player/${id_player}`);
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
				<h2>Detalles del Juego del Jugador</h2>
				{gameDetails ? (
					<div>
						<h3>{gameDetails.title}</h3>
						<img
							src={gameDetails.image}
							alt="Imagen del Test"
							className="img-fluid"
						/>
						<div className="mt-4">
							<h4>Preguntas y Respuestas:</h4>
							{gameDetails.questions.map((question) => (
								<div key={question.id} className="mb-4">
									<h5>{question.title}</h5>
									<img
										src={question.image}
										alt="Imagen de la Pregunta"
										className="img-fluid"
									/>
									<ul className="list-group">
										{question.answers.map((answer) => (
											<li
												key={answer.id}
												className={`list-group-item ${
													answer.isCorrect
														? "list-group-item-success"
														: ""
												}`}
											>
												{answer.title}
												{answer.isCorrect
													? " (Correcta)"
													: ""}
												{gameDetails.games
													.flatMap(
														(game) => game.results
													)
													.flatMap(
														(result) =>
															result.solutions
													)
													.some(
														(solution) =>
															solution.question_id ===
																question.id &&
															solution.answer_id ===
																answer.id
													)
													? " (Elegida)"
													: ""}
											</li>
										))}
									</ul>
								</div>
							))}
						</div>
						<div className="mt-4">
							<h4>Resultados:</h4>
							{gameDetails.games.map((game) => (
								<div key={game.id}>
									{game.results.map((result) => (
										<div
											key={result.id}
											className="card mb-3"
										>
											<div className="card-body">
												<h5
													className="card-title"
													onClick={() =>
														handlePlayerClick(
															result.player_id
														)
													}
												>
													{result.player_name}
												</h5>
												<p className="card-text">
													Puntuación: {result.score}
												</p>
											</div>
										</div>
									))}
								</div>
							))}
							<button
								className="btn btn-danger"
								onClick={handleDeleteGame}
							>
								Borrar Juego
							</button>
						</div>
					</div>
				) : (
					<p>Cargando detalles del juego...</p>
				)}
			</div>
		</div>
	);
}

export default PlayerGameDetails;
