import asyncio
import mysql.connector
from datetime import datetime

#LIMITANTES
#
#debe ser ejecutado con versiones de python igual o superiores a la 3.7
#El largo máximo de caracteres leído es de 10
#
#

async def handle_telnet():
    #Datos de conexión
    #host = '192.168.32.242'  
    host = '192.168.0.2'  
    port = 2001
    try:
        reader, writer = await asyncio.open_connection(host, port)
        today = datetime.now().strftime("%Y-%m-%d")
        print(f"Conectado a {host}:{port}")
        with open(f"logs/{today}.log", "a") as archivo:
            archivo.write(f"{datetime.now().strftime('%d-%m-%Y %H:%M:%S')} - Iniciando captura e inserción. \n")
            archivo.write(f"{datetime.now().strftime('%d-%m-%Y %H:%M:%S')} - Conectado a cámara {host}:{port}\n")               
        # Leer los datos recibidos
        while True:
            today = datetime.now().strftime("%Y-%m-%d")
            try:
                # Esperar datos con un límite de tiempo de 1200 segundos (20 minutos)
                data = await asyncio.wait_for(reader.read(20), timeout=1200)
                with open(f"logs/{today}.log", "a") as archivo:
                    archivo.write(f' {datetime.now().strftime("%d-%m-%Y %H:%M:%S")} - Datos recibidos desde cámara.\n')

            except asyncio.TimeoutError:
                print(f' {datetime.now().strftime("%d-%m-%Y %H:%M:%S")} - Se ha superado el tiempo de espera sin recibir datos. Cerrando la conexión.')
                today = datetime.now().strftime("%Y-%m-%d")
                with open(f"logs/{today}.log", "a") as archivo:
                    archivo.write(f' {datetime.now().strftime("%d-%m-%Y %H:%M:%S")} - Se ha superado el tiempo de espera sin recibir datos. Cerrando la conexión.\n')
                continue
            except asyncio.CancelledError:
                print("Conexión cancelada por el usuario.")
                with open(f"logs/{today}.log", "a") as archivo:
                    archivo.write(datetime.now().strftime("%d-%m-%Y %H:%M:%S") + " - Conexión cancelada por el usuario.\n")
                break
            
            else:
                if not data:
                    break
                data = await reader.read(12)  # Lee hasta 10 bytes
                if not data:
                    break

                # Abrir conexión a la base de datos
                #conexion = mysql.connector.connect(
                    # host="localhost",
                    # user="root",
                    # password="Standrews2024.",
                    # password="Antalis2024.",
                    # database="spt")
                try:
                    #codigoProducto = data.decode(encoding='UTF-8',errors='strict')[-3:-1]
                    codigoProducto = data.decode(encoding='UTF-8',errors='strict')
                    #consulta = f"INSERT INTO spt.produccion (valProduccion, created_at) VALUES ('{codigoProducto}','{ahora}')"
                    
                    #cursor = conexion.cursor()
                    #cursor.execute(consulta)
                    #conexion.commit()
                    with open(f"logs/datos_{today}.log", "a") as archivo:
                        archivo.write(datetime.now().strftime("%d-%m-%Y %H:%M:%S") + ";" + codigoProducto + "\n")
                    with open(f"logs/{today}.log", "a") as archivo:
                        archivo.write(datetime.now().strftime("%d-%m-%Y %H:%M:%S") + " - " + codigoProducto + " insertado correctamente.\n")
                    print(datetime.now().strftime("%d-%m-%Y %H:%M:%S.%f")+ " " + codigoProducto + " insertado correctamente.")
                    # Cerrar conexión a la base de datos
                    #cursor.close()
                    #conexion.close()
                except:
                    print(datetime.now().strftime("%d-%m-%Y %H:%M:%S") + " - " + "error")
                    
    except asyncio.CancelledError:
            print(datetime.now().strftime("%d-%m-%Y %H:%M:%S") + " - " + "Conexión cancelada por el usuario.")
    finally:
        writer.close()  # Cerrar la conexión

async def main():
    try:
        await handle_telnet()
    except KeyboardInterrupt:
        print("Programa cerrado por el usuario.")
        # Registrar el evento de cierre del programa en el archivo de registro
        today = datetime.now().strftime("%Y-%m-%d")
        with open(f"logs/{today}.log", "a") as archivo:
            archivo.write(f"{datetime.now().strftime('%d-%m-%Y %H:%M:%S')} - Programa cerrado por el usuario.\n")

if __name__ == "__main__":
    asyncio.run(main())
