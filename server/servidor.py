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


def get_video_names(videos_directory):
    video_names = []
    for filename in os.listdir(videos_directory):
        if os.path.isfile(os.path.join(videos_directory, filename)):
            video_names.append(filename)
    return video_names

def connectionCentralServer(host, port, base_directory):
    c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    c.connect((host, port))
    # envia el puerto y los videos de get_video_names, todo en un json
    info = {"port": portServerVideo, "videos": get_video_names(os.path.join(base_directory, "videos"))}
    data = json.dumps(info)
    c.send(data.encode())
    c.close()



def start_server(host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    s.listen(5)

    print(f"El servidor intermediario está escuchando en {host}:{port}")
    while True:
        # Establecer conexión
        c, addr = s.accept()
        print(f"Se estableció conexión con: {addr}")
        # Recibir dirección IP del servidor
        ip_received,_ = addr
        print(f"Dirección IP recibida: {ip_received}")
        videos = get_video_names(os.path.join(baseDirectory, "videos"))
        c.send(json.dumps({"port": portServerVideo, "videos": videos}).encode())
        
        c.close()



if __name__ == "__main__":
    
    hostServerVideo = "10.251.45.151"
    portServerVideo = 33332
    
    hostCentralServer = "10.251.45.151"
    portCentralServer = 33330
    baseDirectory = os.path.dirname(os.path.abspath(__file__))
    server_thread = Thread(target=start_server, args=(hostServerVideo, portServerVideo))
    server_thread.start()
    connectionCentralServer(hostCentralServer, portCentralServer,baseDirectory)
    videoDirectory = os.path.join(baseDirectory, "videos")
    print(get_video_names(videoDirectory))
    
