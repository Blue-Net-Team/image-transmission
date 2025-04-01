r"""
Copyright (C) 2025 IVEN-CN(He Yunfeng) and Anan-yy(Weng Kaiyi)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

远程图传
====
该模块包含两个类：

`VideoStreaming`:
----
视频流传输类(服务端)

方法:
    - `__init__(self, host, port)`: 初始化，设置主机IP地址和端口号
    - `connecting(self)`: 连接客户端
    - `start(self)`: 开始传输视频流
    - `send(self, _img: cv2.typing.MatLike) -> bool`: 发送图像数据

`ReceiveImgTCP`:
----
接收视频流类(客户端)

方法:
    - `__init__(self, host, port)`: 初始化，设置主机IP地址和端口号
    - `read(self)`: 读取图像数据

注意:
----
服务端不能主动向客户端发送数据，只能等待客户端连接后发送数据
"""
import io
import socket
import struct
import cv2
import numpy as np
from .Itrans import ReceiveImg, SendImg
import warnings

class NeedReConnect(Exception):
    """need to reconnect"""
    pass

class   SendImgTCP(SendImg):
    """
    send image in server by TCP
    before send image, you must wait for client connect

    >>>sendImg = SendImgTCP("eth0",4444, 0.05)        # use interface name
    >>>sendImg = SendImgTCP("192.168.137.1", 4444, 0.05)       # use ip address

    >>>sendImg.connecting()        # wait for client connect
    if you initialize this class with _timeout, connecting function will
    return False if timeout, else it will clog.We strongly recommend
    you to set a timeout value.

    if you set the timeout value, you can use flowing code to control clog
    >>>while True:
    >>>    if sendImg.connecting():
    >>>        break

    then you can use send function to send image
    >>> img = ... # read image to img by opencv
    >>>sendImg.send(img)
    """

    def __init__(self, interface_or_ip:str, port:int=4444, _timeout:int|float|None = None):
        """
        initialize
        ----
        Args:
            interface_or_ip (str): which interface to send image or ip address
            port (int): server port
            _timeout (int|None): socket timeout, default is None
        """
        super().__init__(interface_or_ip, port)
        self.host_name = ""
        self.client_address = ""
        self.timeout = _timeout

        self.open_socket()

    def open_socket(self):
        if self.host and self.port:
            try:
                self.server_socket = socket.socket()
                self.server_socket.bind((self.host, self.port))
                self.server_socket.listen(5)
                self.server_socket.settimeout(self.timeout)
                self.connection = None
                self.connect = None
                self.stream = io.BytesIO()
                self.is_open = True
            except Exception as e:
                warnings.warn(f"Socket error: {e}", UserWarning)
                self.is_open = False

    def connecting(self):
        def _connect(obj):
            try:
                obj.connection, obj.client_address = obj.server_socket.accept()
                obj.connect = obj.connection.makefile("wb")
                obj.host_name = socket.gethostname()
                obj.host_ip = socket.gethostbyname(obj.host_name)

                return True
            except socket.timeout:
                return False
        if self.is_open:
            return _connect(self)
        else:
            # 重新初始化
            self.open_socket()
            return _connect(self)

    def send(self, _img: cv2.typing.MatLike) -> bool:
        """
        send image
        ----
        before run this function, must run connecting

        Args:
            _img (cv2.typing.MatLike): opencv image
        Returns:
            res (bool): whether send success
        """
        if self.is_open:
            try:
                if self.connect is None:
                    raise ConnectionError("has not conncet any client")

                img_encode = cv2.imencode(".jpg", _img, [int(cv2.IMWRITE_JPEG_QUALITY), 70])[1]
                data_encode = np.array(img_encode)
                self.stream.write(data_encode) # type: ignore
                self.connect.write(struct.pack("<L", self.stream.tell()))
                self.connect.flush()
                self.stream.seek(0)
                self.connect.write(self.stream.read())
                self.stream.seek(0)
                self.stream.truncate()
                self.connect.write(struct.pack("<L", 0))
                return True
            except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError) as e:
                warnings.warn(f"Connection error: {e}", UserWarning)
                self.close()
                raise NeedReConnect("Connection break, please reconnect")
            except OSError as e:
                warnings.warn(f"OSError {e}", UserWarning)
                self.close()
                raise NeedReConnect("Connection break, please reconnect")
        else:
            return False

    def close(self):
        """close socket"""
        if self.is_open:
            if self.connect:
                try:
                    self.connect.close()
                except OSError as e:
                    warnings.warn(f"Error closing connect: {e}", UserWarning)
            if self.connection:
                try:
                    self.connection.close()
                except OSError as e:
                    warnings.warn(f"Error closing connection: {e}", UserWarning)
            if self.server_socket:
                try:
                    self.server_socket.close()
                except OSError as e:
                    warnings.warn(f"Error closing server_socket: {e}", UserWarning)
            self.is_open = False

class ReceiveImgTCP(ReceiveImg):
    """
    receive image by TCP socket.
    This class allow you to receive image from server with class SendImgTCP

    you can use this class with flowing code:
    >>> rec = ReceiveImgTCP("192.168.137.1", 4444)
    the ip 192.168.137.1 is the server ip.And before you initialize this class,
    you must run the server with class SendImgTCP, or you will get a connection error.

    than you can use this class to receive image:
    >>> while True:
    >>>     ret, img = rec.read()
    """

    def __init__(self, host:str, port:int):
        """
        Args:
            host (str): server's ip
            port (int): server's port
        """
        super().__init__(host, port)
        self.host = host
        self.port = port
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.host, self.port))
            self.connection = self.client_socket.makefile("rb")
            self.stream_bytes = b" "

            print("connect successfully")
            print(f"Host : {self.host}" )
        except Exception as e:
            warnings.warn(f"Error: {e}", UserWarning)
            exit()

    def read(self):
        try:
            msg = self.connection.read(4096)
            self.stream_bytes += msg
            first = self.stream_bytes.find(b"\xff\xd8")
            last = self.stream_bytes.find(b"\xff\xd9")

            if first != -1 and last != -1:
                jpg = self.stream_bytes[first : last + 2]
                self.stream_bytes = self.stream_bytes[last + 2 :]
                image = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
                return True, image

        except Exception as e:
            warnings.warn(f"Error: connection error {e}", UserWarning)
        return False, None

    def release(self):
        self.connection.close()
        self.client_socket.close()

class SendImgUDP(SendImg):
    """
    send image in server by UDP

    in this class, you can send image to more than one client

    use `clients_ip` to set the ip list
    >>>sendImg = SendImgUDP("eth0", 4444)
    if you don't use linux, you can initialize this objct by self ip
    >>>sendImg = SendImgUDP("192.169.137.1", 4444)
    and set the ip list, which you want to send image to
    >>>sendImg.clients_ip = ["192.168.173.1", "192.168.137.231"]
    >>> img = ... # read image to img by opencv
    >>>sendImg.send(img)
    """
    EOF_MARKER = b'EOF'
    BUFFER_SIZE = 65536  # UDP最大接收缓冲区大小
    B_IP = ""
    _ip_lst = set()

    @property
    def clients_ip(self):
        """
        clients ip list
        """
        if self.B_IP:
            self._ip_lst.add(self.B_IP)
        return self._ip_lst

    @clients_ip.setter
    def clients_ip(self, ip:list):
        """
        set clients ip list
        ----
        Args:
            ip (list): list of ip address
        """
        self._ip_lst = set(ip)
        if self.B_IP:
            self._ip_lst.add(self.B_IP)

    def __init__(self, interface_or_ip:str, port:int):
        """
        initialize
        ----
        Args:
            interface_or_ip (str): interface name or ip address
            port (int): port number
        """
        super().__init__(interface_or_ip, port)
        self.openSocket()

    def openSocket(self):
        """
        打开udp套接字
        """
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.server_socket.bind((self.host, self.port))

    def connecting(self):
        """
        wait for client connect, if you don't call this function,
        it will send image to ip address in `clients_ip`
        """
        try:
            self.server_socket.settimeout(0.5)
            data, addr = self.server_socket.recvfrom(self.BUFFER_SIZE)
            if addr != (self.host, self.port) and data == b'connect':  # 避免回环请求
                warnings.warn(f"receive request from {addr}")
                # 获取B设备的IP和端口，固定向对端4444端口发送数据
                self.B_IP, _ = addr
                warnings.warn(f"set op connection, IP: {self.B_IP}, port: {self.port}")
                return True
        except socket.timeout:
            return False
        except OSError:
            self.openSocket()
        except Exception as e:
            warnings.warn(str(e))
        return False

    def send(self, _img: cv2.typing.MatLike) -> bool:
        """
        send image data
        ----
        Args:
            _img (cv2.typing.MatLike): opencv image
        Returns:
            res (bool): whether send success
        """
        _, img_encoded = cv2.imencode('.jpg', _img)
        img_data = img_encoded.tobytes()

        # 创建包头：包头包含数据长度
        header = struct.pack('!I', len(img_data))  # '!I' 表示大端字节序的一个无符号整数（数据长度）

        # 构造完整数据包：包头 + 图像数据 + 包尾
        packet = header + img_data + self.EOF_MARKER

        # 发送图像数据到对端
        for ip in self.clients_ip:
            self.server_socket.sendto(packet, (ip, self.port))
        return True

    def close(self):
        self.server_socket.close()

class ReceiveImgUDP(ReceiveImg):
    """
    receive image in client by UDP, you can receive image from server which use class SendImgUDP
    In this class, the `send` function forms a polymorphism with opencv `VideoCapture.raed`

    you can use this class with flowing code:
    >>> rec = ReceiveImgUDP("192.168.137.1", 4444, "192.168.137.161")
    >>> while True:
    >>>     ret, img = rec.read()
    """
    def __init__(self, server_ip:str, port:int, self_ip:str):
        """
        Args:
            server_ip (str): server ip
            port (int): which port to receive in this machine
            self_ip (str): ip address of this machine
        """
        super().__init__(server_ip, port)
        self.host = server_ip
        self.port = port
        # 打开udp套接字
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # 绑定自身ip
        self.client_socket.bind((self_ip, self.port))
        # 发起连接请求
        self.client_socket.sendto(b'connect', (self.host, self.port))

    def read(self):
        """
        receive image data

        Returns:
            tuple (res, img): whether read success, image data
        """
        try:
            self.client_socket.settimeout(1)
            data, addr = self.client_socket.recvfrom(65536)
        except socket.timeout:
            img = np.zeros((240, 320, 3), dtype=np.uint8)
            cv2.putText(
                img,
                "read img timeout",
                (20, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 0, 255),
                2
            )
            return False, img
        if addr != (self.host, self.port):
            warnings.warn(f"received data from unknown server {addr}")
            return False, None

        # 解析包头，获取数据长度
        data_length = struct.unpack('!I', data[:4])[0]  # 获取数据包的长度，前4个字节
        image_data = data[4:4 + data_length]  # 获取图像数据（包头后面的部分）

        # 包尾检查
        if data[4 + data_length:4 + data_length + len(b'EOF')] == b'EOF':
            # 处理图像数据（例如显示）
            nparr = np.frombuffer(image_data, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if frame is not None:
                return True, frame
            else:
                return False, None
        else:
            return False, None

    def release(self):
        """release resource(socket)"""
        self.client_socket.close()
