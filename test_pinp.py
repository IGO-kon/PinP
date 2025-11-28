#!/usr/bin/env python3
"""
Tests for PinP cursor magnifier application.
"""

# Set offscreen platform before importing any Qt modules
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

import sys
import unittest
from unittest.mock import Mock, patch

from PyQt5.QtCore import QPoint, QRect
from PyQt5.QtWidgets import QApplication

# Create application instance for tests
app = QApplication.instance() or QApplication(sys.argv)


class TestPinPWindow(unittest.TestCase):
    """Test cases for the PinPWindow class."""

    def test_import(self):
        """Test that the module can be imported."""
        from pinp import PinPWindow
        self.assertIsNotNone(PinPWindow)

    def test_window_creation(self):
        """Test that the window can be created with default parameters."""
        from pinp import PinPWindow
        window = PinPWindow()
        self.assertIsNotNone(window)
        window.close()

    def test_window_creation_custom_params(self):
        """Test window creation with custom parameters."""
        from pinp import PinPWindow
        window = PinPWindow(
            window_size=(300, 300),
            magnification=3.0,
            update_interval_ms=20,
            offset=60,
            corner_radius=20,
            border_width=3,
            shadow_offset=10,
        )
        self.assertEqual(window.window_width, 300)
        self.assertEqual(window.window_height, 300)
        self.assertEqual(window.magnification, 3.0)
        self.assertEqual(window.offset, 60)
        self.assertEqual(window.corner_radius, 20)
        self.assertEqual(window.border_width, 3)
        self.assertEqual(window.shadow_offset, 10)
        window.close()

    def test_window_size(self):
        """Test that window size includes shadow offset."""
        from pinp import PinPWindow
        window = PinPWindow(
            window_size=(200, 200),
            shadow_offset=8,
        )
        expected_width = 200 + 8
        expected_height = 200 + 8
        self.assertEqual(window.width(), expected_width)
        self.assertEqual(window.height(), expected_height)
        window.close()

    def test_calculate_window_position_basic(self):
        """Test window position calculation near cursor."""
        from pinp import PinPWindow
        window = PinPWindow(
            window_size=(100, 100),
            offset=20,
            shadow_offset=5,
        )

        with patch.object(window, '_get_screen') as mock_screen:
            mock_screen_obj = Mock()
            mock_screen_obj.geometry.return_value = QRect(0, 0, 1920, 1080)
            mock_screen.return_value = mock_screen_obj

            cursor_pos = QPoint(500, 500)
            pos = window._calculate_window_position(cursor_pos)

            # Window should be offset from cursor
            self.assertEqual(pos.x(), 500 + 20)
            self.assertEqual(pos.y(), 500 + 20)

        window.close()

    def test_calculate_window_position_right_edge(self):
        """Test window position near right screen edge."""
        from pinp import PinPWindow
        window = PinPWindow(
            window_size=(100, 100),
            offset=20,
            shadow_offset=5,
        )

        with patch.object(window, '_get_screen') as mock_screen:
            mock_screen_obj = Mock()
            mock_screen_obj.geometry.return_value = QRect(0, 0, 1920, 1080)
            mock_screen.return_value = mock_screen_obj

            # Cursor near right edge
            cursor_pos = QPoint(1900, 500)
            pos = window._calculate_window_position(cursor_pos)

            # Window should be on left side of cursor
            total_width = 100 + 5  # window_width + shadow_offset
            self.assertEqual(pos.x(), 1900 - 20 - total_width)

        window.close()

    def test_timer_setup(self):
        """Test that the update timer is set up correctly."""
        from pinp import PinPWindow
        window = PinPWindow(update_interval_ms=15)
        self.assertTrue(window.timer.isActive())
        self.assertEqual(window.timer.interval(), 15)
        window.close()


if __name__ == '__main__':
    unittest.main()
