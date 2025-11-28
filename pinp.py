#!/usr/bin/env python3
"""
PinP (Picture-in-Picture) Cursor Magnifier

A Python + PyQt5 application that creates a small window which:
- Always moves near the cursor position
- Displays magnified view of the area around the cursor
- Has transparent frame, shadow, and rounded corners
- Lightweight (100fps+ capable)
"""

import sys
from typing import Optional, Tuple

from PyQt5.QtCore import Qt, QTimer, QRect, QPoint
from PyQt5.QtGui import (
    QPainter, QColor, QPen, QBrush, QPainterPath,
    QPixmap, QScreen, QCursor
)
from PyQt5.QtWidgets import QApplication, QWidget


class PinPWindow(QWidget):
    """A floating magnifier window that follows the cursor."""

    def __init__(
        self,
        window_size: Tuple[int, int] = (200, 200),
        magnification: float = 2.0,
        update_interval_ms: int = 10,  # ~100 fps
        offset: int = 50,
        corner_radius: int = 15,
        border_width: int = 2,
        shadow_offset: int = 5,
    ):
        """
        Initialize the PinP window.

        Args:
            window_size: Size of the magnifier window (width, height)
            magnification: Zoom factor for the magnified view
            update_interval_ms: Update interval in milliseconds (lower = smoother)
            offset: Distance from cursor to window
            corner_radius: Radius for rounded corners
            border_width: Width of the window border
            shadow_offset: Offset for drop shadow effect
        """
        super().__init__()

        self.window_width, self.window_height = window_size
        self.magnification = magnification
        self.offset = offset
        self.corner_radius = corner_radius
        self.border_width = border_width
        self.shadow_offset = shadow_offset

        # Cache for the captured screen content
        self._cached_pixmap: Optional[QPixmap] = None

        self._setup_window()
        self._setup_timer(update_interval_ms)

    def _setup_window(self) -> None:
        """Configure window properties for frameless, transparent display."""
        # Set window flags for always-on-top, frameless, transparent
        flags = (
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool  # Don't show in taskbar
        )

        # Add X11-specific flag only on X11 platforms
        if sys.platform.startswith('linux'):
            flags |= Qt.WindowType.X11BypassWindowManagerHint

        self.setWindowFlags(flags)

        # Enable transparency
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Set fixed size (including space for shadow)
        total_width = self.window_width + self.shadow_offset
        total_height = self.window_height + self.shadow_offset
        self.setFixedSize(total_width, total_height)

        # Make the window ignore mouse events (click-through)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

    def _setup_timer(self, interval_ms: int) -> None:
        """Set up the update timer for screen capture and window movement."""
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_position_and_capture)
        self.timer.start(interval_ms)

    def _get_screen(self) -> Optional[QScreen]:
        """Get the screen containing the cursor."""
        cursor_pos = QCursor.pos()
        for screen in QApplication.screens():
            if screen.geometry().contains(cursor_pos):
                return screen
        return QApplication.primaryScreen()

    def _calculate_window_position(self, cursor_pos: QPoint) -> QPoint:
        """
        Calculate the window position to stay near but not under the cursor.

        The window is positioned in one of four quadrants relative to the cursor,
        choosing the quadrant that keeps the window on screen.
        """
        screen = self._get_screen()
        if not screen:
            return cursor_pos

        screen_geometry = screen.geometry()
        total_width = self.window_width + self.shadow_offset
        total_height = self.window_height + self.shadow_offset

        # Try bottom-right of cursor first
        x = cursor_pos.x() + self.offset
        y = cursor_pos.y() + self.offset

        # Adjust if window would go off the right edge
        if x + total_width > screen_geometry.right():
            x = cursor_pos.x() - self.offset - total_width

        # Adjust if window would go off the bottom edge
        if y + total_height > screen_geometry.bottom():
            y = cursor_pos.y() - self.offset - total_height

        # Ensure window stays on screen
        x = max(screen_geometry.left(), min(x, screen_geometry.right() - total_width))
        y = max(screen_geometry.top(), min(y, screen_geometry.bottom() - total_height))

        return QPoint(x, y)

    def _capture_screen_area(self, cursor_pos: QPoint) -> Optional[QPixmap]:
        """
        Capture the screen area around the cursor.

        Args:
            cursor_pos: Current cursor position

        Returns:
            QPixmap of the captured area, or None if capture fails
        """
        screen = self._get_screen()
        if not screen:
            return None

        # Calculate the source area size based on magnification
        source_width = int(self.window_width / self.magnification)
        source_height = int(self.window_height / self.magnification)

        # Center the capture area on the cursor
        source_x = cursor_pos.x() - source_width // 2
        source_y = cursor_pos.y() - source_height // 2

        # Get screen geometry for bounds checking
        screen_geometry = screen.geometry()

        # Clamp capture area to screen bounds
        source_x = max(screen_geometry.left(), source_x)
        source_y = max(screen_geometry.top(), source_y)

        # Ensure we don't capture beyond screen boundaries
        if source_x + source_width > screen_geometry.right():
            source_x = screen_geometry.right() - source_width
        if source_y + source_height > screen_geometry.bottom():
            source_y = screen_geometry.bottom() - source_height

        # Capture the screen area
        pixmap = screen.grabWindow(
            0,  # Window ID (0 = entire screen)
            source_x,
            source_y,
            source_width,
            source_height
        )

        return pixmap

    def _update_position_and_capture(self) -> None:
        """Update window position and capture screen content."""
        cursor_pos = QCursor.pos()

        # Move window to new position
        new_pos = self._calculate_window_position(cursor_pos)
        self.move(new_pos)

        # Capture screen around cursor
        self._cached_pixmap = self._capture_screen_area(cursor_pos)

        # Trigger repaint
        self.update()

    def paintEvent(self, event) -> None:
        """Draw the magnified content with rounded corners and shadow."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw shadow
        shadow_path = QPainterPath()
        shadow_rect = QRect(
            self.shadow_offset,
            self.shadow_offset,
            self.window_width,
            self.window_height
        )
        shadow_path.addRoundedRect(
            shadow_rect.x(),
            shadow_rect.y(),
            shadow_rect.width(),
            shadow_rect.height(),
            self.corner_radius,
            self.corner_radius
        )
        painter.fillPath(shadow_path, QColor(0, 0, 0, 50))

        # Create rounded rectangle path for the main window
        main_path = QPainterPath()
        main_rect = QRect(0, 0, self.window_width, self.window_height)
        main_path.addRoundedRect(
            main_rect.x(),
            main_rect.y(),
            main_rect.width(),
            main_rect.height(),
            self.corner_radius,
            self.corner_radius
        )

        # Clip to rounded rectangle
        painter.setClipPath(main_path)

        # Draw the captured content
        if self._cached_pixmap and not self._cached_pixmap.isNull():
            # Scale the captured pixmap to fill the window
            scaled = self._cached_pixmap.scaled(
                self.window_width,
                self.window_height,
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation
            )
            painter.drawPixmap(0, 0, scaled)
        else:
            # Draw placeholder if no capture available
            painter.fillPath(main_path, QColor(50, 50, 50))

        # Remove clip and draw border
        painter.setClipPath(QPainterPath())

        # Draw border
        border_pen = QPen(QColor(255, 255, 255, 180), self.border_width)
        painter.setPen(border_pen)
        painter.drawRoundedRect(
            self.border_width // 2,
            self.border_width // 2,
            self.window_width - self.border_width,
            self.window_height - self.border_width,
            self.corner_radius,
            self.corner_radius
        )

        # Draw crosshair at center to indicate cursor position
        center_x = self.window_width // 2
        center_y = self.window_height // 2
        crosshair_size = 10

        crosshair_pen = QPen(QColor(255, 0, 0, 200), 2)
        painter.setPen(crosshair_pen)
        painter.drawLine(
            center_x - crosshair_size, center_y,
            center_x + crosshair_size, center_y
        )
        painter.drawLine(
            center_x, center_y - crosshair_size,
            center_x, center_y + crosshair_size
        )

        painter.end()

    def keyPressEvent(self, event) -> None:
        """Handle key press events."""
        # Exit on Escape key
        if event.key() == Qt.Key.Key_Escape:
            self.close()


def main():
    """Main entry point for the PinP application."""
    app = QApplication(sys.argv)

    # Create and show the magnifier window
    window = PinPWindow(
        window_size=(250, 250),
        magnification=2.0,
        update_interval_ms=10,  # ~100 fps
        offset=30,
        corner_radius=15,
        border_width=2,
        shadow_offset=8,
    )
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
