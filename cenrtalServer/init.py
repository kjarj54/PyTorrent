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

    # Guardar la dirección IP del servidor
    data[ip_address] = True

    # Guardar los datos actualizados en el archivo JSON
    with open(json_file_path, 'w') as file:
        json.dump(data, file)

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

if __name__ == "__main__":
    host = ""  
    port = 33330
    
    start_server(host, port)
