import asyncio
import mysql.connector
from datetime import datetime

#LIMITANTES
#
#
#Debe ser ejecutado con versiones de python igual o superiores a la 3.7
#El largo máximo de caracteres leído es de 10
#
#

async def handle_telnet():
    #Datos de conexión
    # host = '192.168.32.242'  
    # port = 23
    host = '192.168.0.2'  
    port = 2001
    while True:
        try:
            reader, writer = await asyncio.open_connection(host, port)
            print(f"Conectado a {host}:{port}")
            today = datetime.now().strftime("%Y-%m-%d")
            with open(f"logs/{today}.log", "a", encoding='utf-8') as archivo:
                archivo.write(f"{datetime.now().strftime('%d-%m-%Y %H:%M:%S')} - Iniciando captura e inserción. \n")
                archivo.write(f"{datetime.now().strftime('%d-%m-%Y %H:%M:%S')} - Conectado a cámara {host}:{port}\n")
            # Leer los datos recibidos
            while True:
                try:
                    # Esperar datos con un límite de tiempo de 1200 segundos (20 minutos)
                    with open(f"logs/{today}.log", "a", encoding='utf-8') as archivo:
                        archivo.write(f'{datetime.now().strftime("%d-%m-%Y %H:%M:%S")} - Esperando datos desde cámara.\n')
                    data = await asyncio.wait_for(reader.read(12), timeout=1200)
                    print("data: " + str(data))
                    # Esperar datos con un límite de tiempo de 1200 segundos (20 minutos)
                    with open(f"logs/{today}.log", "a", encoding='utf-8') as archivo:
                        archivo.write(f'{datetime.now().strftime("%d-%m-%Y %H:%M:%S")} - {str(data)} leído desde cámara.\n')
                    
                    codigoProducto = data.decode(encoding='utf-8')
                    print("codigo producto: " + codigoProducto)
                    
                    with open(f"logs/{today}.log", "a", encoding='utf-8') as archivo:
                        archivo.write(f'{datetime.now().strftime("%d-%m-%Y %H:%M:%S")} - Datos recibidos desde cámara.\n')
                except asyncio.TimeoutError:
                    print(f'{datetime.now().strftime("%d-%m-%Y %H:%M:%S")} - Se ha superado el tiempo de espera sin recibir datos. Cerrando la conexión.')
                    today = datetime.now().strftime("%Y-%m-%d")
                    with open(f"logs/{today}.log", "a", encoding='utf-8') as archivo:
                        archivo.write(f' {datetime.now().strftime("%d-%m-%Y %H:%M:%S")} - Se ha superado el tiempo de espera sin recibir datos. Cerrando la conexión.\n')
                    continue
                except asyncio.CancelledError:
                    print("Conexión cancelada por el usuario.")
                    with open(f"logs/{today}.log", "a", encoding='utf-8') as archivo:
                        archivo.write(datetime.now().strftime("%d-%m-%Y %H:%M:%S") + " - Conexión cancelada por el usuario.\n")
                    break                
                else:
                    if not data:
                        break
                    data = await reader.read(12)  # Lee hasta 10 bytes
                    if not data:
                        break

                    # Abrir conexión a la base de datos
                    conexion = mysql.connector.connect(
                        host="localhost",
                        user="root",
                        #password="Standrews2024.",
                        password="Antalis2024.",
                        database="spt"
                    )
                    
                    cursor = conexion.cursor()
                    ahora = datetime.now()
                    turno = f"SELECT idturno, nombre, inicio, termino, minutos FROM spt.Turno WHERE Planta_idPlanta = 5 AND Planta_Cliente_idCliente = 2 AND estado = 1 AND ((inicio <= '{ahora.time().strftime('%H:%M:%S')}' AND termino >= '{ahora.time().strftime('%H:%M:%S')}') OR (inicio >= termino AND (inicio <= '{ahora.time().strftime('%H:%M:%S')}' OR termino >= '{ahora.time().strftime('%H:%M:%S')}')))"
                    #print("QUERY turno " + turno)
                    cursor.execute(turno)
                    resultados = cursor.fetchall()
                    try:
                        idTurno = int(resultados[0][0])
                        codigoProducto = data.decode(encoding='UTF-8',errors='strict')[-3:-1]
                        print("codigo producto:" + codigoProducto)
                        codProducto = codigoProducto
                        absurdo = f"SELECT idProducto FROM spt.producto WHERE codigo = '{codProducto}'"
                        cursor.execute(absurdo)
                        resultados = cursor.fetchall()
                        if(len(resultados) >= 0):                
                            idProducto = int(resultados[0][0])
                            idGrupoLinea = f"SELECT idGrupoLinea FROM grupoLinea;"
                            cursor.execute(idGrupoLinea)
                            resultados = cursor.fetchall()
                            idGrupoLinea = int(resultados[0][0])
                            idPlanta = f"SELECT idPlanta FROM planta;"
                            cursor.execute(idPlanta)
                            resultados = cursor.fetchall()
                            idPlanta = int(resultados[0][0])
                            idCliente = f"SELECT idCliente FROM cliente;"
                            cursor.execute(idCliente)
                            resultados = cursor.fetchall()
                            idCliente = int(resultados[0][0])
                            consulta = f"INSERT INTO spt.produccion (valProduccion, created_at, Turno_idTurno, Producto_idProducto, Linea_GrupoLinea_idGrupoLinea, Linea_GrupoLinea_Planta_idPlanta, Linea_GrupoLinea_Planta_Cliente_idCliente) VALUES ('{codigoProducto}','{ahora}',{idTurno},{idProducto}, {idGrupoLinea}, {idPlanta}, {idCliente})"
                            print(codProducto + " insertado correctamente.")
                            with open(f"logs/{today}.log", "a", encoding='utf-8') as archivo:
                                archivo.write(datetime.now().strftime("%d-%m-%Y %H:%M:%S") + " - " + codProducto + " insertado correctamente.\n")                            
                        else:
                            consulta = f"INSERT INTO spt.produccion (valProduccion, created_at, Turno_idTurno, Producto_idProducto, Linea_GrupoLinea_idGrupoLinea, Linea_GrupoLinea_Planta_idPlanta, Linea_GrupoLinea_Planta_Cliente_idCliente) VALUES ('{0}','{ahora}',{idTurno},{0}, {idGrupoLinea}, {idPlanta}, {idCliente})"
                            print(datetime.now().strftime("%d-%m-%Y %H:%M:%S") + " - " + "No leído")
                        cursor.execute(consulta)
                        conexion.commit()
                        # Cerrar conexión a la base de datos
                        cursor.close()
                        conexion.close()
                    except:
                        print(datetime.now().strftime("%d-%m-%Y %H:%M:%S") + " - " + "error")
                        with open(f"logs/{today}.log", "a", encoding='utf-8') as archivo:
                            archivo.write(datetime.now().strftime("%d-%m-%Y %H:%M:%S") + " - " + consulta + ".\n")
        except asyncio.CancelledError:
                print(datetime.now().strftime("%d-%m-%Y %H:%M:%S") + " - " + "Conexión cancelada por el usuario.")        
        except Exception as e:
            print(f"Error de conexión: {e}")
            await asyncio.sleep(10)  # Esperar un tiempo antes de intentar la reconexión
            today = datetime.now().strftime("%Y-%m-%d")
            with open(f"logs/{today}.log", "a", encoding='utf-8') as archivo:
                archivo.write(f"{datetime.now().strftime('%d-%m-%Y %H:%M:%S')} - Error de conexión: " + str(e) + "\n")
    
async def main():
    try:
        await handle_telnet()
    except KeyboardInterrupt:
        print("Programa cerrado por el usuario.")
        # Registrar el evento de cierre del programa en el archivo de registro
        today = datetime.now().strftime("%Y-%m-%d")
        with open(f"logs/{today}.log", "a", encoding='utf-8') as archivo:
            archivo.write(f"{datetime.now().strftime('%d-%m-%Y %H:%M:%S')} - Programa cerrado por el usuario.\n")
            
if __name__ == "__main__":
    asyncio.run(main())