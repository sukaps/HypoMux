"""
测试系统代理自动配置功能
"""

import sys
from utils.app_configurator import AppConfigurator


def test_system_proxy():
    """测试系统代理配置和恢复"""
    print("=" * 60)
    print("NetBooster 系统代理自动配置测试")
    print("=" * 60)

    configurator = AppConfigurator(proxy_host="127.0.0.1", proxy_port=1080)

    # 1. 获取当前系统代理状态
    print("\n[1] 检查当前系统代理状态...")
    enabled, server = configurator.get_current_system_proxy()
    print(f"   系统代理已启用: {enabled}")
    if enabled:
        print(f"   当前代理地址: {server}")
    else:
        print(f"   系统代理未启用")

    # 2. 配置系统代理
    print("\n[2] 配置系统代理为 socks=127.0.0.1:1080 ...")
    success, msg = configurator.configure_system_proxy(auto_mode=False)
    if success:
        print(f"   [成功] {msg}")
    else:
        print(f"   [失败] {msg}")
        return

    # 3. 验证配置结果
    print("\n[3] 验证系统代理配置...")
    enabled, server = configurator.get_current_system_proxy()
    print(f"   系统代理已启用: {enabled}")
    print(f"   当前代理地址: {server}")

    # 4. 提示用户测试
    print("\n[4] 请打开浏览器测试系统代理是否生效")
    print("   （注意：需要先启动 NetBooster 的 SOCKS5 代理服务器）")
    input("\n按 Enter 键继续恢复原始设置...")

    # 5. 恢复系统代理
    print("\n[5] 恢复系统代理设置...")
    if not enabled or server == "":
        # 原本就没启用，直接禁用
        success, msg = configurator.restore_system_proxy(auto_mode=False)
        if success:
            print(f"   [成功] {msg}")
        else:
            print(f"   [失败] {msg}")
    else:
        print(f"   检测到原始代理配置: {server}")
        print(f"   已保留原始设置（仅禁用了代理）")

    # 6. 最终验证
    print("\n[6] 最终验证...")
    enabled, server = configurator.get_current_system_proxy()
    print(f"   系统代理已启用: {enabled}")
    if enabled:
        print(f"   当前代理地址: {server}")
    else:
        print(f"   系统代理已禁用")

    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)


if __name__ == "__main__":
    try:
        test_system_proxy()
    except KeyboardInterrupt:
        print("\n\n用户中断测试")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n[错误] 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
