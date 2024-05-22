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
    host = '192.168.32.242'  
    port = 23
    try:
        reader, writer = await asyncio.open_connection(host, port)
        today = datetime.now().strftime("%Y-%m-%d")
        print(f"Conectado a {host}:{port}")
        
        # Leer los datos recibidos
        while True:
            today = datetime.now().strftime("%Y-%m-%d")
            try:
                # Esperar datos con un límite de tiempo de 1200 segundos (20 minutos)
                data = await asyncio.wait_for(reader.read(12), timeout=1200)
                print(str(data))               
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
                try:
                    codigoProducto = data.decode(encoding='UTF-8',errors='strict')[-3:-1]                    
                    print(codigoProducto + " insertado correctamente.")                    
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
        
        
if __name__ == "__main__":
    asyncio.run(main())
