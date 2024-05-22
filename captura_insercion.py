import asyncio

import mysql.connector
from datetime import datetime
import time

conexion = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Standrews2024.",
    database="spt"
)

#LIMITANTES
#
#
#Debe ser ejecutado con versiones de python igual o superiores a la 3.7
#El largo máximo de caracteres leído es de 10
#
#

async def handle_telnet():
    #Datos de conexión
    host = '192.168.32.242'  
    port = 23

    try:
        reader, writer = await asyncio.open_connection(host, port)
        print(f"Conectado a {host}:{port}")

        # Leer los datos recibidos
        while True:
            data = await reader.read(12)  # Lee hasta 10 bytes
            if not data:
                break
            cursor = conexion.cursor()

            ahora = datetime.now()
            turno = f"SELECT idturno, nombre, inicio, termino, minutos FROM spt.Turno WHERE Planta_idPlanta = 5 AND Planta_Cliente_idCliente = 2 AND estado = 1 AND ((inicio <= '{ahora.time().strftime("%H:%M:%S")}' AND termino >= '{ahora.time().strftime("%H:%M:%S")}') OR (inicio >= termino AND (inicio <= '{ahora.time().strftime("%H:%M:%S")}' OR termino >= '{ahora.time().strftime("%H:%M:%S")}')))"
            cursor.execute(turno)
            resultados = cursor.fetchall()
            idTurno = int(resultados[0][0])
            codigoProducto = data.decode(encoding='UTF-8',errors='strict')[-3:-1]
            codProducto = codigoProducto
            absurdo = """SELECT idProducto FROM spt.producto WHERE codigo = '""" + codProducto + """'"""
            cursor.execute(absurdo)
            resultados = cursor.fetchall()
            if(len(resultados) > 0):                
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
            else:
                consulta = f"INSERT INTO spt.produccion (valProduccion, created_at, Turno_idTurno, Producto_idProducto, Linea_GrupoLinea_idGrupoLinea, Linea_GrupoLinea_Planta_idPlanta, Linea_GrupoLinea_Planta_Cliente_idCliente) VALUES ('{0}','{ahora}',{idTurno},{0}, {idGrupoLinea}, {idPlanta}, {idCliente})"
                print("No leído")
            cursor.execute(consulta)
            conexion.commit()
        cursor.close()
        conexion.close()
    except asyncio.CancelledError:
        print("Conexión cancelada por el usuario.")
    finally:
        writer.close()  # Cerrar la conexión

async def main():
    await handle_telnet()

if __name__ == "__main__":
    asyncio.run(main())