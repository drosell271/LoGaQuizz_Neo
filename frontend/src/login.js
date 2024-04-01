import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

function Login() {
	const [username, setUsername] = useState("");
	const [password, setPassword] = useState("");
	const [error, setError] = useState("");
	const navigate = useNavigate();

	const handleSubmit = async (e) => {
		e.preventDefault();
		setError("");

		try {
			const response = await fetch("http://localhost:8000/login", {
				method: "POST",
				headers: {
					"Content-Type": "application/json",
				},
				body: JSON.stringify({ username, password }),
			});

			const data = await response.json();

			if (response.ok) {
				localStorage.setItem("token", data.token);
				navigate("/menu/test"); // Redirige al usuario a /menu
			} else {
				setError(data.detail || "Error de autenticación"); // Muestra el mensaje de error
			}
		} catch (error) {
			setError("Error de Login");
		}
	};

	return (
		<div className="vh-100 d-flex flex-column justify-content-center align-items-center bg-light">
			<div className="card p-4 mb-2" style={{ maxWidth: "400px" }}>
				{" "}
				{/* Ajusta el margen inferior como sea necesario */}
				<div className="card-body">
					<form onSubmit={handleSubmit}>
						<h3 className="card-title text-center mb-3">
							Iniciar Sesión
						</h3>

						{/* Campo Usuario */}
						<div className="mb-3">
							<label htmlFor="username" className="form-label">
								Usuario
							</label>
							<input
								type="text"
								className="form-control"
								id="username"
								value={username}
								onChange={(e) => setUsername(e.target.value)}
								placeholder="Usuario"
							/>
						</div>

						{/* Campo Contraseña */}
						<div className="mb-3">
							<label htmlFor="password" className="form-label">
								Contraseña
							</label>
							<input
								type="password"
								className="form-control"
								id="password"
								value={password}
								onChange={(e) => setPassword(e.target.value)}
								placeholder="Contraseña"
							/>
						</div>

						<button type="submit" className="btn btn-primary w-100">
							Iniciar Sesión
						</button>
					</form>
				</div>
			</div>
			{error && (
				<div
					className="alert alert-danger"
					style={{ maxWidth: "400px" }}
				>
					{error}
				</div>
			)}
		</div>
	);
}

export default Login;
