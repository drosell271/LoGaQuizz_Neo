import React, { useState, useEffect, useCallback } from "react";
import { useParams, useNavigate } from "react-router-dom";

function DetalleTest() {
	const [test, setTest] = useState(null);
	const navigate = useNavigate();
	const { id } = useParams();
	const token = localStorage.getItem("token");

	const fetchTest = useCallback(async () => {
		try {
			const response = await fetch(
				`http://localhost:8000/test/${id}/view/token=${token}`
			);
			if (!response.ok) {
				throw new Error("Error al cargar el test");
			}
			const data = await response.json();
			setTest(data);
		} catch (error) {
			console.error(error.message);
		}
	}, [id, token]);

	useEffect(() => {
		fetchTest();
	}, [fetchTest]);

	const handleEdit = () => {
		navigate(`/menu/test/${id}/edit`);
	};

	const handleViewGames = () => {
		navigate(`/menu/test/${id}/games`);
	};

	const handleArchive = async () => {
		try {
			const response = await fetch(
				`http://localhost:8000/test/${id}/archive/token=${token}`,
				{
					method: "POST",
				}
			);
			if (!response.ok) {
				throw new Error("Error al archivar el test");
			}
			alert("Test archivado con éxito");
			navigate("/menu/test");
		} catch (error) {
			console.error(error.message);
		}
	};

	const handleDelete = async () => {
		if (window.confirm("¿Estás seguro de eliminar el test?")) {
			try {
				const response = await fetch(
					`http://localhost:8000/test/${id}/delete/token=${token}`,
					{
						method: "DELETE",
					}
				);
				if (!response.ok) {
					throw new Error("Error al eliminar el test");
				}
				alert("Test eliminado con éxito");
				navigate("/menu/test");
			} catch (error) {
				console.error(error.message);
			}
		}
	};

	const handlePlay = async () => {
		console.log("Jugar ha sido clickeado");
		console.log("test state", test, test.archiv);
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
						className="btn btn-success mb-3"
						onClick={handlePlay}
					>
						Jugar
					</button>
					<button
						className="btn btn-primary mb-3"
						onClick={handleEdit}
					>
						Editar
					</button>
					<button
						className="btn btn-primary mb-3"
						onClick={handleViewGames}
					>
						Juegos
					</button>
					<button
						className="btn btn-warning mb-3"
						onClick={handleArchive}
					>
						{test
							? test.archived
								? "Desarchivar"
								: "Archivar"
							: "Cargando..."}
					</button>
					<button
						className="btn btn-danger mb-3"
						onClick={handleDelete}
					>
						Eliminar
					</button>
				</aside>

				<section className="col-md-10">
					{test && (
						<div className="card">
							<img
								src={test.image}
								className="card-img-top img-fluid"
								style={{
									maxHeight: "150px",
									objectFit: "cover",
									width: "100%",
								}}
								alt={`Test ${test.title}`}
								onError={(e) => {
									e.target.onerror = null;
									e.target.src = `${process.env.PUBLIC_URL}/default-banner.png`;
								}}
							/>
							<div className="card-body">
								<h2 className="card-title">{test.title}</h2>
								<p className="card-text">
									Jugado: {test.played} veces
								</p>
								<p className="card-text">
									Creado:{" "}
									{new Date(
										test.createdAt
									).toLocaleDateString()}
								</p>
								<p className="card-text">
									Actualizado:{" "}
									{new Date(
										test.updatedAt
									).toLocaleDateString()}
								</p>
								<br />
								<h5 className="mt-4 mb-4">Preguntas:</h5>
								{test.questions.map((question, index) => (
									<div key={question.id} className="mb-3">
										{/* Fondo gris debajo de la imagen y del contenido */}
										<div
											className="d-flex"
											style={{
												backgroundColor: "#f8f9fa",
												borderRadius: "10px",
											}}
										>
											{/* Contenedor de la imagen con bordes redondeados */}
											<div
												className="me-3"
												style={{
													backgroundImage: `url(${question.image}), url(${process.env.PUBLIC_URL}/default-banner.png)`,
													backgroundSize: "cover",
													backgroundPosition:
														"center",
													borderTopLeftRadius: "10px",
													borderBottomLeftRadius:
														"10px",
													width: "100px", // Establece el ancho que desees para la imagen
													minHeight: "150px", // Ajusta esto según el contenido o la altura deseada
												}}
												onError={(e) =>
													(e.currentTarget.style.backgroundImage = `url(${process.env.PUBLIC_URL}/default-banner.png)`)
												}
											>
												{/* Este div permanece vacío; la imagen es un fondo */}
											</div>
											{/* Contenido de la pregunta */}
											<div
												style={{
													flex: 1,
													padding: "10px",
												}}
											>
												<div
													style={{
														fontWeight: "bold",
														marginBottom: "10px",
													}}
												>
													Pregunta {index + 1}{" "}
													{/* Contador de preguntas */}
												</div>
												<p>
													<strong>
														{question.title}
													</strong>
												</p>
												{/* Contenedor para Tiempo y Puntos al mismo nivel y alineados a la izquierda */}
												<div className="d-flex align-items-start">
													<p className="me-3">
														{" "}
														{/* Aumenta el espacio entre "Tiempo" y "Puntos" */}
														<strong>Tiempo:</strong>{" "}
														{question.allocatedTime}{" "}
														segundos
													</p>
													<p>
														<strong>Puntos:</strong>{" "}
														{question.weight}
													</p>
												</div>
												<ul>
													{question.answers.map(
														(answer) => (
															<li
																key={answer.id}
																className={
																	answer.isCorrect
																		? "text-success"
																		: ""
																}
															>
																{answer.title}{" "}
																{answer.isCorrect
																	? "(Correcta)"
																	: ""}
															</li>
														)
													)}
												</ul>
											</div>
										</div>
									</div>
								))}
							</div>
						</div>
					)}
				</section>
			</div>
		</div>
	);
}

export default DetalleTest;
