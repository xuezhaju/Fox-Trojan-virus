#
from colorama import Fore, Back, Style

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

# 默认配置
DEFAULT_HOST = '127.0.0.1'
DEFAULT_PORT = 5556
DEFAULT_FPS = 15
DEFAULT_QUALITY = 80