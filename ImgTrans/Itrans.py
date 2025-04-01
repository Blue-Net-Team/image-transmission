"""
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
"""
import socket
import struct
import fcntl
import warnings

import cv2


class SendImg(object):
    """
    base class of send image
    """
    # 服务端ip
    _host:str = ""
    host_ip:str = ""
    # 服务端端口
    _interface:str = ""

    @property
    def host(self):
        return self._host

    @property
    def interface(self):
        return self._interface

    @interface.setter
    def interface(self, value:str):
        self._interface = value
        self._host = self.get_ip_address(value)

    def __init__(self, interface_or_ip:str, port:int=4444):
        """初始化
        ----
        Args:
            interface_or_ip (str): interface like eth0 and wlan0 or ip address
            port (int): port number
        """
        self.is_open = False
        # if interface_or_ip can be split by '.', it is ip address
        if len(interface_or_ip.split('.')) == 4:
            self._host = interface_or_ip
        else:
            self.interface = interface_or_ip
        self.port = port

    @staticmethod
    def get_ip_address(interface: str) -> str:
        """
        get ip address by interface

        Args:
            interface (str): interface like eth0 and wlan0
        Returns:
            ip (str): IP address
        """
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            return socket.inet_ntoa(fcntl.ioctl(
                s.fileno(),
                0x8915,  # SIOCGIFADDR
                struct.pack('256s', interface[:15].encode('utf-8'))
            )[20:24])
        except Exception as e:
            warnings.warn(f"get_ip_address function must run in linux, {e}", UserWarning)
            return ""

    def connecting(self):
        """
        connect to client
        ----
        """
        ...

    def send(self, _img: cv2.typing.MatLike) -> bool:
        """
        send image data
        ----
        before run this function you must run connect function

        Args:
            _img (cv2.typing.MatLike): image data
        Returns:
            res (bool): whether send success
        """
        ...

    def close(self):
        """close socket"""
        ...


class ReceiveImg(object):
    """
    receive image class
    """
    def __init__(self, host:str, port:int):
        """
        Args:
            host (str): ip address of server
            port (int): port number
        """
        ...

    def read(self) -> tuple[bool, cv2.typing.MatLike]:
        """
        read image data
        ----
        Returns:
            tuple (res, img): whether read success and image data
        """
        ...

    def release(self):
        """release socket"""
        ...
