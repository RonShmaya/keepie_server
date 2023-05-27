import uvicorn
import threading
from keepie_server.keepie_server.db.app_firebase_connector import FirebaseConnector
import socket


class HelperServer:
    __instance = None
    PORT_AVAILABLE = 0

    def __new__(cls):
        if HelperServer.__instance is None:
            HelperServer.__instance = object.__new__(cls)
            HelperServer.__instance.__initialized = False
        return HelperServer.__instance

    def __init__(self):
        if HelperServer.__instance.__initialized: return
        HelperServer.__instance.__initialized = True

    def get_external_ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        path = s.getsockname()[0]
        s.close()
        return path
    
    def is_port_available(self,host,port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        result = sock.connect_ex((host,port))
        sock.close()
        if result == HelperServer.PORT_AVAILABLE:
           return True
        return False
    
    def get_available_port(self):
        sock = socket.socket()
        sock.bind(('', 0))
        port = sock.getsockname()[1]
        sock.close()
        return port


class ServerConfiguration:
    __instance = None
    __API_dir = "keepie_server.keepie_server.app_layer.fast_api:my_api"

    def __new__(self, host=None, port=None):
        if ServerConfiguration.__instance is None:
            ServerConfiguration.__instance = object.__new__(self)
            ServerConfiguration.__instance.__initialized = False
        return ServerConfiguration.__instance

    def __init__(self, host=None , port=None):
        if ServerConfiguration.__instance.__initialized: return
        ServerConfiguration.__instance.__initialized = True
        self.__host = host if host is not None else HelperServer().get_external_ip()
        self.__port = port if port is not None else HelperServer().get_available_port()
        print(f"{self.__host} {self.__port}")
        self.__server_th = threading.Thread(target=self.__activate_server)
        

    def __activate_server(self):
        if HelperServer().is_port_available(self.__host,self.__port):
            config = uvicorn.Config(ServerConfiguration.__API_dir,host=self.__host, port=self.__port, log_level="info")
            server = uvicorn.Server(config)
            server.run()

    def activate_server(self):
        if self.__server_th.is_alive():
            return
        self.__server_th.start()

    def is_server_active(self):
        return self.__server_th.is_alive()


def run_server():
    ServerConfiguration(port=8085).activate_server()


def main():
    ServerConfiguration(port=8085).activate_server()


if __name__ == "__main__":
    main()
