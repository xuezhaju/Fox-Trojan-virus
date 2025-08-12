import re
from colorama import Fore, Style

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