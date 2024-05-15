import socket
import threading
import os
import re
import json
import argparse

def receive_file_fragment(host, port, directory, video_name, num_parts, part_index):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((host, port))
        solicitud = f"{video_name},{num_parts},{part_index}"
        sock.sendall(solicitud.encode())

        filename = sock.recv(1024).decode().strip()
        if not filename:
            print("No se recibió el nombre del archivo correctamente.")
            return

        filepath = os.path.join(directory, filename)
        sock.sendall(b"OK")

        with open(filepath, "wb") as file:
            while True:
                data = sock.recv(1024)
                if not data:
                    break
                file.write(data)


def downloadVid(servers, temp_directory):
    threads = []
    for host, port, video_name, num_parts, part_index in servers:
        thread = threading.Thread(target=receive_file_fragment, args=(
            host, port, temp_directory, video_name, num_parts, part_index))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()


def combineVid(temp_directory):
    received_files = [f for f in os.listdir(
        temp_directory) if os.path.isfile(os.path.join(temp_directory, f))]
    sorted_files = sorted(received_files, key=lambda x: int(
        re.search(r"p(\d+)", x).group(1)))

    output_video_path = "videosCliente/video_final.mp4"
    os.makedirs(os.path.dirname(output_video_path), exist_ok=True)
    with open(output_video_path, "wb") as outfile:
        for f in sorted_files:
            with open(os.path.join(temp_directory, f), "rb") as infile:
                outfile.write(infile.read())

    for f in sorted_files:
        os.remove(os.path.join(temp_directory, f))
    os.rmdir(temp_directory)


def startClient(host, port):
    c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    c.connect((host, port))
    msg_received = c.recv(1024)
    
    reciveJson = json.loads(msg_received.decode('utf8'))
    print(reciveJson)
    c.close()


if __name__ == "__main__":
    #Variables
    host = "192.168.0.14"
    port = 33331
    temp_directory = "temp_parts"
    os.makedirs(temp_directory, exist_ok=True)
    
    
    parser = argparse.ArgumentParser(description='Cliente')
    parser.add_argument('--servers', help='Lista de servidores', action='store_true')
    parser.add_argument('--lsvid', help='Lista de videos', action='store_true')
    parser.add_argument('--video', type=str , help='Opcion de video a descargar')
    parser.add_argument('--download', help='Descargar video', action='store_true')
    
    
    args = parser.parse_args()
    if args.servers:
        startClient(host, port)
    if args.lsvid:
        print("Lista de videos")
     
        
    #servers = [("localhost", 12345, "Appa-Night-Ride-4K-unido.mp4", 2, 2),
    #       ("localhost", 12346, "Appa-Night-Ride-4K-unido.mp4", 2, 1)]
    
    