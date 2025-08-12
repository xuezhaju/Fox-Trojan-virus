#
from colorama import init, Fore, Back, Style
from S_constants import FOX_SCREEN_LOGO

# 初始化彩色输出
init(autoreset=True)

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