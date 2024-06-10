import socket
import threading
import os
import re
import json
import argparse
import shutil
import time


global reciveJson_server

def receive_file_fragmentMultipleServers(host, port, directory, video_name, num_parts, part_index, video_size):
    print(f"Conectando a {host}:{port} para descargar la parte {part_index} de {num_parts} de {video_name}")
   
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        try:
            sock.connect((host, port))
            solicitud = f"VIDEO,{video_name},{num_parts},{part_index}"
            sock.sendall(solicitud.encode())

            file_name = sock.recv(1024).decode().strip()
            if not file_name:
                print("No se recibió el nombre del archivo correctamente.")
                return
            
            print(f"Recibiendo {file_name}")
            filepath = os.path.join(directory, file_name)
            sock.sendall(b"OK")
            with open(filepath, "wb") as file:
                while True:
                    data = sock.recv(1024)
                    if not data:
                        break
                    file.write(data)
        except Exception as e:
            print(f"Error al recibir el fragmento del archivo: {e}")
            
            
            
            
def receive_file_fragment(host, port, directory, video_name, num_parts, part_index, video_size):
    print(f"Conectando a {host}:{port} para descargar la parte {part_index} de {num_parts} de {video_name}")
   
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        try:
            sock.connect((host, port))
            solicitud = f"VIDEO,{video_name},{num_parts},{part_index}"
            sock.sendall(solicitud.encode())

            file_name = sock.recv(1024).decode().strip()
            if not file_name:
                print("No se recibió el nombre del archivo correctamente.")
                return
            
            print(f"Recibiendo {file_name}")
            filepath = os.path.join(directory, file_name)
            sock.sendall(b"OK")
            
            with open(filepath, "wb") as file:
                while True:
                    data = sock.recv(1024)
                    if not data:
                        break
                    file.write(data)
        except Exception as e:
            print(f"Error al recibir el fragmento del archivo: {e}")
              
                
def download_vid(servers, temp_directory):
    threads = []
    start_time = time.time()
    multiple_servers = False

    # Verificar si hay múltiples servidores
    for host, port, video_name, num_parts, part_index, video_size in servers:
        if video_size != 0:
            multiple_servers = True
        break

    if multiple_servers:
        print("Descargando video de múltiples servidores...")
        for host, port, video_name, num_parts, part_index, video_size in servers:
            thread = threading.Thread(target=receive_file_fragmentMultipleServers, args=(host, port, temp_directory, video_name, num_parts, part_index, video_size))
            threads.append(thread)
            thread.start()
    else:
        print("Descargando video de un solo servidor...")
        host, port, video_name, num_parts, part_index, video_size = servers[0]
        thread = threading.Thread(target=receive_file_fragment, args=(host, port, temp_directory, video_name, num_parts, part_index, video_size))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()
    
    end_time = time.time()
    duration = end_time - start_time
    print(f"Descarga completada en {duration:.2f} segundos.")

        
        
def start_client(host, port):
    c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    c.connect((host, port))
    msg_received = c.recv(1024)
    
    recive_json = json.loads(msg_received.decode('utf8'))
    c.close()
    recive_json_server = recive_json
    return recive_json

def combine_vid(temp_directory):
    received_files = [f for f in os.listdir(temp_directory) if os.path.isfile(os.path.join(temp_directory, f))]
    
    # Filtrar solo los archivos que coinciden con el formato esperado
    received_files = [f for f in received_files if re.search(r"_part(\d+)\.bin", f)]
    
    # Verificar si se recibieron archivos
    if not received_files:
        print("No se recibieron archivos válidos para combinar.")
        return
    
    sorted_files = sorted(received_files, key=lambda x: int(re.search(r"_part(\d+)\.bin", x).group(1)))

    output_video_path = "videosCliente/video_final.mp4"
    os.makedirs(os.path.dirname(output_video_path), exist_ok=True)
    with open(output_video_path, "wb") as outfile:
        for f in sorted_files:
            with open(os.path.join(temp_directory, f), "rb") as infile:
                outfile.write(infile.read())

    # Eliminar archivos temporales y directorio
    for f in sorted_files:
        os.remove(os.path.join(temp_directory, f))
    if not os.listdir(temp_directory):
        shutil.rmtree(temp_directory)

    print("La combinación de archivos se realizó con éxito.")
    
#return the size of the video

def searchVideoName(video_name, servers):
    for server_name, server_info in servers.items():
        for video in server_info['videos']:
            if video['name'] == video_name:
                return video['size']
    return 0

def print_servers_info(servers):
    for server_name, server_info in servers.items():
        print(f"Server Name: {server_name}")
        print(f"  IP Address: {server_info['ip']}")
        print(f"  IP port: {server_info['port']}")
        print(f"  Videos: {server_info['videos']}\n")

if __name__ == "__main__":
    
    temp_directory = "temp_parts"
    os.makedirs(temp_directory, exist_ok=True)
    
    
    
    parser = argparse.ArgumentParser(description='Cliente')
    parser.add_argument('--servers', help='Lista de servidores', action='store_true')
    parser.add_argument('--lsvid', help='Lista de videos', action='store_true')
    parser.add_argument('-v', type=str , help='Opcion de video a descargar')
    parser.add_argument('-d', help='Descargar video', action='store_true')
    parser.add_argument('-s',type=str, help='Servidor a conectarse')
    parser.add_argument('-p',type=int, help='Puerto a conectarse')
    parser.add_argument('-cs',type=str, help='Conectar a servidor central')
    parser.add_argument('-cp',type=int, help='Puerto a conectarse del servidor central')
    
    
    
    
    args = parser.parse_args()
    
    host = args.cs
    port = args.cp
    reciveJson = start_client(host, port)
    
    if args.servers:
        print_servers_info(reciveJson)
    if args.lsvid:
        print("Lista de los nombres de los videos disponibles en cada servidor:")
        for server_name, server_info in reciveJson.items():
            print(f"Server Name: {server_name}")
            print(f"Server IP: {server_info['ip']}")
            print(f"Server Port: {server_info['port']}")

            
            print(f"Video Names:")
            for video in server_info['videos']:
                print(f"  {video['name']}")
            
    if args.d:
        if args.p is None and args.s is None:
            video_name = args.v
            servers = []
            part_index = 1

            for server_name, server_info in reciveJson.items():
                for video in server_info['videos']:
                    if video['name'] == video_name:
                        servers.append((server_info['ip'], server_info['port'], video['name'], len(reciveJson), part_index, video['size']))
                        part_index += 1
            
            if not servers:
                print(f"No se encontraron servidores que contengan el video {video_name}")
            else:
                download_vid(servers, temp_directory)
                combine_vid(temp_directory)
        else:
            size = int(searchVideoName(args.v, reciveJson))
            print(size)
            servers = [(args.s, args.p, args.v, 1, 1, size)]
            
            download_vid(servers, temp_directory)
            combine_vid(temp_directory)
            print(f"Video {args.v} descargado exitosamente.")
