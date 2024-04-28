import socket
import os

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

# Ejemplos para diferentes servidores:
# send_file_fragment("localhost", 12345, "videospc1")
# send_file_fragment("localhost", 12346, "videospc2")

def connectionCentralServer(host, port):
    c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    c.connect((host, port))
    c.close()

if __name__ == "__main__":
    host = "192.168.0.13"
    port = 33330
    connectionCentralServer(host, port)
