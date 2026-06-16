"""
HypoMux UI Components - SlidingStackedWidget

Windows 11 阻尼感水平滑动动画页面容器。
基于 QPropertyAnimation + QParallelAnimationGroup 实现丝滑过渡。
"""

from PySide6.QtWidgets import QStackedWidget
from PySide6.QtCore import (
    QPropertyAnimation, QParallelAnimationGroup,
    QEasingCurve, QPoint, Qt,
)


class SlidingStackedWidget(QStackedWidget):
    """带水平滑动动画的 QStackedWidget 替代品。

    特性:
    - 350ms OutCubic 缓动曲线，模拟 Win11 阻尼感
    - 动画期间状态锁，防止高频点击导致界面卡死
    - 不销毁/重构任何子页面，仅操作 pos 属性
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._is_animating = False
        self._duration = 350
        self._easing = QEasingCurve.OutCubic
        self._direction = Qt.Horizontal
        self._anim_group = None

    def slide_to_index(self, index: int):
        """滑动切换到指定页面索引。

        如果目标就是当前页，或动画正在播放中，则直接忽略。
        """
        if self._is_animating:
            return
        if index == self.currentIndex():
            return
        if index < 0 or index >= self.count():
            return

        self._is_animating = True

        # 确定滑动方向：目标在右侧则当前页左移，反之右移
        width = self.frameRect().width()
        current_widget = self.currentWidget()
        next_widget = self.widget(index)

        if index > self.currentIndex():
            # 向左滑：下一页从右侧进入
            offset_current = QPoint(-width, 0)
            offset_next = QPoint(width, 0)
        else:
            # 向右滑：下一页从左侧进入
            offset_current = QPoint(width, 0)
            offset_next = QPoint(-width, 0)

        # 将目标页预设为容器满尺寸，强制完成首次布局计算（消除初次塌陷闪烁）
        current_pos = current_widget.pos()
        height = self.frameRect().height()
        next_widget.setGeometry(0, 0, width, height)
        next_widget.ensurePolished()
        if next_widget.layout():
            next_widget.layout().activate()

        # 移到起始偏移位置并显示
        next_widget.move(current_pos + offset_next)
        next_widget.show()
        next_widget.raise_()

        # 当前页滑出动画
        anim_current = QPropertyAnimation(current_widget, b"pos")
        anim_current.setDuration(self._duration)
        anim_current.setEasingCurve(self._easing)
        anim_current.setStartValue(current_pos)
        anim_current.setEndValue(current_pos + offset_current)

        # 目标页滑入动画
        anim_next = QPropertyAnimation(next_widget, b"pos")
        anim_next.setDuration(self._duration)
        anim_next.setEasingCurve(self._easing)
        anim_next.setStartValue(current_pos + offset_next)
        anim_next.setEndValue(current_pos)

        # 并行执行
        self._anim_group = QParallelAnimationGroup(self)
        self._anim_group.addAnimation(anim_current)
        self._anim_group.addAnimation(anim_next)

        # 动画结束后收尾
        target_index = index

        def _on_finished():
            self.setCurrentIndex(target_index)
            current_widget.move(current_pos)  # 归位，防止后续布局错乱
            self._is_animating = False
            self._anim_group = None

        self._anim_group.finished.connect(_on_finished)
        self._anim_group.start()
