#
import socket
import time
from colorama import Fore, Style
from S_client import ScreenClient
from S_utils import display_banner, get_help, clear_screen
from S_constants import DEFAULT_HOST, DEFAULT_PORT

def main():
    display_banner()

    # 初始化客户端
    client = ScreenClient('192.168.10.195', 5556)  # 修改为你的被控端IP

    # 连接重试逻辑
    retry_count = 0
    max_retries = 3
    while retry_count < max_retries:
        try:
            cmd = input(f"{Fore.RED}FOX-Screen>{Style.RESET_ALL} ").strip().lower()
            if client.connect():
                break
            retry_count += 1
            if retry_count < max_retries:
                choice = input(f"{Fore.YELLOW}是否重试? (Y/N): {Style.RESET_ALL}").lower()
                if choice != 'y':
                    return

            elif cmd.startswith('monitor'):
                # 解析参数：monitor [fps] [quality]
                parts = cmd.split()
                fps = int(parts[1]) if len(parts) > 1 else 15
                quality = int(parts[2]) if len(parts) > 2 else 80
                client.start_monitor(fps, quality)

            elif cmd == 'stop_monitor':
                client.stop_monitor()

        except KeyboardInterrupt:
            client.stop_monitor()
            return

    if retry_count == max_retries:
        print(f"{Fore.RED}[!] 达到最大重试次数，退出程序{Style.RESET_ALL}")
        return

    # 主命令循环
    while True:
        try:
            cmd = input(f"{Fore.RED}FOX-Screen>{Style.RESET_ALL} ").strip()

            if not cmd:
                continue

            if cmd.lower() == '/help':
                print(get_help())
                continue

            if cmd.lower() == '/clear':
                clear_screen()
                display_banner()
                continue

            if cmd.lower() == 'exit':
                client.close()
                break

            # 处理截图命令
            if cmd.lower().startswith('screenshot'):
                parts = cmd.split()
                save_path = parts[1] if len(parts) > 1 else None
                client.save_screenshot(save_path)

            # 处理开始录制命令
            elif cmd.lower().startswith('start_record'):
                parts = cmd.split()
                save_path = parts[1] if len(parts) > 1 else None
                fps = int(parts[2]) if len(parts) > 2 else 10
                quality = int(parts[3]) if len(parts) > 3 else 80
                client.start_recording(save_path, fps, quality)

            # 处理停止录制命令
            elif cmd.lower() == 'stop_record':
                client.stop_recording()

        except KeyboardInterrupt:
            print(f"\n{Fore.RED}[!] 用户中断{Style.RESET_ALL}")
            if input(f"{Fore.YELLOW}是否确认退出? (Y/N): {Style.RESET_ALL}").lower() == 'y':
                client.close()
                break
            else:
                continue

        except Exception as e:
            print(f"{Fore.RED}[!] 错误: {e}{Style.RESET_ALL}")

if __name__ == "__main__":
    main()