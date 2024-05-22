import tkinter as tk
import asyncio
import telnetlib3

class TelnetApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Telnet App")
        
        self.text_area = tk.Text(self.root, height=20, width=50)
        self.text_area.pack(pady=10)
        
        self.connect_button = tk.Button(self.root, text="Conectar", command=self.connect_telnet)
        self.connect_button.pack(pady=5)
        
    async def connect_telnet(self):
        try:
            # Establecer la conexión Telnet
            async with telnetlib3.open_connection("192.168.32.242", 23) as stream:
                self.text_area.insert(tk.END, "Conexión establecida.\n")
                await self.receive_data(stream)
        except Exception as e:
            self.text_area.insert(tk.END, f"Error al conectar: {e}\n")
        
    async def receive_data(self, stream):
        try:
            # Recibir datos del servidor Telnet y mostrarlos en la interfaz
            async for line in stream:
                self.text_area.insert(tk.END, line.decode("utf-8"))
                self.text_area.see(tk.END)  # Desplazar automáticamente el texto al final
        except Exception as e:
            self.text_area.insert(tk.END, f"Error al recibir datos: {e}\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = TelnetApp(root)
    root.mainloop()
