import React, { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";

function MenuJugadores() {
	const [jugadores, setJugadores] = useState([]);
	const [searchTerm, setSearchTerm] = useState("");
	const navigate = useNavigate();
	const token = localStorage.getItem("token");

	const fetchJugadores = useCallback(async () => {
		try {
			const response = await fetch(
				`http://localhost:8000/player/all/token=${token}`
			);
			if (!response.ok) {
				throw new Error("Error al cargar los jugadores");
			}
			const data = await response.json();
			setJugadores(data);
		} catch (error) {
			console.error(error.message);
		}
	}, [token]);

	useEffect(() => {
		fetchJugadores();
	}, [fetchJugadores]);

	const handleInfo = (playerId) => {
		navigate(`/menu/player/${playerId}`);
	};

	const handleDelete = async (playerId) => {
		if (window.confirm("¿Estás seguro de eliminar al jugador?")) {
			try {
				const response = await fetch(
					`http://localhost:8000/player/${playerId}/delete/token=${token}`,
					{
						method: "DELETE",
					}
				);
				if (!response.ok) {
					throw new Error("Error al eliminar al jugador");
				}
				fetchJugadores();
			} catch (error) {
				console.error(error.message);
			}
		}
	};

	const handleSearchChange = (e) => {
		setSearchTerm(e.target.value.toLowerCase());
	};

	const filteredJugadores = jugadores.filter((jugador) =>
		jugador.name.toLowerCase().includes(searchTerm)
	);

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
					<input
						type="text"
						className="form-control mb-3"
						placeholder="Buscar Jugador"
						value={searchTerm}
						onChange={handleSearchChange}
					/>
				</aside>

				<section className="col-md-9">
					<div className="row">
						{filteredJugadores.map((jugador) => (
							<div key={jugador.id} className="col-md-4 mb-4">
								<div className="card">
									<div className="card-body">
										<h5 className="card-title">
											{jugador.name}
										</h5>
										<p className="card-text">
											Creado:{" "}
											{new Date(
												jugador.createdAt
											).toLocaleDateString()}
										</p>
										<div className="d-flex">
											<button
												className="btn btn-info"
												onClick={() =>
													handleInfo(jugador.id)
												}
											>
												Info
											</button>
											<button
												className="btn btn-danger ms-auto"
												onClick={() =>
													handleDelete(jugador.id)
												}
											>
												Eliminar
											</button>
										</div>
									</div>
								</div>
							</div>
						))}
					</div>
				</section>
			</div>
		</div>
	);
}

export default MenuJugadores;
