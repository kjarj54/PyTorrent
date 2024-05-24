import socket
import json
import os
from threading import Thread
import time

def ping_servers(script_dir):
    json_file_path = os.path.join(script_dir, "server_ips.json")
    
    while True:
        if os.path.exists(json_file_path):
            with open(json_file_path, 'r') as file:
                data = json.load(file)
        else:
            data = {}

        servers_to_remove = []

        for server_name, server_info in data.items():
            ip_address = server_info.get("ip")
            port = server_info.get("port")
            if ip_address and port:
                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        s.settimeout(5)
                        s.connect((ip_address, port))
                        s.sendall(b"PING")
                        response = s.recv(1024).decode()
                        if response != "PONG":
                            servers_to_remove.append(server_name)
                            print(f"El servidor {server_name} no está activo.")
                        if response == "PONG":
                            print(f"El servidor {server_name} está activo.")
                            check_servers(script_dir)
                           
                except:
                    servers_to_remove.append(server_name)

        for server_name in servers_to_remove:
            del data[server_name]
            
        with open(json_file_path, 'w') as file:
            json.dump(data, file)

        time.sleep(10)

def check_servers(script_dir):
    json_file_path = os.path.join(script_dir, "server_ips.json")

    while True:
        print("Verificando servidores...")
        if os.path.exists(json_file_path):
            with open(json_file_path, 'r') as file:
                data = json.load(file)
        else:
            data = {}

        servers_to_remove = []

        for server_name, server_info in data.items():
            print(f"Verificando el servidor {server_name}...")
            ip_address = server_info.get("ip")
            port = server_info.get("port")
            if ip_address and port:
                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        s.settimeout(5)
                        result = s.connect_ex((ip_address, port))
                        if result != 0:
                            print(f"El servidor {server_name} no está activo.")
                            servers_to_remove.append(server_name)
                        else:
                            print(f"El servidor {server_name} está activo.")
                            s.sendall(b"INFO")
                            received_data = s.recv(1024)
                            print(f"Datos recibidos: {received_data}")
                            if received_data.startswith(b'{'):
                                json_data = json.loads(received_data.decode())
                                update_server_info(data, server_name, ip_address, port, json_data["videos"])
                            else:
                                print("Los datos recibidos no están en formato JSON.")
                except Exception as e:
                    print(f"No se pudo verificar el servidor {server_name}: {e}")
                    servers_to_remove.append(server_name)

        for server_name in servers_to_remove:
            del data[server_name]

        with open(json_file_path, 'w') as file:
            json.dump(data, file)

        time.sleep(2)

def update_server_info(data, server_name, ip_address, port, videos):
    if server_name in data:
        data[server_name]["ip"] = ip_address
        data[server_name]["port"] = port
        data[server_name]["videos"] = videos
    else:
        data[server_name] = {"ip": ip_address, "port": port, "videos": videos}
    return data

def get_next_server_name(data):
    server_names = [name for name in data if name.startswith("server")]
    if not server_names:
        return "server1"
    
    highest_number = max(int(name[6:]) for name in server_names)
    next_number = highest_number + 1
    return f"server{next_number}"

def save_server_info(ip_address, port, videos, json_file_path):
    if os.path.exists(json_file_path):
        with open(json_file_path, 'r') as file:
            data = json.load(file)
    else:
        data = {}
    server_name = get_next_server_name(data)
    
    data[server_name] = {"ip": ip_address, "port": port, "videos": videos}

    with open(json_file_path, 'w') as file:
        json.dump(data, file)

def start_server(host, port, script_dir):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    s.listen(5)

    print(f"El servidor intermediario está escuchando en {host}:{port}")
    
    json_file_path = os.path.join(script_dir, "server_ips.json")

    while True:
        c, addr = s.accept()
        print(f"Se estableció conexión con: {addr}")
        
        data = c.recv(1024)
        
        port_received = json.loads(data.decode())["port"]
        print(f"Puerto recibido: {port_received}")
        
        videos = json.loads(data.decode())["videos"]
        print(f"Videos recibidos: {videos}")
        
        ip_received, _ = addr
        print(f"Dirección IP recibida: {ip_received}")

        save_server_info(ip_received, port_received, videos, json_file_path)
        c.close()

def send_file_content(client_socket, file_path):
    with open(file_path, 'r') as file:
        file_content = file.read()
        client_socket.send(file_content.encode('utf-8'))

def start_serverClient(host, port, script_dir):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    s.listen(5)
    
    print(f"El servidor para clientes está escuchando en {host}:{port}")
    
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
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    server_thread = Thread(target=start_server, args=(host, port, script_dir))
    server_thread.start()
    
    client_server_thread = Thread(target=start_serverClient, args=(host, portClient, script_dir))
    client_server_thread.start()
    
    ping_thread = Thread(target=ping_servers, args=(script_dir,))
    ping_thread.start()
