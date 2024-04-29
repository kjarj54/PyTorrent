import socket
import json
import os
from threading import Thread
import time

#Metodo para hacer ping

def ping_servers(script_dir):
    json_file_path = os.path.join(script_dir, "server_ips.json")
    
    while True:
        # Cargar datos existentes del archivo JSON o inicializar un diccionario vacío
        if os.path.exists(json_file_path):
            with open(json_file_path, 'r') as file:
                data = json.load(file)
        else:
            data = {}

        servers_to_remove = []

        # Iterar sobre los servidores y realizar ping
        for server_name, server_info in data.items():
            ip_address = server_info.get("ip")
            if ip_address:
                response = os.system("ping -n 1 " + ip_address)
                if response != 0:  # Si el ping no fue exitoso
                    servers_to_remove.append(server_name)

        # Eliminar los servidores que no respondieron al ping
        for server_name in servers_to_remove:
            del data[server_name]

        # Guardar los cambios en el archivo JSON
        with open(json_file_path, 'w') as file:
            json.dump(data, file)

        time.sleep(10)  # Esperar 10 segundos antes de hacer el siguiente ping



# Metodo para los nombres de los servidores
def get_next_server_name(data):
    # Obtener todos los nombres de servidores existentes
    server_names = [name for name in data if name.startswith("server")]
    if not server_names:
        return "server1"  # Si no hay nombres de servidores existentes, comenzar con "server1"
    
    # Obtener el número más alto de los nombres de servidores existentes y calcular el siguiente consecutivo
    highest_number = max(int(name[6:]) for name in server_names)
    next_number = highest_number + 1
    return f"server{next_number}"


# Informacion de los servidores
def save_server_ip(ip_address, json_file_path):
    # Cargar datos existentes del archivo JSON o inicializar un diccionario vacío
    if os.path.exists(json_file_path):
        with open(json_file_path, 'r') as file:
            data = json.load(file)
    else:
        data = {}
    server_name = get_next_server_name(data)
    
    if server_name in data:
        data[server_name]["ip"].append(ip_address)
    else:
        data[server_name] = {"ip": ip_address, "videos": []}

    with open(json_file_path, 'w') as file:
        json.dump(data, file)


def start_server(host, port, script_dir):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    s.listen(5)

    print(f"El servidor intermediario está escuchando en {host}:{port}")
    
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


# Envio de informacion a los clientes
def send_file_content(client_socket, file_path):
    with open(file_path, 'r') as file:
        file_content = file.read()
        client_socket.send(file_content.encode('utf-8'))


def start_serverClient(host, port, script_dir):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    s.listen(5)
    
    print(f"El servidor intermediario está escuchando en {host}:{port}")
    
    while True:
        c, addr = s.accept()
        print(f"Se estableció conexión con: {addr}")
        
        json_file_path = os.path.join(script_dir, "server_ips.json")
        send_file_content(c, json_file_path)
        c.close()


if __name__ == "__main__":
    host = ""  
    port = 33330
    portClient = 33331
    # Obtener la ruta del archivo .py que se está ejecutando
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    server_thread = Thread(target=start_server, args=(host, port, script_dir))
    server_thread.start()
    
    client_server_thread = Thread(target=start_serverClient, args=(host, portClient, script_dir))
    client_server_thread.start()
    
    ping_thread = Thread(target=ping_servers, args=(script_dir,))
    ping_thread.start()
