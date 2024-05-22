import schedule
import time
import mysql.connector

def read_and_write_to_mysql():
    print("HOLA")
    # Lee registros del archivo y escribe en la base de datos MySQL
    try:
        # Abrir el archivo para lectura
        with open('result_codes.log', 'r') as file:
            print("Archivo abierto")
            # Conectar a la base de datos MySQL
            # connection = mysql.connector.connect(
            #     host='localhost',
            #     user='root',
            #     password='Standrews2024.',
            #     database='spt'
            # )

            #cursor = connection.cursor()

            # Iterar sobre las líneas del archivo
            for line in file:
                # Dividir la línea en partes (suponiendo que los registros están separados por comas)
                parts = line.strip().split('|')

                # Verificar si el registro ya existe en la base de datos
                # cursor.execute("SELECT COUNT(created_at) FROM produccion WHERE created_at = %s", (parts[1]))
                # result = cursor.fetchone()

                # # Si el registro no existe, insertarlo en la base de datos
                # if result[0] == 0:
                #     cursor.execute("INSERT INTO produccion ( created_at, valProduccion) VALUES (%s, %s)", (parts[0], parts[1]))
                print(parts[1][1:])
            # Commit para guardar los cambios en la base de datos
            #connection.commit()

            # Cerrar la conexión
            #connection.close()

            print("Registros escritos en la base de datos exitosamente.")
    except Exception as e:
        print(f"Error al escribir registros en la base de datos: {e}")

# Programar la ejecución de la función cada hora
schedule.every(10).seconds.do(read_and_write_to_mysql)

while True:
    # Ejecutar tareas programadas
    schedule.run_pending()
    time.sleep(1)  # Dormir durante 1 segundo
