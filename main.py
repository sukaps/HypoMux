"""
HypoMux - Windows 多网卡跃点数并发调度工具
主应用入口 (v1.2.0)

严格的启动生命周期：
1. 检测管理员权限（纯逻辑，无 Qt 依赖）
2. 创建 QApplication（最首要的 Qt 对象）
3. 读取 QSettings 配置（语言等），加载 QTranslator
4. 延迟导入 MainWindow（此时 QApplication 已就位）
5. 权限安全防线检测
6. 初始化界面并运行事件循环
"""

import sys
import os
import ctypes

# 仅导入非 Qt 模块 - 严禁在此处导入任何 UI 相关模块
from utils.network_utils import is_admin


def check_admin_privileges():
    """
    检测管理员权限（纯逻辑函数，不创建任何 Qt 对象）

    Returns:
        bool: True 表示已有管理员权限，False 表示需要提权
    """
    if is_admin():
        print("[INFO] 程序已以管理员身份运行")
        return True
    else:
        print("[INFO] 程序无管理员权限")
        return False


def register_windows_app_id():
    """为 Windows 注册独立的 AppUserModelID，避免任务栏图标被系统合并。"""
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
            "hypostasiscat.hypomux.accelerator.v2"
        )
    except Exception:
        pass


if __name__ == "__main__":
    # ========== 第一步：检测管理员权限（纯逻辑，无 Qt） ==========
    admin_check = check_admin_privileges()

    # ========== 第二步：立刻创建 QApplication（在任何 QWidget 之前）==========
    register_windows_app_id()
    from PySide6.QtCore import QCoreApplication, QSettings, QTranslator
    from PySide6.QtGui import QIcon
    from PySide6.QtWidgets import QApplication, QMessageBox
    
    runtime_dir = os.path.dirname(os.path.abspath(__file__))
    qt_plugin_path = os.path.join(runtime_dir, "PySide6", "qt-plugins")
    icon_path = os.path.join(runtime_dir, "assets", "icon.ico")
    
    if os.path.exists(qt_plugin_path):
        QCoreApplication.addLibraryPath(qt_plugin_path)
        os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = os.path.join(qt_plugin_path, "platforms")
        
    app = QApplication(sys.argv)
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    # ========== 第三步：读取 QSettings 并加载语言包 ==========
    settings = QSettings("Hypostasis-Cat", "HypoMux")
    language = settings.value("language", "zh")

    translator = QTranslator()
    if language == "en":
        i18n_path = os.path.join(runtime_dir, "i18n", "hypomux_en.qm")
        if os.path.exists(i18n_path):
            translator.load(i18n_path)
            app.installTranslator(translator)
            print("[INFO] 已加载英文语言包")
        else:
            print("[INFO] 英文语言包文件不存在，使用内置英文回退")

    # ========== 第四步：延迟导入 MainWindow（现在 QApplication 已存在）==========
    from ui.main_window import create_main_window

    # ========== 第五步：双模自适应权限防线 ==========
    if not admin_check:
        # 检测当前是否属于打包后的运行状态 (Nuitka / PyInstaller 会注入 frozen 属性)
        is_compiled = getattr(sys, 'frozen', False) or ('__compiled__' in globals())
        
        if is_compiled:
            # 如果是打包后的 .exe 状态，说明操作系统的强制 UAC 提权被用户在外面拦截取消了
            print("[WARN] 权限拦截：打包程序未获得管理员权限")
            QMessageBox.critical(
                None,
                "需要管理员权限",
                "HypoMux 需要管理员权限来修改网卡配置与跃点数。\n\n请右键选择「以管理员身份运行」本程序。"
            )
            sys.exit(1)
        else:
            # 如果是本地源码运行 (python main.py)，则允许激活旧版的延迟导入和自动提权拉起
            from utils.network_utils import elevate_privileges
            print("[INFO] 源码运行环境：正在请求本地 UAC 提权重启...")
            
            reply = QMessageBox.information(
                None,
                "需要管理员权限 (源码调试)",
                "当前正在以源码模式运行，HypoMux 需要请求管理员权限来继续调试。\n\n点击「确定」将尝试触发本地提权拉起。",
                QMessageBox.Ok | QMessageBox.Cancel
            )
            if reply == QMessageBox.Ok:
                elevate_privileges()  # 调用你 utils 里的原版提权函数
            sys.exit(1)

    # ========== 第六步：配置应用属性 ==========
    app.setApplicationName("HypoMux")
    app.setApplicationVersion("1.2.0")
    app.setStyle("Fusion")

    # ========== 第七步：创建并显示主窗口（工厂函数模式）==========
    try:
        window = create_main_window()
        if os.path.exists(icon_path):
            window.setWindowIcon(QIcon(icon_path))
        window.show()
        print("[INFO] 主界面已启动")
    except Exception as e:
        print(f"[ERROR] 创建主窗口失败: {e}")
        QMessageBox.critical(None, "启动失败", f"无法创建主窗口: {e}")
        sys.exit(1)

    # ========== 第八步：运行应用事件循环 ==========
    sys.exit(app.exec())