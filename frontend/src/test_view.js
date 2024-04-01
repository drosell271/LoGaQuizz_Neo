import React, { useState, useEffect, useCallback } from "react";
import { useParams, useNavigate } from "react-router-dom";

function DetalleTest() {
	const [test, setTest] = useState(null);
	const navigate = useNavigate();
	const { id } = useParams(); // Recibe algo como "id=1"
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

	return (
		<div className="container-fluid">
			{" "}
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
				<aside className="col-md-3">
					<button
						className="btn btn-primary mb-3"
						onClick={handleEdit}
					>
						Editar
					</button>
					<button
						className="btn btn-secondary mb-3"
						onClick={handleViewGames}
					>
						Ver Juegos
					</button>
					<button
						className="btn btn-warning mb-3"
						onClick={handleArchive}
					>
						Archivar
					</button>
					<button
						className="btn btn-danger mb-3"
						onClick={handleDelete}
					>
						Eliminar
					</button>
				</aside>

				<section className="col-md-9">
					{test && (
						<div className="card">
							<img
								src={test.image}
								className="card-img-top"
								alt={`Test ${test.title}`}
							/>
							<div className="card-body">
								<h5 className="card-title">{test.title}</h5>
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

								<h6>Preguntas:</h6>
								{test.questions.map((question) => (
									<div key={question.id} className="mb-3">
										<p>
											<strong>Título:</strong>{" "}
											{question.title}
										</p>
										<p>
											<strong>Tiempo Asignado:</strong>{" "}
											{question.allocatedTime} segundos
										</p>
										<p>
											<strong>Valor:</strong>{" "}
											{question.weight}
										</p>
										<img
											src={question.image}
											alt={`Pregunta ${question.title}`}
											className="img-fluid mb-2"
										/>
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
													{answer.title}{" "}
													{answer.isCorrect
														? "(Correcta)"
														: ""}
												</li>
											))}
										</ul>
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
