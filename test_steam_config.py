"""
测试 Steam 注册表代理配置
"""

import winreg
from utils.app_configurator import AppConfigurator


def check_steam_registry():
    """检查 Steam 注册表配置"""
    print("=" * 60)
    print("检查 Steam 注册表配置")
    print("=" * 60)

    try:
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Valve\Steam",
            0,
            winreg.KEY_READ
        ) as key:
            print("\n[成功] 找到 Steam 注册表项")

            # 读取代理配置
            try:
                proxy = winreg.QueryValueEx(key, "Socks5Proxy")[0]
                print(f"  Socks5Proxy = {proxy}")
            except FileNotFoundError:
                print(f"  Socks5Proxy = (未配置)")

            try:
                port = winreg.QueryValueEx(key, "Socks5ProxyPort")[0]
                print(f"  Socks5ProxyPort = {port}")
            except FileNotFoundError:
                print(f"  Socks5ProxyPort = (未配置)")

    except FileNotFoundError:
        print("\n[失败] 未找到 Steam 注册表项（Steam 可能未安装）")
    except Exception as e:
        print(f"\n[错误] {e}")


def test_configure():
    """测试配置 Steam"""
    print("\n" + "=" * 60)
    print("测试配置 Steam 代理")
    print("=" * 60)

    configurator = AppConfigurator(proxy_host="127.0.0.1", proxy_port=1080)
    success, msg = configurator.configure_steam()

    print(f"\n配置结果:")
    print(msg)

    print("\n" + "=" * 60)
    print("配置后的注册表状态:")
    print("=" * 60)
    check_steam_registry()


if __name__ == "__main__":
    print("Steam 代理配置测试工具\n")
    print("此工具将：")
    print("1. 检查当前 Steam 注册表配置")
    print("2. 配置 Steam 使用 SOCKS5 代理")
    print("3. 验证配置结果")

    input("\n按 Enter 继续...")

    # 检查初始状态
    check_steam_registry()

    input("\n按 Enter 开始配置...")

    # 配置 Steam
    test_configure()

    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)
    print("\n重要提示：")
    print("1. 完全关闭 Steam（右键托盘图标 → 退出）")
    print("2. 启动 NetBooster 并点击「一键加速」")
    print("3. 重新启动 Steam")
    print("4. 开始下载游戏并观察 NetBooster 日志")
