import socket
import json
import os

def save_server_ip(ip_address, json_file_path):
    # Cargar datos existentes del archivo JSON o inicializar un diccionario vacío
    if os.path.exists(json_file_path):
        with open(json_file_path, 'r') as file:
            data = json.load(file)
    else:
        data = {}
    
    server_name = "server1"
    
    if server_name in data:
        data[server_name]["videos"].append(ip_address)
    else:
        data[server_name] = {"ip": ip_address, "videos": []}

    with open(json_file_path, 'w') as file:
        json.dump(data, file)


def send_file_content(client_socket, file_path):
    with open(file_path, 'r') as file:
        file_content = file.read()
        client_socket.send(file_content.encode('utf-8'))


def start_server(host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    s.listen(5)

    print(f"El servidor intermediario está escuchando en {host}:{port}")

    # Obtener la ruta del archivo .py que se está ejecutando
    script_dir = os.path.dirname(os.path.abspath(__file__))
    json_file_path = os.path.join(script_dir, "server_ips.json")

    while True:
        # Establecer conexión
        c, addr = s.accept()
        print(f"Se estableció conexión con: {addr}")

        # Recibir dirección IP del servidor
        ip_received = addr
        print(f"Dirección IP recibida: {ip_received}")

        # Guardar la dirección IP en el archivo JSON
        save_server_ip(ip_received, json_file_path)

        
        c.close()

def start_serverClient(host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    s.listen(5)
    
    print(f"El servidor intermediario está escuchando en {host}:{port}")
    
    while True:
        c, addr = s.accept()
        print(f"Se estableció conexión con: {addr}")
        script_dir = os.path.dirname(os.path.abspath(__file__))
        json_file_path = os.path.join(script_dir, "server_ips.json")
        send_file_content(c, json_file_path)
        c.close()

    

if __name__ == "__main__":
    host = ""  
    port = 33330
    portClient = 33331
    
    start_server(host, port)
    
    start_serverClient(host, portClient)
