import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

function CreateTest() {
	const initialTestState = {
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
	};

	const [formData, setFormData] = useState(initialTestState);

	const navigate = useNavigate();
	const token = localStorage.getItem("token");

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
		if (!formData.title.trim() || !formData.image.trim()) return false;

		for (const question of formData.questions) {
			if (
				!question.title.trim() ||
				!question.image.trim() ||
				question.allocatedTime <= 10 ||
				question.weight <= 0 ||
				question.answers.length < 2 ||
				!question.answers.some(
					(answer) => answer.isCorrect && answer.title.trim()
				)
			) {
				return false;
			}
		}

		return true;
	};

	const handleSave = async () => {
		if (!isValidForm()) {
			alert("Por favor, rellena todos los campos correctamente.");
			return;
		}

		try {
			const response = await fetch(
				`http://localhost:8000/test/create/token=${token}`,
				{
					method: "PUT",
					headers: {
						"Content-Type": "application/json",
					},
					body: JSON.stringify(formData),
				}
			);

			if (!response.ok) {
				throw new Error("Error al crear el test");
			}

			alert("Test creado con éxito");
			navigate("/menu/test");
		} catch (error) {
			console.error("Error al crear el test:", error);
			alert("No se pudo crear el test: " + error.message);
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
									min="10"
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
									min="1"
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

export default CreateTest;
