# Auto Play/Pause Videoplayer

## Overview
A smart video player built with **Tkinter, VLC, and OpenCV** that **automatically pauses and plays** based on **face detection**. It also features **seek bar, volume control, speed adjustment, fullscreen mode, and keyboard shortcuts** for a modern playback experience.  


## Features  
* **Auto Play/Pause** – Uses face detection to pause when you're away  
* **Filters Background Faces** – Only tracks the closest user  
* **Gamma Correction & Adaptive Histogram** – Improves detection in different lighting  
* **Keyboard Shortcuts** – Control playback without a mouse  
* **Modern UI** – Includes seek bar, volume & speed control, fullscreen mode  


## Keyboard Shortcuts  
| Shortcut | Action |
|----------|--------|
| `Space` | Play/Pause |
| `S` | Stop |
| `O` | Open Video |
| `F` | Toggle Fullscreen |
| `↑ / ↓` | Increase/Decrease Volume |
| `← / →` | Seek Backward/Forward |
| `+ / -` | Increase/Decrease Playback Speed |
| `Q` | Quit |


## Technologies Used  
- **Python** (Tkinter for GUI)  
- **OpenCV** (Face & Eye Detection)  
- **VLC** (Video Playback)  
- **NumPy** (Image Processing)  


## How to Run  
1. **Install Dependencies:**  
   ```sh
   pip install opencv-python numpy python-vlc
   ```
2. **Run the Script:**  
   ```sh
   python vidplayer.py
   ```
3. **Open a Video & Enjoy AI-Powered Playback!**


## Future Improvements  
- Add **gesture-based controls**  
- Implement **face recognition for personalized settings**  
- Improve UI design with **custom themes**  


