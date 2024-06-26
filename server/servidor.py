import json
import socket
import os
from threading import Thread

def send_file_fragment(host, port, base_directory):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((host, port))
        server_socket.listen()
        print(f"Servidor escuchando en {host}:{port}")
        conn, _ = server_socket.accept()
        with conn:
            solicitud = conn.recv(1024).decode().split(',')
            video_name, num_parts, part_index = solicitud
            num_parts = int(num_parts)
            part_index = int(part_index)
            print(f"Enviando parte {part_index} de {num_parts} de {video_name}")

            video_path = os.path.join(base_directory, video_name)
            with open(video_path, 'rb') as file:
                content = file.read()

            part_size = len(content) // num_parts
            start = (part_index - 1) * part_size
            end = start + part_size if part_index < num_parts else len(content)
            part = content[start:end]

            filename = f"{video_name}_part{part_index}.bin"
            conn.sendall(filename.encode())
            conn.recv(1024)
            conn.sendall(part)
           
                                   
def handle_request(conn, base_directory):
    try:
        solicitud = conn.recv(1024).decode()
        if solicitud == "PING":
            conn.sendall(b"PONG")
        elif solicitud == "INFO":
            video_names = get_video_names(os.path.join(base_directory, "videos"))
            response = {"videos": video_names}
            conn.sendall(json.dumps(response).encode())
        else:
            parts = solicitud.split(',')
            if parts[0] == "VIDEO" and len(parts) == 4:
                video_name, num_parts, part_index = parts[1], int(parts[2]), int(parts[3])
                directory_videos = os.path.join(base_directory, "videos")
                print("Ruta de los videos: ", directory_videos)
                print(f"Enviando parte {part_index} de {num_parts} de {video_name} desde {base_directory}")

                video_path = os.path.join(directory_videos, video_name)
                if not os.path.exists(video_path):
                    print(f"Archivo {video_name} no encontrado.")
                    conn.close()
                    return

                with open(video_path, 'rb') as file:
                    content = file.read()

                part_size = len(content) // num_parts
                start = (part_index - 1) * part_size
                end = start + part_size if part_index < num_parts else len(content)
                part = content[start:end]
                print(f"Enviando parte {part_index} de {num_parts} de {video_name}, con tamaño: {len(part)} bytes")
                
                # Enviar el nombre del archivo al cliente
                filename = f"{video_name}_part{part_index}.bin"
                conn.sendall(filename.encode())
                confirmation = conn.recv(1024).decode().strip()
                
                if confirmation == "OK":
                    # Enviar el fragmento del archivo al cliente
                    conn.sendall(part)
                else:
                    print("El cliente no está listo para recibir el archivo.")
    except Exception as e:
        print(f"Error al manejar la solicitud del cliente: {e}")
    finally:
        conn.close()

def get_video_names(videos_directory):
    video_names = []
    for filename in os.listdir(videos_directory):
        if os.path.isfile(os.path.join(videos_directory, filename)):
            video_names.append(filename)
    return video_names

def connection_central_server(host, port, base_directory):
    try:
        c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        c.connect((host, port))
        info = {"port": portServerVideo, "videos": get_video_names(os.path.join(base_directory, "videos"))}
        data = json.dumps(info)
        c.send(data.encode())
        c.close()
    except Exception as e:
        print(f"Error al conectar con el servidor central: {e}")

def start_server(host, port, base_directory):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    s.listen(5)
    print(f"El servidor de video está escuchando en {host}:{port}")

    while True:
        conn, addr = s.accept()
        print(f"Conexión establecida con: {addr}")
        thread = Thread(target=handle_request, args=(conn, base_directory))
        thread.start()

if __name__ == "__main__":
    print("Ingrese la dirección IP y puerto del servidor de video ")
    print("==============================================")

    hostServerVideo = input("Dirección IP del servidor de video: ")
    portServerVideo = int(input("Puerto del servidor de video: "))
    print("==============================================")
    
    print("Ingrese la dirección IP y puerto del servidor central.")
    hostCentralServer = input("Dirección IP del servidor central: ")
    portCentralServer = int(input("Puerto del servidor central: "))
    
    baseDirectory = os.path.dirname(os.path.abspath(__file__))
    
    try:
        central_server_thread = Thread(target=connection_central_server, args=(hostCentralServer, portCentralServer, baseDirectory))
        central_server_thread.start()
        
        video_server_thread = Thread(target=start_server, args=(hostServerVideo, portServerVideo, baseDirectory))
        video_server_thread.start()

        # Unirse a los hilos para asegurar que se cierren correctamente
        central_server_thread.join()
        video_server_thread.join()
    except Exception as e:
        print(f"Error al iniciar los hilos: {e}")
    finally:
        print("Cerrando servidor de video.")