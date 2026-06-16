"""
HypoMux 设置面板 - SettingsWidget

独立于 MainWindow 的设置页面组件，通过 Qt Signal 与父窗口通信。
所有用户配置通过 QSettings("Hypostasis-Cat", "HypoMux") 持久化到 Windows 注册表。

设计原则：
- 不持有 MainWindow 引用，仅通过信号通知外部状态变更
- ProxyWorker 异步任务不受页面切换影响（QStackedWidget 仅改变可见性）
- 使用 ui.i18n.tr() 字典查表实现双语，retranslate_ui() 刷新所有文本
"""

from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QSpinBox, QGroupBox, QListView,
)
from PySide6.QtCore import Signal, QSettings
from qfluentwidgets import PushButton

from ui.i18n import tr, get_language


# 默认端口常量（与 main_window 保持一致）
DEFAULT_SOCKS_PORT = 10800
DEFAULT_HTTP_PORT = 10801


class SettingsWidget(QFrame):
    """HypoMux 设置面板

    Signals:
        back_clicked            - 用户点击「返回主界面」
        info_message(str)       - 需要在父窗口显示 info 级别提示
        success_message(str)    - 需要在父窗口显示 success 级别提示
        warning_message(str)    - 需要在父窗口显示 warning 级别提示
        ports_changed(int, int) - (socks_port, http_port) 端口修改后通知
        language_changed(str)   - 语言切换后通知父窗口刷新全部文本
    """

    back_clicked = Signal()
    info_message = Signal(str)
    success_message = Signal(str)
    warning_message = Signal(str)
    ports_changed = Signal(int, int)
    language_changed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("settingsPanel")
        self._init_ui()
        self.retranslate_ui()

    def _init_ui(self):
        settings = QSettings("Hypostasis-Cat", "HypoMux")

        self.setStyleSheet("""
            QFrame#settingsPanel {
                background: #f7fbff;
                border: 1px solid rgba(0, 0, 0, 0.08);
                border-radius: 12px;
            }
            QLabel {
                color: #1a1a1a;
            }
            QComboBox {
                border: 1px solid rgba(0, 0, 0, 0.10);
                border-radius: 8px;
                padding: 8px 10px;
                padding-right: 30px;
                background: #ffffff;
                color: #1a1a1a;
                min-width: 120px;
            }
            QComboBox:hover {
                border: 1px solid rgba(0, 120, 212, 0.35);
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: center right;
                width: 26px;
                border: none;
                background: transparent;
            }
            QComboBox::down-arrow {
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 5px solid #64748b;
                width: 0px;
                height: 0px;
            }
            QComboBox::indicator {
                width: 0px;
                height: 0px;
                background: transparent;
                border: none;
            }
            QComboBox QAbstractItemView {
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                background-color: #ffffff;
                outline: 0px;
                padding: 4px 0px;
            }
            QComboBox QAbstractItemView::item {
                height: 28px;
                padding-left: 12px;
                color: #333333;
                background-color: transparent;
            }
            QComboBox QAbstractItemView::item:hover,
            QComboBox QAbstractItemView::item:selected {
                background-color: #e6f3ff;
                color: #1080ee;
            }
            QSpinBox {
                background: #ffffff;
                border: 1px solid rgba(0, 0, 0, 0.10);
                border-radius: 8px;
                padding: 8px 10px;
                color: #1a1a1a;
                min-width: 120px;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                width: 0; height: 0; border: none;
            }
            QGroupBox {
                font-weight: 600;
                font-size: 14px;
                color: #334155;
                border: 1px solid rgba(0, 78, 140, 0.08);
                border-radius: 8px;
                margin-top: 16px;
                padding: 20px 16px 16px 16px;
                background: #f8fafc;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 16px;
                padding: 0 6px;
                background: #f8fafc;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        # ===== 顶部标题 + 返回按钮 =====
        top_bar = QHBoxLayout()
        top_bar.setSpacing(12)

        self.back_btn = PushButton("")
        self.back_btn.setMinimumHeight(36)
        self.back_btn.setMaximumWidth(140)
        self.back_btn.clicked.connect(self.back_clicked.emit)
        self.back_btn.setStyleSheet("""
            QPushButton {
                background: rgba(0, 120, 212, 0.08);
                color: #0078d4;
                border: 1px solid rgba(0, 120, 212, 0.18);
                border-radius: 8px;
                padding: 6px 14px;
                font-size: 13px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: rgba(0, 120, 212, 0.14);
                border: 1px solid rgba(0, 120, 212, 0.28);
            }
            QPushButton:pressed {
                background: rgba(0, 120, 212, 0.20);
            }
        """)

        self.settings_title_label = QLabel("")
        self.settings_title_label.setStyleSheet("font-size: 20px; font-weight: 700; color: #1a1a1a;")

        top_bar.addWidget(self.back_btn)
        top_bar.addWidget(self.settings_title_label)
        top_bar.addStretch()
        layout.addLayout(top_bar)

        # ===== 全局设置区域 =====
        self.global_group = QGroupBox("")
        global_layout = QVBoxLayout(self.global_group)
        global_layout.setSpacing(12)

        # 语言选择
        lang_row = QHBoxLayout()
        self.lang_label = QLabel("")
        self.lang_label.setStyleSheet("font-weight: 600; color: #526579;")
        self.lang_combo = QComboBox()
        self.lang_combo.setView(QListView())
        self.lang_combo.addItem("中文 (Chinese)", "zh")
        self.lang_combo.addItem("English", "en")
        saved_lang = settings.value("language", "zh")
        idx = self.lang_combo.findData(saved_lang)
        if idx >= 0:
            self.lang_combo.setCurrentIndex(idx)
        self.lang_combo.currentIndexChanged.connect(self._on_language_changed)
        lang_row.addWidget(self.lang_label)
        lang_row.addStretch()
        lang_row.addWidget(self.lang_combo)
        global_layout.addLayout(lang_row)

        # 本地代理端口
        port_row = QHBoxLayout()
        self.port_title = QLabel("")
        self.port_title.setStyleSheet("font-weight: 600; color: #526579;")
        port_row.addWidget(self.port_title)
        port_row.addStretch()

        self.http_label = QLabel("")
        self.http_label.setStyleSheet("color: #526579;")
        self.settings_http_port = QSpinBox()
        self.settings_http_port.setMinimum(1)
        self.settings_http_port.setMaximum(65534)
        self.settings_http_port.setButtonSymbols(QSpinBox.NoButtons)
        saved_http = settings.value("http_port", DEFAULT_HTTP_PORT, type=int)
        self.settings_http_port.setValue(saved_http)
        self.settings_http_port.valueChanged.connect(self._on_port_changed)

        self.socks_label = QLabel("")
        self.socks_label.setStyleSheet("color: #526579;")
        self.settings_socks_port = QSpinBox()
        self.settings_socks_port.setMinimum(1)
        self.settings_socks_port.setMaximum(65534)
        self.settings_socks_port.setButtonSymbols(QSpinBox.NoButtons)
        saved_socks = settings.value("socks_port", DEFAULT_SOCKS_PORT, type=int)
        self.settings_socks_port.setValue(saved_socks)
        self.settings_socks_port.valueChanged.connect(self._on_port_changed)

        port_row.addWidget(self.http_label)
        port_row.addWidget(self.settings_http_port)
        port_row.addSpacing(12)
        port_row.addWidget(self.socks_label)
        port_row.addWidget(self.settings_socks_port)
        global_layout.addLayout(port_row)

        layout.addWidget(self.global_group)

        # ===== 关于项目区域 =====
        self.about_group = QGroupBox("")
        about_layout = QVBoxLayout(self.about_group)
        about_layout.setSpacing(10)

        self.version_label = QLabel("")
        self.version_label.setStyleSheet("color: #526579; font-weight: 600;")
        about_layout.addWidget(self.version_label)

        self.repo_label = QLabel(
            '<a href="https://github.com/Hypostasis-Cat/HypoMux" '
            'style="color: #0078d4; text-decoration: none; font-weight: 600;">'
            'https://github.com/Hypostasis-Cat/HypoMux</a>'
        )
        self.repo_label.setOpenExternalLinks(True)
        self.repo_label.setStyleSheet("padding: 4px 0;")
        about_layout.addWidget(self.repo_label)

        layout.addWidget(self.about_group)
        layout.addStretch()

    # ---------- 国际化刷新 ----------
    def retranslate_ui(self):
        """根据当前 QSettings 语言刷新所有可见文本"""
        self.back_btn.setText(tr("settings_back"))
        self.settings_title_label.setText(tr("settings_title"))
        self.global_group.setTitle(tr("settings_global"))
        self.lang_label.setText(tr("settings_language"))
        self.port_title.setText(tr("settings_proxy_port"))
        self.http_label.setText(tr("settings_http_label"))
        self.socks_label.setText(tr("settings_socks_label"))
        self.about_group.setTitle(tr("settings_about"))
        self.version_label.setText(tr("settings_version"))

    # ---------- 交互逻辑 ----------
    def _on_language_changed(self, index):
        """语言切换后持久化到注册表并立即刷新全部 UI"""
        settings = QSettings("Hypostasis-Cat", "HypoMux")
        lang_code = self.lang_combo.itemData(index)
        settings.setValue("language", lang_code)
        settings.sync()
        # 先刷新自身
        self.retranslate_ui()
        # 通知父窗口也刷新
        self.language_changed.emit(lang_code)
        self.info_message.emit(tr("settings_lang_saved"))

    def _on_port_changed(self):
        """端口修改后持久化到注册表并通知父窗口同步"""
        settings = QSettings("Hypostasis-Cat", "HypoMux")
        socks_port = self.settings_socks_port.value()
        http_port = self.settings_http_port.value()
        settings.setValue("socks_port", socks_port)
        settings.setValue("http_port", http_port)
        settings.sync()
        self.ports_changed.emit(socks_port, http_port)

