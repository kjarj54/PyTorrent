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


def check_servers(script_dir):
    json_file_path = os.path.join(script_dir, "server_ips.json")

    while True:
        print("Verificando servidores...")
        # Cargar datos existentes del archivo JSON o inicializar un diccionario vacío
        if os.path.exists(json_file_path):
            with open(json_file_path, 'r') as file:
                data = json.load(file)
        else:
            data = {}

        servers_to_remove = []

        # Iterar sobre los servidores y realizar la conexión
        for server_name, server_info in data.items():
            print(f"Verificando el servidor {server_name}...")
            ip_address = server_info.get("ip")
            print("ip_address",ip_address)
            port = server_info.get("port")
            print("port",port)
            if ip_address and port:
                try:
                    port = int(port)
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        s.settimeout(5) 
                        result = s.connect_ex((ip_address, port))
                        if result != 0:
                            print(f"El servidor {server_name} no está activo.")
                            servers_to_remove.append(server_name)
                        else:
                            print(f"El servidor {server_name} está activo.")
                            received_data = s.recv(1024) 
                            if received_data.startswith(b'{'):  # Verifica si los datos recibidos son JSON
                                json_data = json.loads(received_data.decode())
                                print ("datos actualizados: ", json_data)
                                update_server_info(data, server_name, ip_address, port, json_data["videos"])
                            else:
                                print("Los datos recibidos no están en formato JSON.")
                            
                            
                except Exception as e:
                    print(f"No se pudo verificar el servidor {server_name}: {e}")
                    servers_to_remove.append(server_name)

        # Eliminar los servidores que no están activos
        for server_name in servers_to_remove:
            del data[server_name]

        # Guardar los cambios en el archivo JSON
        with open(json_file_path, 'w') as file:
            json.dump(data, file)

        time.sleep(10)  # Esperar 10 segundos antes de volver a verificar


def update_server_info(data, server_name, ip_address, port, videos):
    if server_name in data:
        data[server_name]["ip"] = ip_address
        data[server_name]["port"] = port
        data[server_name]["videos"] = videos
    else:
        data[server_name] = {"ip": ip_address, "port": port, "videos": videos}
    return data



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
def save_server_info(ip_address,port, videos, json_file_path):
    # Cargar datos existentes del archivo JSON o inicializar un diccionario vacío
    if os.path.exists(json_file_path):
        with open(json_file_path, 'r') as file:
            data = json.load(file)
    else:
        data = {}
    server_name = get_next_server_name(data)
    
    if server_name in data:
        data[server_name]["ip"] = ip_address
        data[server_name]["port"] = port
        data[server_name]["videos"] = videos

    else:
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
        # Establecer conexión
        c, addr = s.accept()
        print(f"Se estableció conexión con: {addr}")
        
        #recibir puerto del servidor
        data = c.recv(1024)
        #data = port {"port": 33332, "videos": ["Jumanji.mp4"]}
        
        #port:
        port_received = json.loads(data.decode())["port"]
        print(f"Puerto recibido: {port_received}")
        
        #videos:
        videos = json.loads(data.decode())["videos"]
        print(f"Videos recibidos: {videos}")
        # Recibir dirección IP del servidor
        ip_received,_ = addr
        print(f"Dirección IP recibida: {ip_received}")

        # Guardar la dirección IP en el archivo JSON
        save_server_info(ip_received, port_received,videos, json_file_path)
        
        

        
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
    
    ping_thread = Thread(target=check_servers, args=(script_dir,))
    ping_thread.start()
