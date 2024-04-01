from fastapi import FastAPI, Response, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
from datetime import datetime
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from typing import List, Optional
import random
import uuid
import asyncio
from starlette.websockets import WebSocketState


from .db_config import Test, Question, Answer, Game, Result, Player, Solution

ADMIN_USER = "admin"
ADMIN_PASSWORD = "1234"

PLAYERS_TOKEN = {}
ADMIN_TOKEN = None

app = FastAPI()

app.add_middleware(
	CORSMiddleware,
	allow_origins=["http://localhost:3000"],  # Permite las solicitudes desde el puerto 3000
	allow_credentials=True,
	allow_methods=["*"],  # Permite todos los métodos
	allow_headers=["*"],  # Permite todos los encabezados
)

engine = create_engine('sqlite:///app/db/local.db')
Session = sessionmaker(bind=engine)
session = Session()

# Modelo de datos para el login
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
	#questionType: Literal['unica', 'multiple']
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
	player_name: str
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
	#questionType: Literal['unica', 'multiple']
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
async def is_admin(token: str):
	if not token:
		raise HTTPException(status_code=401, detail="Fallo de sesión")

	if token != ADMIN_TOKEN:
		raise HTTPException(status_code=401, detail="No eres administrador")

	return True

async def generate_short_token():
	return str(uuid.uuid4())[:10]

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
async def login(input_data: JSON_Login):
	global ADMIN_TOKEN

	user = input_data.username
	password = input_data.password

	if user == ADMIN_USER:
		if password == ADMIN_PASSWORD:
			token = await generate_short_token()
			ADMIN_TOKEN = token
			return {"detail": "Autenticación como administrador exitosa", "token": token}
		else:
			raise HTTPException(status_code=401, detail="Nombre o contraseña incorrecta")

@app.post("/logout/token={token}")
async def logout(token: str, response: Response):
	if not token:
		raise HTTPException(status_code=401, detail="No se encontró token de sesión")

	if token == ADMIN_TOKEN:
		ADMIN_TOKEN = None
	elif token in PLAYERS_TOKEN:
		del PLAYERS_TOKEN[token]

	return {"detail": "Sesión cerrada"}

@app.get("/session/token={token}")
async def actual_session(token: str):
	if not token:
		raise HTTPException(status_code=401, detail="No se encontró token de sesión")

	if token == ADMIN_TOKEN:
		return {"detail": "Sesión de administrador activa"}
	elif token in PLAYERS_TOKEN:
		return {"detail": f"Sesión de jugador activa: {PLAYERS_TOKEN[token]}"}




# RUTAS DE TESTS
@app.get("/test/all/token={token}", response_model=List[JSON_Test_Output])
async def get_all_test(token: str):
	await is_admin(token)
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

@app.get("/test/{ID}/view/token={token}", response_model=JSON_Test_Output)
async def get_test_by_ID(token: str, ID: int):
	await is_admin(token)
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
				#questionType=question.questionType,
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

@app.delete("/test/{ID}/delete/token={token}")
async def delete_test_by_ID(token: str, ID: int):
	await is_admin(token)
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

@app.post("/test/{ID}/archive/token={token}")
async def toggle_archive_test(token: str, ID: int):
	await is_admin(token)
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

@app.put("/test/create/token={token}")
async def create_test(token: str, input_data: JSON_Test_Input):
	await is_admin(token)
	try:
		for question in input_data.questions:
			correct_answer = len([answer for answer in question.answers if answer.isCorrect])
			if  correct_answer == 0:
				raise HTTPException(status_code=500, detail="Debe haber al menos una respuesta correcta")
			elif correct_answer > 1: #and question.questionType == "unica":
				raise HTTPException(status_code=500, detail="Solo puede haber una respuesta correcta")
			elif correct_answer > 4:
				raise HTTPException(status_code=500, detail="Solo puede haber cuatro respuestas correctas")
			#elif (correct_answer < 2 or len(question.answers) < 3) and question.questionType == "multiple":
			#	raise HTTPException(status_code=500, detail="Debe haber al menos dos respuestas correctas y tres pregunta_raws para un test de selección múltiple")

			existing_test = session.query(Test).filter(Test.title == input_data.title).first()

			if existing_test is not None:
				raise HTTPException(status_code=400, detail="Ya existe un test con este título")
			
		new_test = Test(
			title=input_data.title,
			image=input_data.image,
			createdAt=datetime.now(),
			updatedAt=datetime.now()
		)
		session.add(new_test)
		session.flush()
		
		if not input_data.questions:
			raise HTTPException(status_code=400, detail="No hay pregunta_raws para guardar")

		index = 1
		for question_data in input_data.questions:

			if not question_data.answers:
				raise HTTPException(status_code=400, detail="No hay respuestas para guardar")

			new_question = Question(
				test_id=new_test.id,
				title=question_data.title,
				image=question_data.image,
				#questionType=question_data.questionType,
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

@app.post("/test/{ID}/edit/token={token}")
async def edit_test(token: str, ID: int, input_data: JSON_Test_Input):
	await is_admin(token)
	try:
		await delete_test_by_ID(ID=ID, token=token)
		await create_test(input_data=input_data, token=token)
		return {"detail": "Test editado correctamente"}
	except HTTPException as e:
		raise e
	except Exception as e:
		session.rollback()
		raise HTTPException(status_code=500, detail=f"Error al editar el test: {str(e)}")
	finally:
		session.close()





# RUTAS DE RESULTADOS
@app.get("/results/test/{ID}/all/token={token}", response_model=JSON_Test_Output)
async def get_all_results(token: str, ID: int):
	await is_admin(token)
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
						player_name=session.query(Player).filter(Player.id == result.player_id).first().name,
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

@app.get("/results/test/{ID}/game/{GAME_ID}/token={token}", response_model=JSON_Test_Output)
async def get_results_by_game(token: str, ID: int, GAME_ID: int):
	await is_admin(token)
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
					player_name=session.query(Player).filter(Player.id == result.player_id).first().name,
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
				#questionType=question.questionType,
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

@app.get("/results/player/{ID}/all/token={token}")
async def get_all_results_by_player(token: str, ID: int, response_model=List[JSON_Test_Output]):
	await is_admin(token)
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
						player_name=session.query(Player).filter(Player.id == result.player_id).first().name,
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

@app.get("/results/player/{ID}/game/{GAME_ID}/token={token}")
async def get_results_by_player(token: str, ID: int, GAME_ID: int):
	await is_admin(token)
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
			player_name=session.query(Player).filter(Player.id == ID).first().name,
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
				#questionType=question.questionType,
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

@app.put("/results/game/token={token}")
async def create_game(token: str, input_data: JSON_Game_Input):
	await is_admin(token)
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
					raise HTTPException(status_code=404, detail="pregunta_raw no encontrada")

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

@app.delete("/results/{ID}/delete/token={token}")
async def delete_game(token: str, ID: int):
	await is_admin(token)
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


# RUTAS DE JUGADORES
@app.put("/player/add/token={token}")
async def create_player(token: str):
	await is_admin(token)
	try:
		for username in PLAYERS_TOKEN.values():
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

@app.get("/player/all/token={token}", response_model=List[JSON_Player_Output])
async def get_all_players(token: str):
	await is_admin(token)
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

@app.delete("/player/{ID}/delete/token={token}")
async def delete_player(token: str, ID: int):
	await is_admin(token)
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

MODE = None
PIN = None
TEST = None
TOTAL_PREGUNTAS = None
PREGUNTA_ACTUAL = None
TOTAL_RESPONSES = None
TIME = None
DONE = None

UPDATE = None

CONNECTIONS = []
TEMP_RESULT = {}
STATS = []

async def transmitir(websocket: WebSocket, token: str):
	global TIME, MODE, UPDATE, TOTAL_RESPONSES
	if token == ADMIN_TOKEN:
		admin = True
	else:
		admin = False
	
	while True:
		if MODE == "LOBBY" and UPDATE:
			if admin:
				mensaje = {
					"mode": "LOBBY",
					"PIN": PIN,
					"test": TEST.title,
					"image": TEST.image,
					"players": list(PLAYERS_TOKEN.values()),
					"questions": TOTAL_PREGUNTAS,
					"instructions": "Esperando jugadores se unan, enviar 'START' para comenzar la partida"
				}
				UPDATE = False
				await websocket.send_text(json.dumps(mensaje))
			else:
				mensaje = {
					"mode": "LOBBY",
					"name": PLAYERS_TOKEN[token],
					"token": token
				}
				await websocket.send_text(json.dumps(mensaje))
		elif MODE == "LOADING":
			for countdown in range(5, 0, -1):
				mensaje = {
					"mode": "LOADING",
					"countdown": countdown,
					"time": TIME
				}
				await websocket.send_text(json.dumps(mensaje))
				await asyncio.sleep(1)
			MODE = "PLAYING"
		elif MODE == "PLAYING":
			if admin:
				Question = TEST.questions[PREGUNTA_ACTUAL]
				mensaje = {
					"mode": "PLAYING",
					"question": [
						{
							"question_id": Question.id,
							"question_title": Question.title,
							"question_image": Question.image,
							#"question_type": Question.questionType,
							"question_weight": Question.weight,
							"question_answers": [
								{
									"answers_id": answer.id,
									"answers_title": answer.title,
								} for answer in Question.answers
								]
						}
					],
					"question_current": PREGUNTA_ACTUAL,
					"question_total": TOTAL_PREGUNTAS,
					"question_time": TIME,
					"responses": TOTAL_RESPONSES,
					"players": len(PLAYERS_TOKEN),
					"instructions": "Puedes ver los resultados mandando 'SKIP'"
				}
				await websocket.send_text(json.dumps(mensaje))
				TIME -= 1
				if TIME == 0:
					await calculate_results()
					MODE = "RESULTS"
			else:
				Question = TEST.questions[PREGUNTA_ACTUAL]
				mensaje = {
					"mode": "PLAYING",
					"question": [
						{
							"question_id": Question.id,
							"question_title": Question.title,
							#"question_type": Question.questionType,
							"question_answers": [
								{
									"answers_id": answer.id,
									"answers_title": answer.title,
								} for answer in Question.answers
								]
						}
					],
					"question_time": TIME
				}
				await websocket.send_text(json.dumps(mensaje))
			await asyncio.sleep(1)
			pass
		elif MODE == "RESULTS":
			if admin:
				mensaje = {
					"mode": "RESULTS",
					"global_score": [
						{
							"player": PLAYERS_TOKEN[token],
							"score": TEMP_RESULT[token].score
						} for token in TEMP_RESULT
					],
					"number question": PREGUNTA_ACTUAL,
					"question": TEST.questions[PREGUNTA_ACTUAL].title,
					"answers": [
						{
							"player": PLAYERS_TOKEN[token],
							"answer": STATS[PREGUNTA_ACTUAL][token][1],
							"correct": STATS[PREGUNTA_ACTUAL][token][2]
						} for token in STATS[PREGUNTA_ACTUAL]
					],
					"posible_answers": [
						{
							"answers": answer.title,
							"correct": answer.isCorrect
						} for answer in TEST.questions[PREGUNTA_ACTUAL].answers
					],
					"instructions": "Enviar 'NEXT' para continuar con la siguiente pregunta o 'END' para finalizar la partida"

				}
				await websocket.send_text(json.dumps(mensaje))

			else:
				mensaje = {
					"mode": "RESULTS",
					"score": TEMP_RESULT[token].score,
					"question": STATS[PREGUNTA_ACTUAL][token][0],
					"answer": STATS[PREGUNTA_ACTUAL][token][1],
					"correct": STATS[PREGUNTA_ACTUAL][token][2]
				}

				await websocket.send_text(json.dumps(mensaje))
			await asyncio.sleep(10)
		elif MODE == "END":
			if admin:
				mensaje = {
					"mode": "END",
					"results": [
						{
							"player": PLAYERS_TOKEN[token],
							"score": TEMP_RESULT[token].score
						} for token in TEMP_RESULT
					]
				}
				await websocket.send_text(json.dumps(mensaje))
			else:
				mensaje = {
					"mode": "END",
					"score": TEMP_RESULT[token].score
				}
				await websocket.send_text(json.dumps(mensaje))

			await asyncio.sleep(10)

		await asyncio.sleep(1)

async def recibir(websocket: WebSocket, token: str):
	global TIME, PREGUNTA_ACTUAL, MODE, TEMP_RESULT, TOTAL_RESPONSES, STATS, DONE
	if token == ADMIN_TOKEN:
		admin = True
	else:
		admin = False

	while True:
		if MODE == "LOBBY" and admin:
			data = await websocket.receive_text()
			if data == "START" and len(PLAYERS_TOKEN) > 0:
				TIME = TEST.questions[PREGUNTA_ACTUAL].allocatedTime
				PREGUNTA_ACTUAL = 0
				TOTAL_RESPONSES = 0

				await create_player(token)

				for clave, valor in PLAYERS_TOKEN.items():
					temp_player = session.query(Player).filter(Player.name == valor).first()
					TEMP_RESULT[clave] = JSON_Result_Input(
						player_id=temp_player.id,
						score=0,
						solutions=[]
					)
				MODE = "LOADING"
			else:
				await websocket.send_text(json.dumps({"error": "No hay jugadores suficientes o el comando es incorrecto"}))
		elif MODE == "PLAYING":
			if admin:
				data = await websocket.receive_text()
				if data == "SKIP":
					await calculate_results()
					MODE = "RESULTS"
						

			elif TOTAL_RESPONSES >= len(PLAYERS_TOKEN):
				await calculate_results()
				MODE = "RESULTS"				

			else:
				data = await websocket.receive_text()
				data_dict = json.loads(data)

				solution_input = JSON_Solution_Input(
					question_id=data_dict["question_id"],
					answer_id=data_dict["answer_id"],
					time=TIME
				)

				if token in TEMP_RESULT:
					TEMP_RESULT[token].solutions.append(solution_input)
					TOTAL_RESPONSES += 1
					await websocket.send_text(json.dumps({"status": "Recibido"}))
		elif MODE == "RESULTS":
			if admin:
				data = await websocket.receive_text()
				if data == "NEXT":
					PREGUNTA_ACTUAL += 1
					TOTAL_RESPONSES = 0
					DONE = False
					if PREGUNTA_ACTUAL == TOTAL_PREGUNTAS:
						MODE = "END"
					else:
						TIME = TEST.questions[PREGUNTA_ACTUAL].allocatedTime
						MODE = "LOADING"
				elif data == "END":
					MODE = "END"
		elif MODE == "END":
			if admin:
				data = await websocket.receive_text()
				if data == "SAVE":
					await save_game(websocket, token)
					await close_all_connections()
					await websocket.close()
				elif data == "CLOSE":
					await close_all_connections()
					await websocket.close()

		await asyncio.sleep(1)

async def close_all_connections():
	for connection in CONNECTIONS:
		await connection.close()

async def calculate_results():
    global TEMP_RESULT, STATS, DONE

    if not DONE:
        temp_stats = {}

        for token in TEMP_RESULT:
            solucion_encontrada = False

            for solution in TEMP_RESULT[token].solutions:
                if TEST.questions[PREGUNTA_ACTUAL].id == solution.question_id:
                    temp_answer = session.query(Answer).filter(Answer.id == solution.answer_id).first()

                    if temp_answer and temp_answer.question_id == TEST.questions[PREGUNTA_ACTUAL].id:
                        correct = temp_answer.isCorrect
                        if correct:
                            TEMP_RESULT[token].score += TEST.questions[PREGUNTA_ACTUAL].weight
                        
                        temp_stats[token] = [TEST.questions[PREGUNTA_ACTUAL].title, temp_answer.title, correct]
                        solucion_encontrada = True
                        break

            if not solucion_encontrada:
                temp_stats[token] = [TEST.questions[PREGUNTA_ACTUAL].title, "No contestado", False]

        STATS.append(temp_stats)
        DONE = True

async def save_game(websocket: WebSocket, token: str):
	global TEST, TEMP_RESULT
	
	test = session.query(Test).filter(Test.id == TEST.id).first()
	if not test:
		await websocket.send_text(json.dumps({"error": "Test no encontrado"}))
		return
	
	new_game = Game(
		test_id=TEST.id,
		playedAt=datetime.now()
	)

	session.add(new_game)
	session.flush()

	for token in TEMP_RESULT:
		player = session.query(Player).filter(Player.name == PLAYERS_TOKEN[token]).first()
		if not player:
			await websocket.send_text(json.dumps({"error": "Jugador no encontrado"}))
			return

		new_result = Result(
			player_id=player.id,
			game_id=new_game.id,
			score=TEMP_RESULT[token].score
		)
		session.add(new_result)
		session.flush()

		for solution in TEMP_RESULT[token].solutions:
			new_solution = Solution(
				result_id=new_result.id,
				question_id=solution.question_id,
				answer_id=solution.answer_id,
				time=solution.time
			)
			session.add(new_solution)

		session.commit()
	
	await websocket.send_text(json.dumps({"status": "Partida guardada correctamente"}))
	
	






@app.websocket("/play/test={testID}/token={token}")
async def admin_websocket(websocket: WebSocket, testID: int, token: str):
	global MODE, PIN, TEST, TOTAL_PREGUNTAS, PREGUNTA_ACTUAL, UPDATE, PLAYERS_TOKEN, TEMP_RESULT, STATS, CONNECTIONS
	await websocket.accept()

	try:
		if not token or token != ADMIN_TOKEN:
			await websocket.send_text(json.dumps({"error": "Fallo de sesión"}))
			return

		MODE = "LOBBY"
		PIN = await generate_PIN()
		TEST = await getTest(testID)
		TOTAL_PREGUNTAS = len(TEST.questions)
		PREGUNTA_ACTUAL = 0
		UPDATE = True
		PLAYERS_TOKEN.clear()
		TEMP_RESULT.clear()
		STATS.clear()
		CONNECTIONS.clear()
		if not TEST:
			await websocket.send_text(json.dumps({"error": "Test no encontrado"}))
			return

		send_task = asyncio.create_task(transmitir(websocket, token))
		receive_task = asyncio.create_task(recibir(websocket, token))
		await asyncio.gather(send_task, receive_task)

	except (Exception, WebSocketDisconnect) as e:
		if websocket.client_state != WebSocketState.DISCONNECTED:
			await websocket.send_text(json.dumps({"error": f"Error: {str(e)}"}))

	finally:
		pass


async def generate_PIN():
	return random.randint(100000, 999999)

async def getTest(testID: int):
	test = session.query(Test).filter(Test.id == testID).first()
	if test is None:
		raise WebSocketDisconnect("Test no encontrado")

	questions_data = [
		JSON_Question_Output(
			id=question.id,
			test_id=question.test_id,
			title=question.title,
			image=question.image,
			#questionType=question.questionType,
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



@app.websocket("/play/pin={playerPIN}/player={player}")
async def player_websocket(websocket: WebSocket, playerPIN: int, player: str):
	global MODE, PIN, PLAYERS_TOKEN, UPDATE
	await websocket.accept()

	try:

		if player in PLAYERS_TOKEN.values():
			await websocket.send_text(json.dumps({"error": "Nombre de jugador ya en uso"}))
			await websocket.close()
			return
		else:
			token = await generate_short_token()
			PLAYERS_TOKEN[token] = player

		if not token:
			await websocket.send_text(json.dumps({"error": "Fallo de sesión"}))
			await websocket.close()
			return

		if PIN != playerPIN:
			await websocket.send_text(json.dumps({"error": "PIN incorrecto"}))
			await websocket.close()
			return
		UPDATE = True
		CONNECTIONS.append(websocket)
		send_task = asyncio.create_task(transmitir(websocket, token))
		receive_task = asyncio.create_task(recibir(websocket, token))
		await asyncio.gather(send_task, receive_task)

	except (Exception, WebSocketDisconnect) as e:
		if websocket.client_state != WebSocketState.DISCONNECTED:
			await websocket.send_text(json.dumps({"error": f"Error: {str(e)}"}))

	finally:
		for key, value in list(PLAYERS_TOKEN.items()):
			if value == player:
				del PLAYERS_TOKEN[key]
				UPDATE = True
				break