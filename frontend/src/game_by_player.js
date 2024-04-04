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
				console.log(data);
				setGameDetails(data);
			} catch (error) {
				console.error("Fetch error:", error);
			}
		};

		fetchGameDetails();
	}, [id_player, id_game, token]);

	const handgleReturn = () => {
		navigate(-1);
	};

	return (
		<div className="container-fluid">
			{""}
			<nav className="navbar navbar-expand-lg navbar-light bg-light mb-4">
				<a className="navbar-brand" href="#">
					<img
						src={`${process.env.PUBLIC_URL}/logo.png`}
						alt="Logo"
						height="30"
					/>
				</a>
				<div className="navbar-nav">
					<a
						href="#"
						onClick={() => navigate("/menu/test")}
						className="nav-link"
					>
						Test
					</a>
					<a
						href="#"
						onClick={() => navigate("/menu/players")}
						className="nav-link"
					>
						Jugadores
					</a>
				</div>
				<button
					className="btn btn-danger ms-auto"
					onClick={() => {
						localStorage.removeItem("token");
						navigate("/login");
					}}
				>
					Logout
				</button>
			</nav>

			<div className="row">
				<aside className="col-md-2 d-flex flex-column">
					<button
						className="btn btn-secondary mb-3"
						onClick={handgleReturn}
					>
						Volver
					</button>
				</aside>
				<section className="col-md-10">
					{gameDetails ? (
						<>
							<div className="mb-4">
								<h1>{gameDetails.title}</h1>
								<img
									src={
										gameDetails.image ||
										`${process.env.PUBLIC_URL}/default-banner.png`
									}
									alt="Imagen del Test"
									className="img-fluid"
									style={{
										maxHeight: "200px",
										objectFit: "cover",
										width: "100%",
									}}
									onError={(e) => {
										e.target.onerror = null;
										e.target.src = `${process.env.PUBLIC_URL}/default-banner.png`;
									}}
								/>
							</div>
							<div>
								<h4>
									Detalles del Juego del Jugador:{" "}
									<strong>
										{
											gameDetails.games[0].results[0]
												.player_name
										}
									</strong>
								</h4>
								{gameDetails.questions &&
									gameDetails.questions.map(
										(question, index) => (
											<div
												key={index}
												className="card mb-3"
												style={{ maxWidth: "540px" }}
											>
												<div className="row g-0">
													{question.image && (
														<div className="col-md-4">
															<div
																className="card-img-top rounded-start h-100"
																style={{
																	backgroundImage: `url(${
																		question.image ||
																		`${process.env.PUBLIC_URL}/default-question-image.png`
																	}), url(${
																		process
																			.env
																			.PUBLIC_URL
																	}/default-banner.png)`,
																	backgroundSize:
																		"cover",
																	backgroundPosition:
																		"center",
																	borderTopLeftRadius:
																		"10px",
																	borderBottomLeftRadius:
																		"10px",
																}}
															></div>
														</div>
													)}
													<div className="col-md-8">
														<div className="card-body">
															<h5 className="card-title">
																{question.title}
															</h5>
															<ul className="list-group list-group-flush">
																{question.answers.map(
																	(
																		answer
																	) => {
																		const isCorrectAnswer =
																			answer.isCorrect;
																		const isAnsweredByUser =
																			gameDetails &&
																			gameDetails.games &&
																			gameDetails
																				.games
																				.length >
																				0 &&
																			gameDetails
																				.games[0]
																				.results &&
																			gameDetails
																				.games[0]
																				.results
																				.length >
																				0 &&
																			gameDetails
																				.games[0]
																				.results[0]
																				.solutions &&
																			gameDetails.games[0].results[0].solutions.some(
																				(
																					solution
																				) =>
																					solution.question_id ===
																						question.id &&
																					solution.answer_id ===
																						answer.id
																			);

																		return (
																			<li
																				key={
																					answer.id
																				}
																				className={`list-group-item ${
																					isCorrectAnswer
																						? "text-success"
																						: ""
																				}`}
																				style={{
																					textDecoration:
																						isAnsweredByUser
																							? "underline"
																							: "none",
																				}}
																			>
																				{isAnsweredByUser && (
																					<strong>
																						{
																							answer.title
																						}
																					</strong>
																				)}
																				{!isAnsweredByUser &&
																					answer.title}
																				{isCorrectAnswer &&
																					" (Correcta)"}
																			</li>
																		);
																	}
																)}
															</ul>
														</div>
													</div>
												</div>
											</div>
										)
									)}
								<div className="mt-4">
									<h4>Resultados:</h4>
									{gameDetails.games.map((game) => (
										<div key={game.id}>
											{game.results.map((result) => (
												<div
													key={result.id}
													className="card mb-3"
													style={{
														maxWidth: "540px",
													}}
												>
													<div className="card-body">
														<h5 className="card-title">
															{result.player_name}
														</h5>
														<p className="card-text">
															Puntuación:{" "}
															<strong>
																{result.score}
															</strong>
														</p>
													</div>
												</div>
											))}
										</div>
									))}
								</div>
							</div>
						</>
					) : (
						<p>Cargando detalles del juego...</p>
					)}
				</section>
			</div>
		</div>
	);
}

export default PlayerGameDetails;
