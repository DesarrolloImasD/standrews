import asyncio

async def handle_client(reader, writer):
    addr = writer.get_extra_info('peername')
    print(f"Conexión establecida desde {addr}")

    while True:
        data = await reader.read(100)  # Ajusta el tamaño del búfer según tus necesidades
        if not data:
            break
        message = data.decode().strip()
        print(f"Datos recibidos desde {addr}: {message}")

    print(f"Conexión con {addr} cerrada")
    writer.close()

async def main():
    # Cambia la dirección IP y el puerto según tus necesidades
    server = await asyncio.start_server(handle_client, '192.168.0.2', 2001)

    addr = server.sockets[0].getsockname()
    print(f"Servidor TCP iniciado en {addr}")

    async with server:
        await server.serve_forever()

asyncio.run(main())
