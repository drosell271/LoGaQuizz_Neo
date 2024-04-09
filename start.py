import subprocess
import os
import shutil
import socket

def obtener_direccion_ip():
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	try:
		# no necesitamos hacer una llamada real
		s.connect(('10.255.255.255', 1))
		IP = s.getsockname()[0]
	except Exception:
		IP = '127.0.0.1'
	finally:
		s.close()
	return IP

def escribir_ip_en_frontend(ip):
	ruta_env_frontend = "./LoGaQuizz_Neo/frontend/.env"
	try:
		with open(ruta_env_frontend, "w") as file:
			file.write(f"REACT_APP_IP={ip}\n")
		print(f"Dirección IP {ip} escrita en el archivo .env del frontend.")
	except IOError:
		print("Hubo un error al escribir en el archivo .env del frontend.")

def modificar_credenciales_admin(nuevo_usuario, nueva_contrasena):
	ruta_api = "./LoGaQuizz_Neo/backend/app/api.py"
	try:
		with open(ruta_api, "r") as file:
			contenido = file.readlines()
		
		with open(ruta_api, "w") as file:
			for linea in contenido:
				if "ADMIN_USER" in linea:
					file.write(f'ADMIN_USER = "{nuevo_usuario}"\n')
				elif "ADMIN_PASSWORD" in linea:
					file.write(f'ADMIN_PASSWORD = "{nueva_contrasena}"\n')
				else:
					file.write(linea)
	except IOError:
		print("Hubo un error al actualizar las credenciales del administrador.")

def mostrar_info_admin():
	user, password = "No encontrado", "No encontrado"
	try:
		with open("./LoGaQuizz_Neo/backend/app/api.py", "r") as file:
			for line in file:
				if "ADMIN_USER" in line:
					user = line.split('=')[1].strip().strip('"').strip("'")
				elif "ADMIN_PASSWORD" in line:
					password = line.split('=')[1].strip().strip('"').strip("'")
	except IOError:
		print("No se pudo leer la configuración del administrador.")

	ip = obtener_direccion_ip()
	escribir_ip_en_frontend(ip)
	print("\nInformación del administrador:")
	print(f"Usuario: {user}")
	print(f"Contraseña: {password}")
	print(f"Dirección IP del ordenador: {ip}")

def cambiar_credenciales():
	nuevo_usuario = input("Ingrese el nuevo usuario: ")
	nueva_contrasena = input("Ingrese la nueva contraseña: ")
	modificar_credenciales_admin(nuevo_usuario, nueva_contrasena)

def lanzar_comandos_en_paralelo():
	# Define los comandos para frontend y backend
	comando_frontend = "npm start"
	comando_backend = "python ./app/main.py"  # Asegúrate de ajustar este comando según tu archivo principal del backend

	# Directorios de trabajo para cada comando
	dir_frontend = "./LoGaQuizz_Neo/frontend"
	dir_backend = "./LoGaQuizz_Neo/backend"

	# Iniciar los procesos en paralelo
	proceso_frontend = subprocess.Popen(comando_frontend, shell=True, cwd=dir_frontend)
	proceso_backend = subprocess.Popen(comando_backend, shell=True, cwd=dir_backend)

	# Esperar a que ambos procesos terminen
	proceso_frontend.wait()
	proceso_backend.wait()

def opcion_iniciar():
	mostrar_info_admin()
	cambiar = input("\n¿Desea cambiar estas credenciales? (y/n): ")
	if cambiar.lower() == 'y':
		cambiar_credenciales()
	lanzar_comandos_en_paralelo()

def menu_existente():
	while True:
		print("\nLa carpeta LoGaQuizz_Neo ya existe. Elige una opción:")
		print("1. Iniciar programa")
		print("2. Reinstalar/Reparar")
		print("3. Eliminar programa")
		opcion = input("Ingresa tu opción (1, 2, 3): ")

		if opcion == '1':
			lanzar_comandos_en_paralelo()
			break
		elif opcion == '2':
			reinstalar_programa()
			break
		elif opcion == '3':
			eliminar_programa()
			break
		else:
			print("Opción no válida, intenta de nuevo.")

def reinstalar_programa():
	eliminar_programa()
	instalar_backend()
	instalar_frontend()

def eliminar_programa():
	confirmacion = input("¿Estás seguro de que quieres eliminar LoGaQuizz_Neo? (y/n): ")
	if confirmacion.lower() == 'y':
		if os.path.isdir("./LoGaQuizz_Neo"):
			shutil.rmtree("./LoGaQuizz_Neo")
			print("Programa eliminado correctamente.")
		else:
			print("No se encontró la carpeta LoGaQuizz_Neo.")
	else:
		print("Eliminación cancelada.")

def preguntar_instalar():
	if not existe_carpeta_logaquizz():
		respuesta = input("La carpeta LoGaQuizz_Neo no existe. ¿Desea instalar el programa? (y/n): ")
		if respuesta.lower() == 'y':
			instalar_backend()
			instalar_frontend()
	else:
		menu_existente()

def existe_carpeta_logaquizz():
	return os.path.isdir("./LoGaQuizz_Neo")

def generar_base_de_datos():
	comando_db = "python app/server/db_config.py"
	subprocess.call(comando_db, shell=True, cwd="./LoGaQuizz_Neo/backend")
	print("Base de datos local.db creada.")

def instalar_backend():
	if not os.path.isdir("./LoGaQuizz_Neo/backend"):
		print("Creando y configurando el entorno virtual para el backend...")

		subprocess.call(["git", "clone", "https://github.com/drosell271/LoGaQuizz_Neo"], shell=True)
		subprocess.call(["python", "-m", "venv", "venv"], shell=True, cwd="./LoGaQuizz_Neo/backend")

		# Verificar si existe local.db y generarla si no existe
		if not os.path.isfile("./LoGaQuizz_Neo/backend/app/db/local.db"):
			generar_base_de_datos()
		
		if os.name == 'nt':  # Windows
			subprocess.call(".\\venv\\Scripts\\activate && pip install -r requirements.txt", shell=True, cwd="./LoGaQuizz_Neo/backend")
		else:  # Unix (Linux, macOS)
			subprocess.call("source ./venv/bin/activate && pip install -r requirements.txt", shell=True, cwd="./LoGaQuizz_Neo/backend")
	else:
		print("El backend ya está configurado.")

def instalar_frontend():
	if not os.path.isdir("./LoGaQuizz_Neo/frontend"):
		print("Instalando dependencias del frontend...")
		subprocess.call("npm install", shell=True, cwd="./LoGaQuizz_Neo/frontend")
	else:
		print("El frontend ya está configurado.")

def preguntar_instalar():
	if not existe_carpeta_logaquizz():
		respuesta = input("La carpeta LoGaQuizz_Neo no existe. ¿Desea instalar el programa? (y/n): ")
		if respuesta.lower() == 'y':
			instalar_backend()
			instalar_frontend()
			print("Programa instalado correctamente.")
			menu_existente()
	else:
		menu_existente()

def main():
	preguntar_instalar()

if __name__ == "__main__":
	main()