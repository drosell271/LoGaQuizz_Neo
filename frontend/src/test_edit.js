import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";

function EditTest() {
	const [formData, setFormData] = useState({
		title: "",
		image: "",
		questions: [
			{
				title: "",
				image: "",
				allocatedTime: 30,
				weight: 1,
				answers: [
					{ title: "", isCorrect: false },
					{ title: "", isCorrect: false },
				],
			},
		],
	});

	const navigate = useNavigate();
	const { id } = useParams();
	const token = localStorage.getItem("token"); // Asegúrate de obtener el token como sea necesario para tu aplicación.

	useEffect(() => {
		async function fetchTestDetails() {
			try {
				const response = await fetch(
					`http://localhost:8000/test/${id}/view/token=${token}`
				);
				if (!response.ok) {
					throw new Error("Network response was not ok.");
				}
				const data = await response.json();
				setFormData(data);
			} catch (error) {
				console.error("Error:", error);
				navigate("/error"); // Asumiendo que tienes una ruta de error configurada
			}
		}

		fetchTestDetails();
	}, [id, token, navigate]);

	const updateFormField = (field, value) => {
		setFormData({ ...formData, [field]: value });
	};

	const updateQuestion = (questionIndex, field, value) => {
		const updatedQuestions = formData.questions.map((question, index) =>
			index === questionIndex ? { ...question, [field]: value } : question
		);
		setFormData({ ...formData, questions: updatedQuestions });
	};

	const updateAnswer = (questionIndex, answerIndex, field, value) => {
		const updatedQuestions = formData.questions.map((question, qIndex) =>
			qIndex === questionIndex
				? {
						...question,
						answers: question.answers.map((answer, aIndex) =>
							aIndex === answerIndex
								? { ...answer, [field]: value }
								: answer
						),
				  }
				: question
		);
		setFormData({ ...formData, questions: updatedQuestions });
	};

	const addQuestion = () => {
		setFormData({
			...formData,
			questions: [
				...formData.questions,
				{
					title: "",
					image: "",
					allocatedTime: 30,
					weight: 1,
					answers: [
						{ title: "", isCorrect: false },
						{ title: "", isCorrect: false },
					],
				},
			],
		});
	};

	const removeQuestion = (questionIndex) => {
		const updatedQuestions = formData.questions.filter(
			(_, index) => index !== questionIndex
		);
		setFormData({ ...formData, questions: updatedQuestions });
	};

	const addAnswer = (questionIndex) => {
		const updatedQuestions = formData.questions.map((question, qIndex) =>
			qIndex === questionIndex
				? {
						...question,
						answers: [
							...question.answers,
							{ title: "", isCorrect: false },
						],
				  }
				: question
		);
		setFormData({ ...formData, questions: updatedQuestions });
	};

	const removeAnswer = (questionIndex, answerIndex) => {
		const updatedQuestions = formData.questions.map((question, qIndex) =>
			qIndex === questionIndex
				? {
						...question,
						answers: question.answers.filter(
							(_, aIndex) => aIndex !== answerIndex
						),
				  }
				: question
		);
		setFormData({ ...formData, questions: updatedQuestions });
	};

	const setCorrectAnswer = (questionIndex, answerIndex) => {
		const updatedQuestions = formData.questions.map((question, qIndex) =>
			qIndex === questionIndex
				? {
						...question,
						answers: question.answers.map((answer, aIndex) => ({
							...answer,
							isCorrect: aIndex === answerIndex,
						})),
				  }
				: question
		);
		setFormData({ ...formData, questions: updatedQuestions });
	};

	const isValidForm = () => {
		// Comprueba si el título del test y la imagen están llenos
		if (!formData.title.trim() || !formData.image.trim()) {
			return false;
		}

		// Comprueba cada pregunta
		for (const question of formData.questions) {
			// Comprueba que el título y la imagen de la pregunta no estén vacíos
			if (!question.title.trim() || !question.image.trim()) {
				return false;
			}

			// Comprueba que el tiempo asignado y el peso sean mayores que cero
			if (question.allocatedTime <= 10 || question.weight <= 0) {
				return false;
			}

			// Comprueba que haya al menos dos respuestas
			if (question.answers.length < 2) {
				return false;
			}

			// Comprueba que al menos una respuesta sea correcta y no esté vacía
			let correctAnswerFound = false;
			for (const answer of question.answers) {
				if (answer.isCorrect && answer.title.trim()) {
					correctAnswerFound = true;
				}
			}
			if (!correctAnswerFound) {
				return false;
			}
		}

		// Si todas las comprobaciones anteriores son correctas, el formulario es válido
		return true;
	};

	const handleSave = async () => {
		if (!isValidForm()) {
			alert("Por favor, rellena todos los campos.");
			return;
		}

		try {
			const response = await fetch(
				`http://localhost:8000/test/${id}/edit/token=${token}`,
				{
					method: "POST",
					headers: {
						"Content-Type": "application/json",
					},
					body: JSON.stringify(formData),
				}
			);

			if (!response.ok) {
				throw new Error("Error al guardar el test");
			}

			alert("Test guardado con éxito");
			navigate("/menu/test"); // O donde quieras redirigir al usuario después de guardar
		} catch (error) {
			console.error("Error al guardar el test:", error);
		}
	};

	const handleCancel = () => {
		navigate("/menu/test");
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
				<button
					className="btn btn-link"
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
						onClick={handleSave}
						disabled={!isValidForm()}
					>
						Guardar
					</button>
					<button
						className="btn btn-secondary mb-3"
						onClick={handleCancel}
					>
						Cancelar
					</button>
				</aside>

				<section className="col-md-9">
					<div className="card p-3">
						<input
							type="text"
							className="form-control mb-3"
							value={formData.title}
							onChange={(e) =>
								updateFormField("title", e.target.value)
							}
							placeholder="Título del Test"
						/>
						<input
							type="text"
							className="form-control mb-3"
							value={formData.image}
							onChange={(e) =>
								updateFormField("image", e.target.value)
							}
							placeholder="URL de la Imagen"
						/>

						<h6>Preguntas:</h6>
						{formData.questions.map((question, qIndex) => (
							<div key={qIndex} className="border p-3 mb-3">
								<input
									type="text"
									className="form-control mb-2"
									value={question.title}
									onChange={(e) =>
										updateQuestion(
											qIndex,
											"title",
											e.target.value
										)
									}
									placeholder="Título de la Pregunta"
								/>
								<input
									type="text"
									className="form-control mb-2"
									value={question.image}
									onChange={(e) =>
										updateQuestion(
											qIndex,
											"image",
											e.target.value
										)
									}
									placeholder="URL de la Imagen de la Pregunta"
								/>
								<input
									type="number"
									className="form-control mb-2"
									value={question.allocatedTime}
									onChange={(e) =>
										updateQuestion(
											qIndex,
											"allocatedTime",
											e.target.value
										)
									}
									placeholder="Tiempo asignado (segundos)"
								/>
								<input
									type="number"
									className="form-control mb-2"
									value={question.weight}
									onChange={(e) =>
										updateQuestion(
											qIndex,
											"weight",
											e.target.value
										)
									}
									placeholder="Peso de la pregunta"
								/>

								{question.answers.map((answer, aIndex) => (
									<div
										key={aIndex}
										className="d-flex align-items-center mb-2"
									>
										<input
											type="text"
											className="form-control me-2"
											value={answer.title}
											onChange={(e) =>
												updateAnswer(
													qIndex,
													aIndex,
													"title",
													e.target.value
												)
											}
											placeholder="Texto de la Respuesta"
										/>
										<input
											type="checkbox"
											className="form-check-input me-2"
											checked={answer.isCorrect}
											onChange={() =>
												setCorrectAnswer(qIndex, aIndex)
											}
										/>
										<label className="form-check-label">
											Correcta
										</label>
										{question.answers.length > 2 && (
											<button
												onClick={() =>
													removeAnswer(qIndex, aIndex)
												}
												className="btn btn-danger ms-2"
											>
												Eliminar Respuesta
											</button>
										)}
									</div>
								))}
								{question.answers.length < 4 && (
									<button
										onClick={() => addAnswer(qIndex)}
										className="btn btn-primary mb-2"
									>
										Añadir Respuesta
									</button>
								)}
								{formData.questions.length > 1 && (
									<button
										onClick={() => removeQuestion(qIndex)}
										className="btn btn-danger"
									>
										Eliminar Pregunta
									</button>
								)}
							</div>
						))}
						<button
							onClick={addQuestion}
							className="btn btn-success"
						>
							Añadir Pregunta
						</button>
					</div>
				</section>
			</div>
		</div>
	);
}

export default EditTest;
