"""
(局域网)远程图传
----
该库提供了一个简单的局域网远程图传功能。当然，如果两个设备使用了内网穿刺技术，也可以在不同网络下使用。
该库提供了两个类: `ReceiveImg` 和 `StreamImg`。
- `ReceiveImg` 类用于接收图像数据。
- `StreamImg` 类用于发送图像数据。

该项目中，服务端进行图像传输,客户端进行图像接收。即服务端可以部署在树莓派上,客户端部署在PC上。

使用说明:
--------
首先需要导入库

>>> import ImgTrans

发送图像
------------
ip地址是服务端的ip，即图像发送方的ip地址

>>> stream = ImgTrans.StreamImg("192.168.113.18", 8000)
>>> stream.connecting()
>>> stream.start()
>>> stream.send(image)      # image是openmv的mat类型

接收图像
------------
ip地址是服务端的ip，即图像发送方的ip地址，端口号要和服务端设置的端口号一致

>>> receive = ImgTrans.ReceiveImg("192.168.113.18", 8000)
>>> img = receive.read()        # 函数回返回一个元组，第一个元素是bool类型，表示是否接收成功，第二个元素是图像数据

注意
----
发送图像的connecting需要在接受图像一方接收器对象创建之前调用，如果先执行

>>> receive = ImgTrans.ReceiveImg("192.168.113.18", 8000)

然后才执行

>>> stream = ImgTrans.StreamImg("192.168.113.18", 8000)
>>> stream.connecting()

会发生报错
"""

__version__ = "1.0.0"

from ImgTrans.trans import *
