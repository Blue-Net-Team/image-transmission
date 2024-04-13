"""在本地电脑运行"""
import socket
import cv2
import numpy as np


class ReceiveImg(object):
    def __init__(self, host, port):
        """初始化
        * host: 树莓派的IP地址
        * port: 端口号，与树莓派设置的端口号一致"""
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)					# 设置创建socket服务的Client客服务的参数
        self.client_socket.connect((host, port))												# 连接的主机IP地址和端口
        self.connection = self.client_socket.makefile('rb')										# 创建一个makefile传输文件，读功能，读数据是b''二进制类型
        print(" ")
        print("已连接到服务端：")
        print("Host : ", host)
        print("请按‘q’退出图像传输!")
        self.start()

    def start(self):
        try:
            # need bytes here
            stream_bytes = b' '											# 创建一个变量，存放的数据类型是b''二进制类型数据
            while True:
                msg = self.connection.read(1024)						# 读makefile传输文件，一次读1024个字节
                stream_bytes += msg
                first = stream_bytes.find(b'\xff\xd8')					# 检测帧头位置
                last = stream_bytes.find(b'\xff\xd9')					# 检测帧尾位置

                if first != -1 and last != -1:
                    jpg = stream_bytes[first:last + 2]					# 帧头和帧尾中间的数据就是二进制图片数据（编码后的二进制图片数据，需要解码后使用）
                    stream_bytes = stream_bytes[last + 2:]				# 更新stream_bytes数据
                    image = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)			# 将二进制图片数据转换成numpy.uint8格式（也就是图片格式）数据，然后解码获得图片数据
                    cv2.imshow('image', image)							# 打开一个窗口显示图片 
                    if cv2.waitKey(1) & 0xFF == ord('q'):				# 等待1ms后显示下一帧图片
                        break
        except:
            print("Error：连接出错！")

        finally:
            print("已退出图像传输！")
            cv2.destroyAllWindows()
            print("已关闭窗口！")
            self.connection.close()
            print("与断开服务端连接！")


if __name__ == '__main__':
    ReceiveImg('192.168.137.112', 8000)
