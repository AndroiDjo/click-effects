import sys
import winsound
import os
import random
from pynput import mouse
from PyQt6.QtCore import Qt, QTimer, QPointF
from PyQt6.QtGui import QColor, QPainter, QPen
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtCore import QMetaObject, Q_ARG
from PyQt6.QtCore import pyqtSlot

# ---------------------------
# Ripple Overlay Widget
# ---------------------------

class RippleOverlay(QWidget):
    def __init__(self):
        super().__init__()

        # transparent click-through window
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool |
            Qt.WindowType.WindowTransparentForInput |
            Qt.WindowType.BypassWindowManagerHint
        )

        # animation config
        self.duration = 300
        self.fps = 60
        self.frames = int(self.duration / (1000 / self.fps))
        self.frame = 0

        self.start_radius = 12
        self.end_radius = 36

        self.start_thickness = 9
        self.end_thickness = 3

        self.color = QColor("#26F7FF")
        self.glow_color = QColor("#8AFDFF")

        self.glow_width = 14

        self.opacity_start = 1.0
        self.opacity_end = 0.0

        self.timer = QTimer()
        self.timer.timeout.connect(self.animate)

    # easing
    def ease(self, t):
        return 1 - (1 - t)**5  # EaseOutQuint

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        t = self.ease(self.frame / self.frames)

        radius = self.start_radius + (self.end_radius - self.start_radius) * t
        thickness = self.start_thickness + (self.end_thickness - self.start_thickness) * t
        opacity = self.opacity_start + (self.opacity_end - self.opacity_start) * t

        # glow
        glow_pen = QPen(self.glow_color)
        glow_pen.setWidth(self.glow_width)
        glow_pen.setColor(QColor(
            self.glow_color.red(),
            self.glow_color.green(),
            self.glow_color.blue(),
            int(80 * (1 - t))
        ))
        painter.setPen(glow_pen)
        painter.drawEllipse(
            int(self.width()/2 - radius),
            int(self.height()/2 - radius),
            int(radius * 2),
            int(radius * 2)
        )

        # main ring
        pen = QPen(self.color)
        pen.setWidth(int(thickness))
        pen.setColor(QColor(
            self.color.red(),
            self.color.green(),
            self.color.blue(),
            int(255 * opacity)
        ))
        painter.setPen(pen)
        painter.drawEllipse(
            int(self.width()/2 - radius),
            int(self.height()/2 - radius),
            int(radius * 2),
            int(radius * 2)
        )

    def animate(self):
        self.frame += 1
        if self.frame >= self.frames:
            self.timer.stop()
            self.hide()
            return
        self.repaint()

    @pyqtSlot(int, int)
    def trigger_ripple(self, x, y):
        self.play_random_sound()
        
        self.frame = 0

        size = (self.end_radius + self.glow_width) * 4
        self.resize(size, size)
        self.move(int(x - size/2), int(y - size/2))

        self.show()
        self.timer.start(int(1000 / self.fps))

    def play_random_sound(self):
        folder = os.path.join(os.path.dirname(sys.argv[0]), "click_sounds")

        if not os.path.exists(folder):
            return

        files = [f for f in os.listdir(folder) 
                if f.lower().endswith(".wav")]

        if not files:
            return

        sound_file = os.path.join(folder, random.choice(files))

        try:
            winsound.PlaySound(sound_file, winsound.SND_ASYNC | winsound.SND_FILENAME)
        except:
            pass



# ---------------------------
# Global Mouse Hook
# ---------------------------

def on_click(x, y, button, pressed):
    if pressed:
        QMetaObject.invokeMethod(
            app.overlay,
            "trigger_ripple",
            Qt.ConnectionType.QueuedConnection,
            Q_ARG(int, x),
            Q_ARG(int, y)
        )

# ---------------------------
# Main
# ---------------------------

class App(QApplication):
    def __init__(self, args):
        super().__init__(args)
        self.overlay = RippleOverlay()


if __name__ == "__main__":
    app = App(sys.argv)

    # start global mouse listener
    listener = mouse.Listener(on_click=on_click)
    listener.start()

    sys.exit(app.exec())
