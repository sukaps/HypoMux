"""
HypoMux 国际化模块 - Python 原生字典查表法

无需 .qm 外部文件，兼容 Nuitka 单文件打包。
所有界面文本通过 tr(key) 函数统一获取，语言切换时由各组件的
retranslate_ui() 方法批量刷新 .setText()。
"""

from PySide6.QtCore import QSettings


# 全局双语映射字典
I18N_MAP = {
    "zh": {
        # === 主窗口 ===
        "window_title": "HypoMux - Windows 多网卡双协议分流加速",
        "subtitle": "多网卡 HTTP/HTTPS/SOCKS 分流引擎 · 实时分流大屏",
        "settings_btn": "设置",
        "status_loading": "状态: 正在加载网卡...",
        "status_no_adapters": "状态: 未找到可用的网卡",
        "status_loaded": "状态: 已加载 {count} 个网卡，就绪",
        "status_load_failed": "状态: 加载失败",
        "status_starting": "状态: 正在启动双协议分流引擎...",
        "status_stopping": "状态: 正在停止...",
        "status_stopped": "状态: 已停止，就绪",
        "status_start_failed": "状态: 启动失败",
        "status_running": "状态: 双协议分流引擎运行中 @ {endpoint}",
        "status_running_live": "状态: 分流运行中 · 下行 {down:.2f} MB/s · 连接 {conn}",

        # 表头
        "col_select": "选择",
        "col_alias": "网卡别名",
        "col_ipv4": "IPv4 地址",
        "col_speed": "实时速度 (MB/s)",
        "col_conn": "实时连接数",

        # 数据大屏
        "speed_caption": "合并下行总速度 (MB/s)",
        "up_format": "上行 {value:.2f} MB/s",
        "conn_format": "总连接数 {value}",

        # 控制台
        "console_caption": "调度控制台",

        # 操作栏
        "select_all": "全选",
        "deselect_all": "取消全选",
        "port_label": "SOCKS 端口",
        "boost_start": "一键加速",
        "boost_stop": "停止加速",

        # 警告/提示
        "warn_boosting_refresh": "加速运行中，请先停止再刷新网卡",
        "warn_no_adapters": "未找到任何可用的网卡",
        "warn_no_selection": "请先勾选至少一张拥有有效 IPv4 的网卡",
        "error_load_adapters": "加载网卡失败:\n\n{error}",
        "error_start_failed": "分流引擎启动失败:\n\n{error}",
        "error_proxy_write": "双协议引擎已监听，但无法写入 Windows 系统代理:\n\n{error}",

        # InfoBar 标题
        "infobar_info": "提示",
        "infobar_success": "成功",
        "infobar_warning": "警告",
        "infobar_error": "错误",

        # === 设置面板 ===
        "settings_back": "< 返回主界面",
        "settings_title": "设置",
        "settings_global": "全局设置",
        "settings_language": "软件语言 (Language)",
        "settings_proxy_port": "本地代理端口",
        "settings_http_label": "HTTP:",
        "settings_socks_label": "SOCKS5:",
        "settings_about": "关于项目",
        "settings_version": "当前版本: v1.2 (Stable)",
        "settings_lang_saved": "界面语言已切换",
    },

    "en": {
        # === Main Window ===
        "window_title": "HypoMux - Multi-NIC Dual-Protocol Traffic Splitting",
        "subtitle": "Multi-NIC HTTP/HTTPS/SOCKS Splitting Engine · Live Dashboard",
        "settings_btn": "Settings",
        "status_loading": "Status: Loading network adapters...",
        "status_no_adapters": "Status: No available adapters found",
        "status_loaded": "Status: {count} adapter(s) loaded, ready",
        "status_load_failed": "Status: Load failed",
        "status_starting": "Status: Starting dual-protocol engine...",
        "status_stopping": "Status: Stopping...",
        "status_stopped": "Status: Stopped, ready",
        "status_start_failed": "Status: Start failed",
        "status_running": "Status: Dual-protocol engine running @ {endpoint}",
        "status_running_live": "Status: Running · Down {down:.2f} MB/s · Conn {conn}",

        # Table headers
        "col_select": "Select",
        "col_alias": "Adapter Alias",
        "col_ipv4": "IPv4 Address",
        "col_speed": "Speed (MB/s)",
        "col_conn": "Connections",

        # Dashboard
        "speed_caption": "Combined Download Speed (MB/s)",
        "up_format": "Up {value:.2f} MB/s",
        "conn_format": "Connections {value}",

        # Console
        "console_caption": "Dispatch Console",

        # Action bar
        "select_all": "Select All",
        "deselect_all": "Deselect All",
        "port_label": "SOCKS Port",
        "boost_start": "Boost",
        "boost_stop": "Stop",

        # Warnings / Messages
        "warn_boosting_refresh": "Boosting in progress, stop first before refreshing",
        "warn_no_adapters": "No available network adapters found",
        "warn_no_selection": "Please select at least one adapter with a valid IPv4",
        "error_load_adapters": "Failed to load adapters:\n\n{error}",
        "error_start_failed": "Engine start failed:\n\n{error}",
        "error_proxy_write": "Engine is listening but cannot write system proxy:\n\n{error}",

        # InfoBar titles
        "infobar_info": "Info",
        "infobar_success": "Success",
        "infobar_warning": "Warning",
        "infobar_error": "Error",

        # === Settings Panel ===
        "settings_back": "< Back",
        "settings_title": "Settings",
        "settings_global": "Global Settings",
        "settings_language": "Language",
        "settings_proxy_port": "Local Proxy Ports",
        "settings_http_label": "HTTP:",
        "settings_socks_label": "SOCKS5:",
        "settings_about": "About",
        "settings_version": "Version: v1.2 (Stable)",
        "settings_lang_saved": "Language switched",
    },
}


def get_language() -> str:
    """读取 QSettings 中保存的语言代码，默认 zh"""
    settings = QSettings("Hypostasis-Cat", "HypoMux")
    lang = settings.value("language", "zh")
    if lang not in I18N_MAP:
        lang = "zh"
    return lang


def tr(key: str, **kwargs) -> str:
    """根据当前语言获取翻译文本

    Args:
        key: I18N_MAP 中的键名
        **kwargs: 用于 str.format() 的动态参数

    Returns:
        翻译后的字符串，如果 key 不存在则原样返回 key
    """
    lang = get_language()
    text = I18N_MAP.get(lang, I18N_MAP["zh"]).get(key, key)
    if kwargs:
        try:
            return text.format(**kwargs)
        except (KeyError, ValueError):
            return text
    return text
