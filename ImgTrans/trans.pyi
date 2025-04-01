import cv2


class SendImgUDP:
    def __init__(self, interface_or_ip: str, port: int = 4444) -> None: 
        self.clients_ip = None
        self.EOF_MARKER = None
        self.B_IP = None
        self.BUFFER_SIZE = None
        self.port = None
        self.host = None
        self.server_socket = None
        ...
    def openSocket(self) -> None: ...
    def connecting(self) -> bool: ...
    def send(self, img: str) -> bool: ...
    def close(self) -> None: ...

class SendImgTCP:
    def __init__(self, interface_or_ip: str, port: int = 4444, _timeout:int|float|None = None) -> None: 
        self.stream = None
        self.timeout = None
        self.port = None
        self.host = None
        self.server_socket = None
        self.connection = None
        self.connect = None
        self.is_open = None
        self.client_address = None
        self.host_ip = None
        self.host_name = None
        ...
    def open_socket(self) -> None: ...
    def connecting(self) -> bool: ...
    def send(self, img: str) -> bool: ...
    def close(self) -> None: ...

class ReceiveImgUDP:
    def __init__(self, interface_or_ip: str, port: int = 4444) -> None: 
        self.host = None
        self.port = None
        self.client_socket = None
        ...
    def read(self) -> tuple[bool, cv2.typing.MatLike]: ...
    def release(self) -> None: ...

class ReceiveImgTCP:
    def __init__(self, interface_or_ip: str, port: int = 4444) -> None: 
        self.port = None
        self.host = None
        self.stream_bytes = None
        self.client_socket = None
        self.connection = None
        ...
    def read(self) -> tuple[bool, cv2.typing.MatLike]: ...
    def release(self) -> None: ...
