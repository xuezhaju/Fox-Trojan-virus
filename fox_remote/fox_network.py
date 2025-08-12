import socket


class FoxClient:
    def __init__(self, server_host='192.168.10.195', server_port=5555):
        self.server_host = server_host
        self.server_port = server_port
        self.socket = None

    def connect(self):
        """连接到服务器"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.server_host, self.server_port))
            return True
        except Exception as e:
            return False

    def send_command(self, command):
        """发送命令并接收响应"""
        try:
            self.socket.send(command.encode('utf-8'))

            # 接收响应 (分块接收大数据)
            response = b""
            while True:
                chunk = self.socket.recv(4096)
                if not chunk:
                    break
                response += chunk
                if len(chunk) < 4096:
                    break

            return response
        except Exception as e:
            raise ConnectionError(f"命令执行失败: {e}")

    def close(self):
        """关闭连接"""
        if self.socket:
            self.socket.close()