# PinP

A Python + PyQt5 + X11 screen capture application that creates a "follow-along small window" (追従付き小窓) cursor magnifier.

## Features

- ✔ Small window that always moves near the cursor position
- ✔ Displays magnified view of the area around the cursor
- ✔ Transparent frame with shadow and rounded corners
- ✔ Lightweight (100fps+ capable with 10ms update interval)
- ✔ Crosshair indicator showing cursor position

## Requirements

- Python 3.6+
- PyQt5
- X11 display (Linux) or compatible display server

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python3 pinp.py
```

Press `Escape` to exit the application.

## Configuration

The `PinPWindow` class accepts the following parameters:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `window_size` | `(200, 200)` | Size of the magnifier window (width, height) |
| `magnification` | `2.0` | Zoom factor for the magnified view |
| `update_interval_ms` | `10` | Update interval in ms (lower = smoother, ~100fps at 10ms) |
| `offset` | `50` | Distance from cursor to window |
| `corner_radius` | `15` | Radius for rounded corners |
| `border_width` | `2` | Width of the window border |
| `shadow_offset` | `5` | Offset for drop shadow effect |

## Example

```python
from pinp import PinPWindow
from PyQt5.QtWidgets import QApplication
import sys

app = QApplication(sys.argv)

window = PinPWindow(
    window_size=(300, 300),
    magnification=3.0,
    update_interval_ms=16,  # ~60fps
    offset=40,
)
window.show()

sys.exit(app.exec())
```

## License

MIT