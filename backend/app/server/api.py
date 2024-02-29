from fastapi import FastAPI, Response, Request, HTTPException, WebSocket
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import random
from datetime import datetime
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from typing import List, Optional, Literal

from .db_config import Test, Question, Answer, Game, Result, Player, Solution

ADMIN_USER = "admin"
ADMIN_PASSWORD = "1234"

app = FastAPI()

ADMIN_TOKEN = None
PLAYERS = {}

engine = create_engine('sqlite:///app/db/local.db')
Session = sessionmaker(bind=engine)
session = Session()

# Modelos de los JSON de login
class JSON_Login(BaseModel):
	username: str
	password: Optional[str]

# Modelos de los JSON de entrada
class JSON_Solution_Input(BaseModel):
	question_id: int
	answer_id: int
	time: int

class JSON_Result_Input(BaseModel):
	player_id: int
	score: int
	solutions: List[JSON_Solution_Input]

class JSON_Game_Input(BaseModel):
	test_id: int
	results: List[JSON_Result_Input]

class JSON_Answer_Input(BaseModel):
	title: str
	isCorrect: bool

class JSON_Question_Input(BaseModel):
	title: str
	image: Optional[str]
	questionType: Literal['unica', 'multiple']
	allocatedTime: int
	weight: int
	answers: List[JSON_Answer_Input]

class JSON_Test_Input(BaseModel):
	title: str
	image: Optional[str]
	questions: List[JSON_Question_Input]

# Modelos de los JSON de salida
class JSON_Solution_Output(BaseModel):
	id: int
	result_id: int
	question_id: int
	answer_id: int
	time: int

class JSON_Result_Output(BaseModel):
	id: int
	player_id: int
	game_id: int
	score: int
	solutions: Optional[List[JSON_Solution_Output]]

class JSON_Game_Output(BaseModel):
	id: int
	test_id: int
	playedAt: datetime
	players: int
	results: Optional[List[JSON_Result_Output]]

class JSON_Player_Output(BaseModel):
	id: int
	name: str
	createdAt: datetime
	results: Optional[List[JSON_Result_Output]]

class JSON_Answer_Output(BaseModel):
	id: int
	question_id: int
	title: str
	isCorrect: bool

class JSON_Question_Output(BaseModel):
	id: int
	test_id: int
	title: str
	image: Optional[str]
	questionType: Literal['unica', 'multiple']
	allocatedTime: int
	weight: int
	answers: Optional[List[JSON_Answer_Output]]

class JSON_Test_Output(BaseModel):
	id: int
	title: str
	image: Optional[str]
	archived: bool
	played: int
	createdAt: datetime
	updatedAt: datetime
	questions: Optional[List[JSON_Question_Output]]
	games: Optional[List[JSON_Game_Output]]

# FUNCIONES
async def get_session(request: Request):
	user = request.cookies.get("user")
	admin = request.cookies.get("admin")
	token = request.cookies.get("token")

	if user is None or token is None:
		raise HTTPException(status_code=401, detail="Sin datos de sesión")

	if admin and user == ADMIN_USER and token == ADMIN_TOKEN:
		return user, True

	elif user in PLAYERS and PLAYERS[user] == token:
		return user, False
		
	else:
		raise HTTPException(status_code=401, detail=f"Fallo de sesión")

async def count_games(test_id: int):
	count = session.query(func.count(Game.id)).filter(Game.test_id == test_id).scalar()
	if count is None:
		count = 0
	return count

async def count_players(game_id: int):
	count = session.query(func.count(Result.id)).filter(Result.game_id == game_id).scalar()
	if count is None:
		count = 0
	return count

# RUTAS DE SESION
@app.post("/login")
async def login(request: Request, input_data: JSON_Login, response: Response):
	if input_data.username is not None:
		temp_token = random.randint(100000000, 999999999)
		if input_data.username == ADMIN_USER:
			if input_data.password == ADMIN_PASSWORD:
				global ADMIN_TOKEN 
				ADMIN_TOKEN = str(temp_token)
				response.set_cookie(key="user", value=input_data.username, httponly=True)
				response.set_cookie(key="admin", value=True, httponly=True)
				response.set_cookie(key="token", value=temp_token)
				return {"detail": "Autenticación como administrador exitosa"}
			else:
				raise HTTPException(status_code=401, detail="Contraseña de admin incorrecta")
		else:
			if input_data.username in PLAYERS:
				return {"detail": "El nombre de jugador ya existe"}
			else:
				PLAYERS[input_data.username] = str(temp_token)
				response.set_cookie(key="user", value=input_data.username, httponly=True)
				response.set_cookie(key="admin", value=False, httponly=True)
				response.set_cookie(key="token", value=temp_token)
				return {"detail": "Autenticación como jugador exitosa"}
	else:
		raise HTTPException(status_code=401, detail="Usuario o contraseña incorrectos")

@app.post("/logout")
async def logout(request: Request, response: Response):
	user, admin = await get_session(request)
	response.delete_cookie(key="user")
	response.delete_cookie(key="admin")
	response.delete_cookie(key="token")
	
	if not admin:
		del PLAYERS[user]
	
	return {"detail": "Sesion cerrada"}

@app.get("/session")
async def actual_session(request: Request):
	user, admin = await get_session(request)
	return {"detail": f"Usuario: {user} | Admin?: {admin}"}

# RUTAS DE TESTS
@app.get("/test/all", response_model=List[JSON_Test_Output])
async def get_all_test(request: Request):
	_, admin = await get_session(request)
	if admin:
		try:
			all_test = session.query(Test).all()

			if not all_test:
				raise HTTPException(status_code=404, detail="No hay tests disponibles")

			response = []

			for test in all_test:
				test_data = JSON_Test_Output(
					id=test.id, 
					title=test.title, 
					image=test.image, 
					archived=test.archived, 
					played=await count_games(test.id),
					createdAt=test.createdAt.isoformat() if test.createdAt else None,
					updatedAt=test.updatedAt.isoformat() if test.updatedAt else None,
					questions=None,
					games=None
				)

				response.append(test_data)

			return response
		except HTTPException as e:
			raise e
		except Exception as e:
			raise HTTPException(status_code=500, detail=f"Error al obtener los test: {str(e)}")
		finally:
			session.close()
	else:
		raise HTTPException(status_code=403, detail="No tienes permiso para ver los test")

@app.get("/test/{ID}/view", response_model=JSON_Test_Output)
async def get_test_by_ID(request: Request, ID: int):
	_, admin = await get_session(request)
	if admin:
		try:
			test = session.query(Test).filter(Test.id == ID).first()
			if test is None:
				raise HTTPException(status_code=404, detail="Test no encontrado")

			questions_data = [
				JSON_Question_Output(
					id=question.id,
					test_id=question.test_id,
					title=question.title,
					image=question.image,
					questionType=question.questionType,
					allocatedTime=question.allocatedTime,
					questionOrder=question.questionOrder,
					weight=question.weight,
					answers=[
						JSON_Answer_Output(
							id=answer.id,
							question_id=answer.question_id,
							title=answer.title,
							isCorrect=answer.isCorrect
						) for answer in question.answers
					]
				) for question in test.questions
				]

			response = JSON_Test_Output(
				id=test.id, 
				title=test.title, 
				image=test.image, 
				archived=test.archived, 
				played=await count_games(test.id),
				createdAt=test.createdAt,
				updatedAt=test.updatedAt,
				questions=questions_data,
				games=None
			)

			return response
		except HTTPException as e:
			raise e
		except Exception as e:
			raise HTTPException(status_code=500, detail=f"Error al obtener el test: {str(e)}")
		finally:
			session.close()
	else:
		raise HTTPException(status_code=403, detail="No tienes permiso para ver los detalles del test")

@app.delete("/test/{ID}/delete")
async def delete_test_by_ID(request: Request, ID: int):
	_, admin = await get_session(request)
	if admin:
		try:
			test_to_delete = session.query(Test).filter(Test.id == ID).first()
			if test_to_delete is None:
				raise HTTPException(status_code=404, detail="Test no encontrado")
			session.delete(test_to_delete)
			session.commit()
			return {"detail": "Test eliminado correctamente"}
		
		except HTTPException as e:
			raise e
		except Exception as e:
			session.rollback()
			raise HTTPException(status_code=500, detail=f"Error al eliminar el test: {str(e)}")
		finally:
			session.close()
	else:
		raise HTTPException(status_code=403, detail="No tienes permiso para eliminar tests")

@app.post("/test/{ID}/archive")
async def toggle_archive_test(request: Request, ID: int):
	_, admin = await get_session(request)
	if admin:
		try:
			test = session.query(Test).filter(Test.id == ID).first()
			if test is None:
				raise HTTPException(status_code=404, detail="Test no encontrado")

			test.archived = not test.archived
			test.updatedAt = datetime.now()
			session.commit()
			return {"detail": "Test archivado" if test.archived else "Test desarchivado"}

		except HTTPException as e:
			raise e
		except Exception as e:
			session.rollback()
			raise HTTPException(status_code=500, detail=f"Error al archivar el test: {str(e)}")
		finally:
			session.close()
	else:
		raise HTTPException(status_code=403, detail="No tienes permiso para archivar tests")

@app.put("/test/create")
async def create_test(request: Request, input_data: JSON_Test_Input):
	_, admin = await get_session(request)
	if admin:
		try:
			for question in input_data.questions:
				correct_answer = len([answer for answer in question.answers if answer.isCorrect])
				if  correct_answer == 0:
					raise HTTPException(status_code=500, detail="Debe haber al menos una respuesta correcta")
				elif correct_answer > 1 and question.questionType == "unica":
					raise HTTPException(status_code=500, detail="Solo puede haber una respuesta correcta")
				elif (correct_answer < 2 or len(question.answers) < 3) and question.questionType == "multiple":
					raise HTTPException(status_code=500, detail="Debe haber al menos dos respuestas correctas y tres preguntas para un test de selección múltiple")

			new_test = Test(
				title=input_data.title,
				image=input_data.image,
				createdAt=datetime.now(),
				updatedAt=datetime.now()
			)
			session.add(new_test)
			session.flush()
			
			if not input_data.questions:
				raise HTTPException(status_code=400, detail="No hay preguntas para guardar")

			index = 1
			for question_data in input_data.questions:

				if not question_data.answers:
					raise HTTPException(status_code=400, detail="No hay respuestas para guardar")

				new_question = Question(
					test_id=new_test.id,
					title=question_data.title,
					image=question_data.image,
					questionType=question_data.questionType,
					allocatedTime=question_data.allocatedTime,
					weight=question_data.weight
				)
				session.add(new_question)
				session.flush()

				for answer_data in question_data.answers:
					new_answer = Answer(
						question_id=new_question.id,
						title=answer_data.title,
						isCorrect=answer_data.isCorrect
					)
					session.add(new_answer)
				index += 1
			session.commit()
			return {"detail": "Test creado correctamente con ID: {}".format(new_test.id)}
		except HTTPException as e:
			raise e
		except Exception as e:
			session.rollback()
			raise HTTPException(status_code=500, detail=f"Error al editar el test: {str(e)}")
		finally:
			session.close()
	else:
		raise HTTPException(status_code=403, detail="No tienes permiso para crear tests")

@app.post("/test/{ID}/edit")
async def edit_test(request: Request, ID: int, input_data: JSON_Test_Input):
	_, admin = await get_session(request)
	if admin:
		try:
			test = session.query(Test).filter(Test.id == ID).first()

			count = await count_games(ID)

			if not test:
				raise HTTPException(status_code=404, detail="Test no encontrado")
			
			if count == 0:
				created_temp = test.createdAt

				test_to_delete = session.query(Test).filter(Test.id == ID).first()
				if test_to_delete is None:
					raise HTTPException(status_code=404, detail="Test no encontrado")
				session.delete(test_to_delete)
				session.commit()
				
				for question in input_data.questions:
					correct_answer = len([answer for answer in question.answers if answer.isCorrect])
					if  correct_answer == 0:
						raise HTTPException(status_code=500, detail="Debe haber al menos una respuesta correcta")
					elif correct_answer > 1 and question.questionType == "unica":
						raise HTTPException(status_code=500, detail="Solo puede haber una respuesta correcta")

					new_test = Test(
					title=input_data.title,
					image=input_data.image,
					createdAt=created_temp,
					updatedAt=datetime.now()
				)
				session.add(new_test)
				session.flush()
				
				if not input_data.questions:
					raise HTTPException(status_code=400, detail="No hay preguntas para guardar")

				index = 1
				for question_data in input_data.questions:

					if not question_data.answers:
						raise HTTPException(status_code=400, detail="No hay respuestas para guardar")

					new_question = Question(
						test_id=new_test.id,
						title=question_data.title,
						image=question_data.image,
						questionType=question_data.questionType,
						allocatedTime=question_data.allocatedTime,
						weight=question_data.weight
					)
					session.add(new_question)
					session.flush()

					for answer_data in question_data.answers:
						new_answer = Answer(
							question_id=new_question.id,
							title=answer_data.title,
							isCorrect=answer_data.isCorrect
						)
						session.add(new_answer)
					index += 1
				session.commit()

				create_test(request, input_data)
				return {"detail": "Test editado correctamente"}
			else:
				raise HTTPException(status_code=403, detail="No puedes editar un test que ya ha sido jugado")
		except HTTPException as e:
			raise e
		except Exception as e:
			session.rollback()
			raise HTTPException(status_code=500, detail=f"Error al editar el test: {str(e)}")
		finally:
			session.close()
	else:
		raise HTTPException(status_code=403, detail="No tienes permiso para editar tests")


# RUTAS DE RESULTADOS
@app.get("/results/test/{ID}/all", response_model=JSON_Test_Output)
async def get_all_results(request: Request, ID: int):
	_, admin = await get_session(request)
	if admin:
		try:
			test = session.query(Test).filter(Test.id == ID).first()
			if test is None:
				raise HTTPException(status_code=404, detail="Test no encontrado")

			games_for_this_test = session.query(Game).filter(Game.test_id == ID).all()
			if not games_for_this_test:
				raise HTTPException(status_code=404, detail="No hay juegos para este test")

			games_json = []
			for game in games_for_this_test:
				results = session.query(Result).filter(Result.game_id == game.id).all()

				if not results:
					raise HTTPException(status_code=404, detail="No hay resultados para este juego")

				game_data = JSON_Game_Output(
					id=game.id,
					test_id=game.test_id,
					playedAt=game.playedAt.isoformat() if game.playedAt else None,
					players=await count_players(game.id),
					results=[
						JSON_Result_Output(
							id=result.id,
							player_id=result.player_id,
							game_id=result.game_id,
							score=result.score,
							solutions=None
						) for result in results
					]
				)
				games_json.append(game_data)

			response_data = JSON_Test_Output(
				id=test.id, 
				title=test.title, 
				image=test.image, 
				archived=test.archived,
				played=await count_games(test.id), 
				createdAt=test.createdAt,
				updatedAt=test.updatedAt,
				questions=None,
				games=games_json
			)

			return response_data
		except HTTPException as e:
			raise e
		except Exception as e:
			raise HTTPException(status_code=500, detail=f"Error al obtener los test: {str(e)}")
		finally:
			session.close()
	else:
		raise HTTPException(status_code=403, detail="No tienes permiso para ver los resultados del test")

@app.get("/results/test/{ID}/game/{GAME_ID}", response_model=JSON_Test_Output)
async def get_results_by_game(request: Request, ID: int, GAME_ID: int):
	_, admin = await get_session(request)
	if admin:
		try:
			test = session.query(Test).filter(Test.id == ID).first()
			if test is None:
				raise HTTPException(status_code=404, detail="Test no encontrado")

			game= session.query(Game).filter(Game.test_id == ID, Game.id == GAME_ID).first()
			if not game:
				raise HTTPException(status_code=404, detail="No hay juegos para este test, o el juego no existe")

			results = session.query(Result).filter(Result.game_id == game.id).all()

			if not results:
				raise HTTPException(status_code=404, detail="No hay resultados para este juego")

			game_json = []
			game_json.append(JSON_Game_Output(
				id=game.id,
				test_id=game.test_id,
				playedAt=game.playedAt.isoformat() if game.playedAt else None,
				players=await count_players(game.id),
				results=[
					JSON_Result_Output(
						id=result.id,
						player_id=result.player_id,
						game_id=result.game_id,
						score=result.score,
						solutions=[
							JSON_Solution_Output(
								id=solution.id,
								result_id=solution.result_id,
								question_id=solution.question_id,
								answer_id=solution.answer_id,
								time=solution.time
							) for solution in result.solutions
						]
					) for result in results
				]
			))

			questions_data = [
				JSON_Question_Output(
					id=question.id,
					test_id=question.test_id,
					title=question.title,
					image=question.image,
					questionType=question.questionType,
					allocatedTime=question.allocatedTime,
					questionOrder=question.questionOrder,
					weight=question.weight,
					answers=[
						JSON_Answer_Output(
							id=answer.id,
							question_id=answer.question_id,
							title=answer.title,
							isCorrect=answer.isCorrect
						) for answer in question.answers
					]
				) for question in test.questions
				]

			response_data = JSON_Test_Output(
				id=test.id, 
				title=test.title, 
				image=test.image, 
				archived=test.archived,
				played=await count_games(test.id), 
				createdAt=test.createdAt,
				updatedAt=test.updatedAt,
				questions=questions_data,
				games=game_json
			)

			return response_data
		except HTTPException as e:
			raise e
		except Exception as e:
			raise HTTPException(status_code=500, detail=f"Error al obtener el test: {str(e)}")
		finally:
			session.close()
	else:
		raise HTTPException(status_code=403, detail="No tienes permiso para ver los resultados del test")

@app.get("/results/player/{ID}/all")
async def get_all_results_by_player(request: Request, ID: int, response_model=List[JSON_Test_Output]):
	_, admin = await get_session(request)
	if admin:
		try:
			player = session.query(Player).filter(Player.id == ID).first()
			if player is None:
				raise HTTPException(status_code=404, detail="Jugador no encontrado")

			results = session.query(Result).filter(Result.player_id == ID).all()
			if not results:
				raise HTTPException(status_code=404, detail="No hay resultados para este jugador")

			gamesId = {result.game_id for result in results}
			games = session.query(Game).filter(Game.id.in_(gamesId)).all()
			if not games:
				raise HTTPException(status_code=404, detail="No hay juegos para este jugador")

			testsId = {game.test_id for game in games}
			tests = session.query(Test).filter(Test.id.in_(testsId)).all()
			if not tests:
				raise HTTPException(status_code=404, detail="No hay tests para este jugador")

			games_dict = {game.id: game for game in games}
			tests_dict = {test.id: test for test in tests}
			results_dict = {}
			for result in results:
				results_dict.setdefault(result.game_id, []).append(result)

			response_data = []
			for test_id, test in tests_dict.items():
				games_json = []
				for game_id, game in games_dict.items():
					if game.test_id == test_id:
						results_json = [JSON_Result_Output(
							id=result.id,
							player_id=result.player_id,
							game_id=result.game_id,
							score=result.score,
							solutions=None
						) for result in results_dict.get(game_id, [])]

						game_data = JSON_Game_Output(
							id=game.id,
							test_id=game.test_id,
							playedAt=game.playedAt.isoformat() if game.playedAt else None,
							players=await count_players(game.id),
							results=results_json
						)
						games_json.append(game_data)

				test_data = JSON_Test_Output(
					id=test.id, 
					title=test.title, 
					image=test.image, 
					archived=test.archived,
					played=await count_games(test.id), 
					createdAt=test.createdAt,
					updatedAt=test.updatedAt,
					questions=None,
					games=games_json
				)
				response_data.append(test_data)

			return response_data
		except HTTPException as e:
			raise e
		except Exception as e:
			raise HTTPException(status_code=500, detail=f"Error al obtener los test: {str(e)}")
		finally:
			session.close()
	else:
		raise HTTPException(status_code=403, detail="No tienes permiso para ver los resultados del test")

@app.get("/results/player/{ID}/game/{GAME_ID}")
async def get_results_by_player(request: Request, ID: int, GAME_ID: int):
	_, admin = await get_session(request)
	if admin:
		try:
			player = session.query(Player).filter(Player.id == ID).first()
			if player is None:
				raise HTTPException(status_code=404, detail="Jugador no encontrado")

			result = session.query(Result).filter(Result.player_id == ID, Result.game_id == GAME_ID).first()
			if result is None:
				raise HTTPException(status_code=404, detail="No hay resultados para este jugador en este juego")

			solution = session.query(Solution).filter(Solution.result_id == result.id).all()
			if solution is None:
				raise HTTPException(status_code=404, detail="No hay soluciones para este jugador en este juego")

			game = session.query(Game).filter(Game.id == GAME_ID).first()
			if game is None:
				raise HTTPException(status_code=404, detail="Juego no encontrado")

			test = session.query(Test).filter(Test.id == game.test_id).first()
			if test is None:
				raise HTTPException(status_code=404, detail="Test no encontrado")

			result_data = [
				JSON_Result_Output(
				id=result.id,
				player_id=result.player_id,
				game_id=result.game_id,
				score=result.score,
				solutions=[
					JSON_Solution_Output(
						id=solution.id,
						result_id=solution.result_id,
						question_id=solution.question_id,
						answer_id=solution.answer_id,
						time=solution.time
					) for solution in solution
				]
			)
			]

			game_data = [
				JSON_Game_Output(
				id=game.id,
				test_id=game.test_id,
				playedAt=game.playedAt.isoformat() if game.playedAt else None,
				players=await count_players(game.id),
				results=result_data
			)]

			questions_data = [
				JSON_Question_Output(
					id=question.id,
					test_id=question.test_id,
					title=question.title,
					image=question.image,
					questionType=question.questionType,
					allocatedTime=question.allocatedTime,
					questionOrder=question.questionOrder,
					weight=question.weight,
					answers=[
						JSON_Answer_Output(
							id=answer.id,
							question_id=answer.question_id,
							title=answer.title,
							isCorrect=answer.isCorrect
						) for answer in question.answers
					]
				) for question in test.questions
				]

			response_data = JSON_Test_Output(
				id=test.id,
				title=test.title,
				image=test.image,
				archived=test.archived,
				played=await count_games(test.id),
				createdAt=test.createdAt,
				updatedAt=test.updatedAt,
				questions=questions_data, 
				games=game_data
			)

			return response_data
		except HTTPException as e:
			raise e
		except Exception as e:
			raise HTTPException(status_code=500, detail=f"Error al obtener el test: {str(e)}")
		finally:
			session.close()
	else:
		raise HTTPException(status_code=403, detail="No tienes permiso para ver los resultados del test")

@app.put("/results/game")
async def create_game(request: Request, input_data: JSON_Game_Input):
	_, admin = await get_session(request)
	if admin:
		try:
			test = session.query(Test).filter(Test.id == input_data.test_id).first()
			if not test:
				raise HTTPException(status_code=404, detail="Test no encontrado")

			new_game = Game(
				test_id=test.id,
				playedAt=datetime.now()
			)
			session.add(new_game)
			session.flush()

			for result_data in input_data.results:
				if not session.query(Player).filter(Player.id == result_data.player_id).first():
					raise HTTPException(status_code=404, detail="Jugador no encontrado")

				new_result = Result(
					player_id=result_data.player_id,
					game_id=new_game.id,
					score=result_data.score
				)
				session.add(new_result)
				session.flush()

				for solution_data in result_data.solutions:
					if not session.query(Question).filter(Question.id == solution_data.question_id).first():
						raise HTTPException(status_code=404, detail="Pregunta no encontrada")

					new_solution = Solution(
						result_id=new_result.id,
						question_id=solution_data.question_id,
						answer_id=solution_data.answer_id,
						time=solution_data.time
					)
					session.add(new_solution)

			session.commit()

			return {"detail": "Partida guardada correctamente con ID: {}".format(new_game.id)}
		except HTTPException as e:
			raise e
		except Exception as e:
			session.rollback()
			raise HTTPException(status_code=500, detail=f"Error al guardar partida: {str(e)}")
		finally:
			session.close()
	else:
		raise HTTPException(status_code=403, detail="No tienes permiso para guardar partida")

@app.delete("/results/{ID}/delete")
async def delete_game(request: Request, ID: int):
	_, admin = await get_session(request)
	if admin:
		try:
			game_to_delete = session.query(Game).filter(Game.id == ID).first()
			if game_to_delete is None:
				raise HTTPException(status_code=404, detail="Juego no encontrado")
			session.delete(game_to_delete)
			session.commit()
			return {"detail": "Juego eliminado correctamente"}
		
		except HTTPException as e:
			raise e
		except Exception as e:
			session.rollback()
			raise HTTPException(status_code=500, detail=f"Error al eliminar el juego: {str(e)}")
		finally:
			session.close()
	else:
		raise HTTPException(status_code=403, detail="No tienes permiso para eliminar juegos")


# RUTAS DE JUGADORES
@app.put("/player/add")
async def create_player(request: Request):
	_, admin = await get_session(request)
	if admin:
		try:
			for username in PLAYERS:
				existing_player = session.query(Player).filter(Player.name == username).first()
				if not existing_player:
					new_player = Player(
						name=username,
						createdAt=datetime.now()
					)
					session.add(new_player)

			session.commit()
			return {"detail": "Jugadores creados correctamente"}

		except HTTPException as e:
			raise e
		except Exception as e:
			session.rollback()
			raise HTTPException(status_code=500, detail=f"Error al crear los jugadores: {str(e)}")
		finally:
			session.close()
	else:
		raise HTTPException(status_code=403, detail="No tienes permiso para crear jugadores")

@app.get("/player/all", response_model=List[JSON_Player_Output])
async def get_all_players(request: Request):
	_, admin = await get_session(request)
	if admin:
		try:
			all_players = session.query(Player).all()

			if not all_players:
				raise HTTPException(status_code=404, detail="No hay jugadores disponibles")


			response_data = []
			for player in all_players:
				player_data = JSON_Player_Output(
					id=player.id,
					name=player.name,
					createdAt=player.createdAt,
					results=None
				)
			
				response_data.append(player_data)

			return response_data
		except HTTPException as e:
			raise e
		except Exception as e:
			raise HTTPException(status_code=500, detail=f"Error al obtener los jugadores: {str(e)}")
		finally:
			session.close()
	else:
		raise HTTPException(status_code=403, detail="No tienes permiso para ver los jugadores")

@app.delete("/player/{ID}/delete")
async def delete_player(request: Request, ID: int):
	_, admin = await get_session(request)
	if admin:
		try:
			player_to_delete = session.query(Player).filter(Player.id == ID).first()
			if player_to_delete is None:
				raise HTTPException(status_code=404, detail="Jugador no encontrado")
			session.delete(player_to_delete)
			session.commit()
			return {"detail": "Jugador eliminado correctamente"}
		
		except HTTPException as e:
			raise e
		except Exception as e:
			session.rollback()
			raise HTTPException(status_code=500, detail=f"Error al eliminar el jugador: {str(e)}")
		finally:
			session.close()
	else:
		raise HTTPException(status_code=403, detail="No tienes permiso para eliminar jugadores")

'''
# WEBSOCKET DE JUEGO
@app.websocket("/play")							# FALTA
async def admin_websocket(websocket: WebSocket):
	pass
'''