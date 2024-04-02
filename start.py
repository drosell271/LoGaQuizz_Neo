import subprocess
import os
import psutil
from tqdm import tqdm
import sys

def obtener_color_porcentaje(porcentaje):
    if porcentaje < 85:
        return '\033[92m'  # Verde
    else:
        return '\033[91m'  # Rojo

def limpiar_pantalla():
    # Verificar el sistema operativo y ejecutar el comando correspondiente para limpiar la pantalla
    if os.name == 'nt':  # Windows
        subprocess.call('cls', shell=True)
    else:  # Unix (Linux, macOS)
        subprocess.call('clear', shell=True)

def lanzar_comandos_en_paralelo(comando1=None, comando2=None):
    if comando1 is None:
        comando1 = "npm start"
    if comando2 is None:
        comando2 = ".\\venv\\Scripts\\activate && python ./app/main.py"

    proceso1 = None
    proceso2 = None
    
    try:
        # Iniciar proceso para el primer comando
        proceso1 = subprocess.Popen(comando1, shell=True, cwd="./frontend", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Iniciar proceso para el segundo comando
        proceso2 = subprocess.Popen(comando2, shell=True, cwd="./backend", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # Esperar a que ambos procesos terminen
        while proceso1.poll() is None or proceso2.poll() is None:
            # Limpiar la pantalla antes de imprimir las nuevas medidas
            limpiar_pantalla()

            # Obtener estadísticas de uso de CPU y memoria
            cpu_percent = psutil.cpu_percent()
            memory_percent = psutil.virtual_memory().percent

            # Obtener el color correspondiente para la barra de progreso de CPU
            color_cpu = obtener_color_porcentaje(cpu_percent)
            # Imprimir la barra de progreso con el uso de CPU
            barra_cpu = '#' * int(cpu_percent / 2)
            print(f"CPU:     [{color_cpu}{barra_cpu:<50}\033[0m] {cpu_percent:5.1f}%")

            # Obtener el color correspondiente para la barra de progreso de memoria
            color_memoria = obtener_color_porcentaje(memory_percent)
            # Imprimir la barra de progreso con el uso de memoria
            barra_memoria = '#' * int(memory_percent / 2)
            print(f"Memoria: [{color_memoria}{barra_memoria:<50}\033[0m] {memory_percent:5.1f}%")

            # Esperar un segundo antes de volver a verificar las estadísticas
            psutil.cpu_percent(interval=1)
        
        # Mostrar mensaje indicando que los procesos han finalizado
        print("\nProcesos finalizados.")

    except KeyboardInterrupt:
        confirmar_salida = input("\n¿Estás seguro de que deseas salir? (y/n): ")
        if confirmar_salida.lower() == 'y':
            # Cerrar los procesos si el usuario confirma la salida
            if proceso1:
                proceso1.terminate()
            if proceso2:
                proceso2.terminate()
            print("Procesos interrumpidos. Saliendo...")
        else:
            # Continuar esperando si el usuario decide no salir
            lanzar_comandos_en_paralelo(comando1, comando2)

# Llamar a la función sin especificar comandos
lanzar_comandos_en_paralelo()
