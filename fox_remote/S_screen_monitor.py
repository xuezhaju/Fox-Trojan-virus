import socket
import threading

import cv2
import numpy as np
import os
from colorama import init, Fore, Back, Style

# 初始化彩色输出
init(autoreset=True)

# FOX-Screen标志
FOX_SCREEN_LOGO = f"""
{Fore.RED}{Back.BLACK} ███████╗ ██████╗ ██╗  ██╗    ███████╗ ██████╗██████╗ ███████╗███████╗███╗   ██╗
{Fore.RED}{Back.BLACK} ██╔════╝██╔═══██╗╚██╗██╔╝    ██╔════╝██╔════╝██╔══██╗██╔════╝██╔════╝████╗  ██║
{Fore.RED}{Back.BLACK} █████╗  ██║   ██║ ╚███╔╝     ███████╗██║     ██████╔╝█████╗  █████╗  ██╔██╗ ██║
{Fore.RED}{Back.BLACK} ██╔══╝  ██║   ██║ ██╔██╗     ╚════██║██║     ██╔══██╗██╔══╝  ██╔══╝  ██║╚██╗██║
{Fore.RED}{Back.BLACK} ██║     ╚██████╔╝██╔╝ ██╗    ███████║╚██████╗██║  ██║███████╗███████╗██║ ╚████║
{Fore.RED}{Back.BLACK} ╚═╝      ╚═════╝ ╚═╝  ╚═╝    ╚══════╝ ╚═════╝╚═╝  ╚═╝╚══════╝╚══════╝╚═╝  ╚═══╝
{Style.RESET_ALL}
"""


def display_banner():
    """显示控制端横幅"""
    print(FOX_SCREEN_LOGO)
    print(f"{Fore.RED}[ FOX-Screen 远程监控控制端 ]{Style.RESET_ALL}")
    print(f"{Fore.RED}{Back.BLACK} 输入 /help 查看可用命令 {Style.RESET_ALL}\n")


def get_help():
    """获取帮助信息"""
    return f"""
{Fore.RED}┌──────────────────────────────────┐
{Fore.RED}│  {Fore.BLACK}{Back.RED} 命 令 帮 助 {Style.RESET_ALL}{Fore.RED}    
{Fore.RED}├──────────────────────────────────┤
{Fore.RED}│  {Fore.WHITE}屏幕控制:{Style.RESET_ALL}                            
{Fore.RED}│    {Fore.CYAN}screenshot [path]{Fore.RED}             - 保存截图到指定路径       
{Fore.RED}│    {Fore.CYAN}start_record [path] [fps] [q]{Fore.RED} - 开始录制   
{Fore.RED}│    {Fore.CYAN}stop_record{Fore.RED}                   - 停止录制                
{Fore.RED}│  {Fore.WHITE}屏幕监控(还在做)：{Style.RESET_ALL}                           
{Fore.RED}│    {Fore.CYAN}monitor [fps] [画质]{Fore.RED}           - 开启屏幕监视            
{Fore.RED}│    {Fore.CYAN}stop_monitor(没用，请使用exit){Fore.RED}                  - 结束屏幕监视                   
{Fore.RED}│  {Fore.WHITE}系统控制:{Style.RESET_ALL}                              
{Fore.RED}│    {Fore.CYAN}/help{Fore.RED}                         - 显示本帮助                  
{Fore.RED}│    {Fore.CYAN}/clear{Fore.RED}                        - 清空屏幕                   
{Fore.RED}│    {Fore.CYAN}exit{Fore.RED}                          - 退出程序                
{Fore.RED}└──────────────────────────────────┘
{Style.RESET_ALL}
注: [path]为保存路径, [fps]为帧率(默认10), [q]为质量(1-100,默认80)"""


def clear_screen():
    """清屏函数"""
    print("\033c", end="")


class ScreenClient:
    def __init__(self, host='127.0.0.1', port=5556):
        self.host = host
        self.port = port
        self.client_socket = None
        self.is_recording = False
        self.recording_thread = None
        self.video_writer = None
        self.is_monitoring = False
        self.monitor_thread = None

    def _recv_all(self, length):
        """可靠接收指定长度的数据"""
        data = b''
        while len(data) < length:
            try:
                packet = self.client_socket.recv(length - len(data))
                if not packet:
                    raise ConnectionError("连接已中断")
                data += packet
            except socket.timeout:
                if not self.is_recording:  # 如果已经要求停止
                    break
                continue
        return data

    def connect(self):
        """连接到服务器"""
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.settimeout(5)
            self.client_socket.connect((self.host, self.port))
            print(f"{Fore.GREEN}[*] 成功连接到 {self.host}:{self.port}{Style.RESET_ALL}")
            return True
        except Exception as e:
            print(f"{Fore.RED}[!] 连接失败: {e}{Style.RESET_ALL}")
            return False

    def start_monitor(self, fps=15, quality=80):
        """启动实时监视（不保存文件）"""
        if not self.client_socket:
            if not self.connect():
                return

        try:
            self.client_socket.sendall(f'start_record {fps} {quality}'.encode())
            self.is_monitoring = True

            print(f"{Fore.CYAN}[*] 开始实时监视 ({fps}FPS){Style.RESET_ALL}")
            print(f"{Fore.YELLOW}[!] 按Q键停止监视{Style.RESET_ALL}")

            self.monitor_thread = threading.Thread(
                target=self._monitor_frames,
                daemon=True
            )
            self.monitor_thread.start()

        except Exception as e:
            print(f"{Fore.RED}[!] 启动监视失败: {e}{Style.RESET_ALL}")
            self.stop_monitor()

    def _monitor_frames(self):
        """接收并显示监控帧"""
        try:
            cv2.namedWindow('FOX-Screen 实时监视', cv2.WINDOW_NORMAL)

            while self.is_monitoring:
                # 接收帧数据
                length_bytes = self.client_socket.recv(4)
                if not length_bytes: break

                length = int.from_bytes(length_bytes, 'big')
                frame_data = self.client_socket.recv(length)

                # 显示帧
                frame = cv2.imdecode(np.frombuffer(frame_data, np.uint8), cv2.IMREAD_COLOR)
                cv2.imshow('FOX-Screen 实时监视', frame)

                # 按Q键停止
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

        except Exception as e:
            print(f"{Fore.RED}[!] 监视错误: {e}{Style.RESET_ALL}")
        finally:
            self.stop_monitor()
            cv2.destroyAllWindows()

    def stop_monitor(self):
        """停止监视"""
        if self.is_monitoring:
            try:
                self.is_monitoring = False
                self.client_socket.sendall(b'stop_record')
                print(f"{Fore.GREEN}[*] 监视已停止{Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.RED}[!] 停止监视失败: {e}{Style.RESET_ALL}")

    def save_screenshot(self, save_path=None):
        """保存截图到指定路径"""
        try:
            # 处理路径格式
            if save_path:
                # 替换路径中的正斜杠和双反斜杠
                save_path = save_path.replace('/', '\\')
                save_path = save_path.replace('\\\\', '\\')

                # 如果是目录路径，自动添加文件名
                if os.path.isdir(save_path) or save_path.endswith('\\'):
                    save_path = os.path.join(save_path, f"screenshot_{time.strftime('%Y%m%d_%H%M%S')}.jpg")
                # 确保目录存在
                os.makedirs(os.path.dirname(save_path), exist_ok=True)
            else:
                save_path = f"screenshot_{time.strftime('%Y%m%d_%H%M%S')}.jpg"

            # 获取截图数据
            self.client_socket.sendall(b'screenshot')
            img_data = self.client_socket.recv(1024 * 1024)

            # 保存文件
            with open(save_path, 'wb') as f:
                f.write(img_data)

            # 显示成功信息（绿色）
            print(f"{Fore.GREEN}[√] 截图已保存到: {os.path.abspath(save_path)}{Style.RESET_ALL}")

            # 显示截图预览
            try:
                img = cv2.imdecode(np.frombuffer(img_data, np.uint8), cv2.IMREAD_COLOR)
                cv2.imshow('截图预览 (2秒后自动关闭)', img)
                cv2.waitKey(2000)
                cv2.destroyAllWindows()
            except Exception as e:
                print(f"{Fore.YELLOW}[!] 预览失败: {e}{Style.RESET_ALL}")

        except Exception as e:
            # 显示错误信息（红色）
            print(f"{Fore.RED}[!] 截图失败: {e}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}提示: 请检查路径是否有效且有写入权限{Style.RESET_ALL}")

    def start_recording(self, save_path=None, fps=10, quality=80):
        """开始屏幕录制"""
        try:
            # 处理保存路径
            if not save_path:
                save_path = f"recording_{time.strftime('%Y%m%d_%H%M%S')}.avi"
            else:
                # 规范化路径
                save_path = os.path.normpath(save_path.replace('/', '\\'))

                # 如果是目录，自动添加文件名
                if os.path.isdir(save_path) or save_path.endswith('\\'):
                    save_path = os.path.join(save_path, f"recording_{time.strftime('%Y%m%d_%H%M%S')}.avi")
                # 确保扩展名是支持的视频格式
                elif not save_path.lower().endswith(('.avi', '.mp4', '.mov')):
                    save_path += '.avi'

            # 确保目录存在
            os.makedirs(os.path.dirname(save_path), exist_ok=True)

            # 初始化视频写入器
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            frame_size = (1920, 1080)  # 根据实际分辨率调整
            self.video_writer = cv2.VideoWriter(save_path, fourcc, fps, frame_size)

            if not self.video_writer.isOpened():
                raise ValueError("无法创建视频文件，请检查路径和编码器")

            self.client_socket.sendall(f'start_record {fps} {quality}'.encode())
            self.is_recording = True

            print(f"{Fore.CYAN}[*] 开始录制 (保存到: {save_path}){Style.RESET_ALL}")
            print(f"{Fore.YELLOW}[!] 按任意键停止录制{Style.RESET_ALL}")

            # 启动接收线程
            self.recording_thread = threading.Thread(
                target=self._receive_frames,
                daemon=True
            )
            self.recording_thread.start()

        except Exception as e:
            print(f"{Fore.RED}[!] 开始录制失败: {e}{Style.RESET_ALL}")
            self.stop_recording()

    def _receive_frames(self):
        """增强版帧接收线程"""
        try:
            while getattr(self, 'is_recording', False):
                try:
                    # 接收帧长度
                    length_bytes = self._recv_all(4)
                    if not length_bytes or len(length_bytes) != 4:
                        break

                    length = int.from_bytes(length_bytes, 'big')
                    frame_data = self._recv_all(length)

                    # 写入视频
                    if getattr(self, 'is_recording', False) and hasattr(self, 'video_writer'):
                        frame = cv2.imdecode(np.frombuffer(frame_data, np.uint8), cv2.IMREAD_COLOR)
                        if frame is not None:
                            self.video_writer.write(frame)

                except socket.timeout:
                    continue
                except Exception as e:
                    if getattr(self, 'is_recording', False):
                        print(f"{Fore.RED}[!] 帧处理错误: {e}{Style.RESET_ALL}")
                    break

        finally:
            # 确保资源释放
            if hasattr(self, 'video_writer') and self.video_writer:
                self.video_writer.release()

    def stop_recording(self):
        """终极版停止录制方法"""
        if not getattr(self, 'is_recording', False):
            print(f"{Fore.YELLOW}[!] 录制未运行{Style.RESET_ALL}")
            return

        try:
            # 1. 原子操作设置停止标志
            self.is_recording = False

            # 2. 发送停止命令
            if hasattr(self, 'client_socket') and self.client_socket:
                try:
                    self.client_socket.settimeout(2.0)
                    self.client_socket.sendall(b'stop_record')
                except (socket.timeout, OSError) as e:
                    print(f"{Fore.YELLOW}[!] 停止命令发送失败: {e}{Style.RESET_ALL}")

            # 3. 等待线程结束
            if hasattr(self, 'recording_thread') and self.recording_thread:
                self.recording_thread.join(timeout=3.0)
                if self.recording_thread.is_alive():
                    print(f"{Fore.YELLOW}[!] 线程未正常退出{Style.RESET_ALL}")

            # 4. 释放视频写入器
            if hasattr(self, 'video_writer') and self.video_writer:
                self.video_writer.release()
                self.video_writer = None

            print(f"{Fore.GREEN}[√] 录制已停止{Style.RESET_ALL}")

        except Exception as e:
            print(f"{Fore.RED}[!] 停止过程中发生错误: {e}{Style.RESET_ALL}")
        finally:
            # 最终保障
            self.is_recording = False
            if hasattr(self, 'video_writer') and self.video_writer:
                self.video_writer.release()

    def close(self):
        """关闭连接"""
        self.stop_recording()
        if self.client_socket:
            self.client_socket.close()
            print(f"{Fore.RED}[-] 连接已关闭{Style.RESET_ALL}")


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
    import time

    main()