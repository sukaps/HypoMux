"""
Windows 系统代理注册表控制模块
用于 HypoMux 多网卡下载加速的即开即用配置

核心功能：
- 修改 Windows 系统代理注册表（WinINet）
- 支持 SOCKS5 代理格式
- 动态刷新无需重启
- 生命周期绑定，防止异常退出导致断网
"""

import winreg
import ctypes
from typing import Tuple


def set_system_proxy(enable: bool, proxy_addr: str = "127.0.0.1:1080") -> Tuple[bool, str]:
    """
    设置 Windows 系统代理（SOCKS5）

    Args:
        enable: True=启用代理, False=禁用代理
        proxy_addr: 代理地址，格式为 "ip:port"

    Returns:
        (成功, 消息)
    """
    try:
        # 打开注册表项
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Internet Settings"

        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            key_path,
            0,
            winreg.KEY_WRITE
        ) as key:
            if enable:
                # 启用代理
                winreg.SetValueEx(key, "ProxyEnable", 0, winreg.REG_DWORD, 1)
                # 设置代理地址（必须带 socks= 前缀）
                proxy_value = f"socks={proxy_addr}"
                winreg.SetValueEx(key, "ProxyServer", 0, winreg.REG_SZ, proxy_value)
                msg = f"系统代理已启用: {proxy_value}"
            else:
                # 禁用代理
                winreg.SetValueEx(key, "ProxyEnable", 0, winreg.REG_DWORD, 0)
                msg = "系统代理已禁用"

        # 动态刷新系统代理设置（无需重启浏览器）
        _refresh_system_proxy()

        return True, msg

    except Exception as e:
        return False, f"设置系统代理失败: {str(e)}"


def _refresh_system_proxy():
    """
    通知 Windows 刷新系统代理设置
    使用 WinINet API 动态刷新，立即生效
    """
    try:
        internet_set_option = ctypes.windll.Wininet.InternetSetOptionW
        # INTERNET_OPTION_SETTINGS_CHANGED = 39
        internet_set_option(0, 39, 0, 0)
        # INTERNET_OPTION_REFRESH = 37
        internet_set_option(0, 37, 0, 0)
    except Exception as e:
        print(f"[WARNING] 刷新系统代理失败: {e}")


def get_system_proxy_status() -> Tuple[bool, str]:
    """
    获取当前系统代理状态

    Returns:
        (是否启用, 代理地址)
    """
    try:
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Internet Settings"

        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            key_path,
            0,
            winreg.KEY_READ
        ) as key:
            try:
                enabled = winreg.QueryValueEx(key, "ProxyEnable")[0]
                proxy_server = winreg.QueryValueEx(key, "ProxyServer")[0]

                if enabled == 1:
                    return True, proxy_server
                else:
                    return False, ""
            except FileNotFoundError:
                return False, ""

    except Exception:
        return False, ""


if __name__ == "__main__":
    # 测试代码
    print("=" * 60)
    print("Windows 系统代理控制测试")
    print("=" * 60)

    # 检查当前状态
    enabled, proxy = get_system_proxy_status()
    print(f"\n当前状态:")
    print(f"  启用: {enabled}")
    print(f"  代理: {proxy if proxy else '(无)'}")

    # 启用代理
    print(f"\n启用系统代理...")
    success, msg = set_system_proxy(True, "127.0.0.1:1080")
    print(f"  {msg}")

    # 检查状态
    enabled, proxy = get_system_proxy_status()
    print(f"\n启用后状态:")
    print(f"  启用: {enabled}")
    print(f"  代理: {proxy}")

    input("\n按 Enter 键禁用代理...")

    # 禁用代理
    print(f"\n禁用系统代理...")
    success, msg = set_system_proxy(False)
    print(f"  {msg}")

    # 检查状态
    enabled, proxy = get_system_proxy_status()
    print(f"\n禁用后状态:")
    print(f"  启用: {enabled}")
    print(f"  代理: {proxy if proxy else '(无)'}")

    print("\n测试完成！")
