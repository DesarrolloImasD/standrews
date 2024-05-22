import tkinter as tk
from connect import connect_to_database  # Import the function from connect.py

import threading
import socket
import re
import time
from datetime import datetime

def on_escape(root):
    root.destroy()

def get_lineas_from_database(db_connection):
    try:
        cursor = db_connection.cursor()
        query = "SELECT id, nombre, ip, activa FROM LINEA;"
        cursor.execute(query)
        return cursor.fetchall()
    except Exception as e:
        print(f"Error fetching LINEA records: {e}")
        return []

def create_gui():
    # Create the main Tkinter window
    root = tk.Tk()
    root.title("Tkinter GUI")

    # Bind the 'Escape' key to the on_escape function
    root.bind('<Escape>', lambda event: on_escape(root))

    # Set the initial size to maximize the window
    window_width = root.winfo_screenwidth()
    window_height = int(root.winfo_screenheight() * 0.9)  # Reduced height to 90%
    root.geometry(f"{window_width}x{window_height}+0+0")

    # Set a margin for the container frame
    margin = 20

    # Add a title label above the container frame
    title_label = tk.Label(root, text="Lineas", font=("Helvetica", 16))
    title_label.pack(pady=(margin, 0))  # Add margin only at the bottom

    # Create a Frame to contain the boxes
    container_frame = tk.Frame(root)
    container_frame.pack(expand=True, fill="both", padx=margin, pady=0)  # Set pady to 0

    # Connect to the database
    db_connection = connect_to_database()

    # Retrieve LINEA records from the database
    lineas = get_lineas_from_database(db_connection)
    db_connection.close()

    # Add a box for each LINEA record
    for linea in lineas:
        box_frame = tk.Frame(container_frame, width=90, height=90, borderwidth=2, relief="solid")
        box_frame.grid(row=(linea[0] - 1) // 5, column=(linea[0] - 1) % 5, padx=2, pady=2, sticky="nsew")

        # Add a title label inside each box
        title_label = tk.Label(box_frame, text=f"Linea {linea[1]}", font=("Helvetica", 10))
        title_label.pack()

        # Add an IP label inside each box
        ip_label = tk.Label(box_frame, text=f"IP: {linea[2]}", font=("Helvetica", 8))
        ip_label.pack()

        # Check if 'activa' is True, set bg to black and font color to white
        if linea[3]:
            box_frame.configure(bg="black")
            title_label.configure(fg="white", bg="black")
            ip_label.configure(fg="white", bg="black")

    # Close the database connection
    # db_connection.close()

    # Configure row and column weights to make the boxes expandable
    for i in range(5):  # Configure 5 columns
        container_frame.grid_columnconfigure(i, weight=1)

    for i in range((len(lineas) - 1) // 5 + 1):  # Configure rows based on the number of boxes
        container_frame.grid_rowconfigure(i, weight=1)

    # Extract IP addresses from LINEA records
    lantronix_ips = [linea[2] for linea in lineas]

    return root, container_frame, lantronix_ips

def get_latest_lote(db_connection):
    try:
        cursor = db_connection.cursor()
        query = "SELECT TOP 1 LOTE FROM LOTE ORDER BY FECHA DESC;"
        cursor.execute(query)
        row = cursor.fetchone()
        cursor.close()

        if row:
            return row.LOTE
        else:
            return None
        
        
    except Exception as e:
        print(f"Error fetching latest LOTE value: {e}")
        return None
    
def insert_into_caja(db_connection, lote, sel, cal, pes, cpes, emb, temb, cor, cemb):
    try:
        cursor = db_connection.cursor()

        # Get the current datetime
        current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Define the SQL query for insertion
        query = """
            INSERT INTO CAJA (CJNUMLOTE, CJCODSELE, CJCODCALI, CJCODPESA, CJCODPESO, CJCODEMBA, CJCODTEMB, CJFECHA, CJHORA, CJNUMCORR, TIPOEMBA)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """

        # Execute the query with the provided values
        cursor.execute(query, (lote, sel, cal, pes, cpes, emb, temb, current_datetime, current_datetime, cor, cemb))

        # Commit the changes to the database
        db_connection.commit()

        print("Inserted into CAJA table successfully.")

    except Exception as e:
        print(f"Error inserting into CAJA table: {e}")

def update_caja(db_connection, lote, sel, cal, pes, cpes, emb, temb, cor, cemb):
    try:
        cursor = db_connection.cursor()

        # Get the current datetime
        current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Define the SQL query for updating
        query = """
            UPDATE CAJA
            SET CJNUMLOTE = ?,CJCODSELE = ?, CJCODCALI = ?, CJCODPESA = ?, CJCODPESO = ?, CJCODEMBA = ?, CJCODTEMB = ?, CJFECHA = ?, CJHORA = ?, TIPOEMBA = ?;
        """

        # Execute the query with the provided values
        cursor.execute(query, (lote, sel, cal, pes, cpes, emb, temb, current_datetime, current_datetime, cemb))

        # Commit the changes to the database
        db_connection.commit()
        # cursor.close()

        print("Updated CAJA table successfully.")

    except Exception as e:
        print(f"Error updating CAJA table: {e}")


def delete_caja(db_connection, cor):
    try:
        cursor = db_connection.cursor()
        # Define the SQL query for updating
        query = """
            DELETE FROM CAJA WHERE CJNUMCORR = ?;
        """

        # Execute the query with the provided values
        cursor.execute(query, (cor))

        # Commit the changes to the database
        db_connection.commit()
        # cursor.close()

        print("delete CAJA table successfully.")

    except Exception as e:
        print(f"Error deleting CAJA table: {e}")

# Function to update GUI
def update_gui(container_frame, line_number):
    box_frame = container_frame.grid_slaves(row=(line_number - 1) // 5, column=(line_number - 1) % 5)[0]
    box_frame.configure(bg="green")
    container_frame.after(500, lambda: box_frame.configure(bg="black"))



def connect_to_lantronix(ip, read_port, response_port, line_number, container_frame):
    print(f"Connecting to {ip}:{read_port}")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s_read:
        try:
            s_read.connect((ip, read_port))
            print(f"Connected to {ip}:{read_port}")

            while True:
                received_data = ""

                while True:
                    data_chunk = s_read.recv(1024).decode('utf-8')
                    if not data_chunk:
                        break

                    received_data += data_chunk

                    emb_match = re.search(r'/(.*?)-', received_data)
                    if not emb_match:
                        print("embalaje error de lectura")
                    sel_match = re.search(r'\+(.*?)-', received_data)
                    if not sel_match:
                        print("seleccion error de lectura")
                    cor_match = re.search(r'#(.*?)-', received_data)
                    if not cor_match:
                        print("correlativo error de lectura")
                    pes_match = re.search(r'\(.?)-', received_data)
                    if not pes_match:
                        print("pesaje error de lectura")

                    if emb_match and sel_match and cor_match and pes_match:

                        print("All patterns matched, emb_match: ",emb_match,"sel_match: ",sel_match,"cor_match: ", cor_match,"pes_match: ", pes_match  )

                        emb = emb_match.group(1)
                        sel = sel_match.group(1)
                        cor = cor_match.group(1)
                        pes = pes_match.group(1)
                        print("pes: >   >   >  ", pes)

                        emb = emb.split('-')[0]
                        cal = sel[-1]
                        sel = sel[:-1]
                        temb = emb[-1] 
                        cemb = emb[-7]                      
                        emb = emb[:-1]
                        cpes= pes[-1]
                        pes = pes[:-1]

                        print(f"emb: {emb}, temb: {temb}, sel: {sel}, cor: {cor}, cal: {cal}, pes: {pes}, cpes: {cpes}, cemb:{cemb}")

                        if emb and sel and cor and cal and pes:
                            response = f"Received: emb={emb}, sel={sel}, cor={cor}, cal={cal}, pes={pes}, cpes={cpes}, cemb={cemb}"

                            db_connection = connect_to_database()
                            if db_connection:
                                latest_lote = get_latest_lote(db_connection)
                                print(latest_lote)
                                # Check if a record with the given CJNUMCORR exists
                                cursor = db_connection.cursor()
                                check_query = "SELECT * FROM CAJA WHERE CJNUMCORR = ?;"

                                cursor.execute(check_query, (cor,))
                                existing_record = cursor.fetchone()
                                cursor.close()

                                if existing_record:
                                    print("existe ya el correlativo")
                                    
                                    delete_caja(db_connection, cor)
                                    insert_into_caja(db_connection, latest_lote, sel, cal, pes, cpes, emb, temb, cor, cemb)
                                    print(f"deleted then Inserted into CAJA table with CJNUMCORR={cor} successfully.")

                                    # Update GUI based on the line number
                                    container_frame.after(0, lambda: update_gui(container_frame, line_number))
                                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s_response:
                                        s_response.connect((ip, response_port))
                                        s_response.send(response.encode('utf-8'))
                                else:
                                    # If no record exists with the given CJNUMCORR, insert a new record
                                    insert_into_caja(db_connection, latest_lote, sel, cal, pes, cpes, emb, temb, cor, cemb)
                                    print(f"Inserted into CAJA table with CJNUMCORR={cor} successfully.")
                                    # Update GUI based on the line number
                                    container_frame.after(0, lambda: update_gui(container_frame, line_number))
                                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s_response:
                                        s_response.connect((ip, response_port))
                                        s_response.send(response.encode('utf-8'))

                            db_connection.close()

                        latest_lote, sel, cal, pes, cpes, emb, temb, cor, cemb = "", "", "", "", "", "", "", "", ""
                        received_data = ""
                    
        except Exception as e:
            print(f"Error: {e}")

if _name_ == "_main_":
    gui_root, container_frame, lantronix_ips = create_gui()

    read_port = 10001
    response_port = 10002

    threads = []

    for i, ip in enumerate(lantronix_ips):
        thread = threading.Thread(
            target=connect_to_lantronix,
            args=(ip, read_port, response_port, i + 1, container_frame),
            name=f"LantronixThread-{ip}"
        )
        thread.start()
        threads.append(thread)

    gui_root.mainloop()