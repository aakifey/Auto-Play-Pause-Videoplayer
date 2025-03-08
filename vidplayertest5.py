import tkinter as tk
from tkinter import filedialog, ttk
import vlc
import cv2
import time
import threading
import numpy as np
from collections import deque

class FaceDetectionVideoPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("Face Detection Video Player")
        self.root.geometry("800x600")
        self.root.config(bg="black")

        # VLC Player Instance
        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()

        # OpenCV Cascades for Face and Eye Detection
        self.face_cascade = cv2.CascadeClassifier('Cascades/haarcascade_frontalface_default.xml')
        self.eye_cascade = cv2.CascadeClassifier('Cascades/haarcascade_eye_tree_eyeglasses.xml')

        # Video Display Frame
        self.video_frame = tk.Frame(self.root, bg="black", width=800, height=500)
        self.video_frame.pack_propagate(0)
        self.video_frame.pack(fill=tk.BOTH, expand=True)

        # Bottom Control Bar
        self.bottom_bar = tk.Frame(self.root, bg="gray", height=100)
        self.bottom_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Play/Pause Button
        self.play_button = tk.Button(self.bottom_bar, text="Play", command=self.toggle_play)
        self.play_button.grid(row=0, column=0, padx=5)

        # Stop Button
        self.stop_button = tk.Button(self.bottom_bar, text="Stop", command=self.stop_video)
        self.stop_button.grid(row=0, column=1, padx=5)

        # Seek Bar
        self.seek_var = tk.DoubleVar()
        self.seek_bar = ttk.Scale(
            self.bottom_bar, from_=0, to=100, orient="horizontal", variable=self.seek_var, command=self.seek_video
        )
        self.seek_bar.grid(row=0, column=2, columnspan=5, padx=10, sticky="ew")

        # Time Display
        self.time_label = tk.Label(self.bottom_bar, text="00:00 / 00:00", bg="gray", fg="white")
        self.time_label.grid(row=0, column=7, padx=5)

        # Volume Control
        self.volume_var = tk.DoubleVar(value=50)
        self.volume_slider = ttk.Scale(
            self.bottom_bar, from_=0, to=100, orient="horizontal", variable=self.volume_var, command=self.set_volume
        )
        self.volume_slider.grid(row=0, column=8, padx=5)

        # Playback Speed Dropdown
        self.speed_var = tk.StringVar(value="1x")
        self.speed_menu = ttk.Combobox(
            self.bottom_bar, textvariable=self.speed_var, values=["0.5x", "1x", "1.5x", "2x"], state="readonly"
        )
        self.speed_menu.grid(row=0, column=9, padx=5)
        self.speed_menu.bind("<<ComboboxSelected>>", self.change_speed)

        # Fullscreen Button
        self.fullscreen_button = tk.Button(self.bottom_bar, text="Fullscreen", command=self.toggle_fullscreen)
        self.fullscreen_button.grid(row=0, column=10, padx=5)

        # File Open Button
        self.open_button = tk.Button(self.bottom_bar, text="Open Video", command=self.open_video)
        self.open_button.grid(row=0, column=11, padx=5)

        # Detection Parameters
        self.cap = cv2.VideoCapture(0)
        self.cap.set(3, 640)  # Width
        self.cap.set(4, 480)  # Height
        self.last_eye_detection_time = time.time()
        self.eye_detection_timeout = 0.5  # Timeout in seconds
        self.face_detection_paused_until = 0

        # Detection Queue for smoothing
        self.detection_queue = deque(maxlen=5)

        # Flags and Timers
        self.running = True
        self.is_fullscreen = False

        # Key bindings
        self.root.bind("<space>", lambda event: self.man_toggle_play())
        self.root.bind("<s>", lambda event: self.stop_video())
        self.root.bind("<o>", lambda event: self.open_video())
        self.root.bind("<f>", lambda event: self.toggle_fullscreen())
        self.root.bind("<Up>", lambda event: self.adjust_volume(5))
        self.root.bind("<Down>", lambda event: self.adjust_volume(-5))
        self.root.bind("<Right>", lambda event: self.seek_adjust(5))
        self.root.bind("<Left>", lambda event: self.seek_adjust(-5))
        self.root.bind("<plus>", lambda event: self.change_speed_hotkey(1))
        self.root.bind("<minus>", lambda event: self.change_speed_hotkey(-1))
        self.root.bind("<q>", lambda event: self.on_close())

        # Start Threads
        threading.Thread(target=self.detect_faces_and_eyes, daemon=True).start()
        threading.Thread(target=self.update_seek_bar, daemon=True).start()

    def adjust_gamma(self, image, gamma=1.0):
        invGamma = 1.0 / gamma
        table = np.array([((i / 255.0) ** invGamma) * 255 for i in np.arange(0, 256)]).astype("uint8")
        return cv2.LUT(image, table)

    def open_video(self):
        filepath = filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4;*.avi;*.mov;*.mkv")])
        if filepath:
            media = self.instance.media_new(filepath)
            self.player.set_media(media)
            self.player.set_hwnd(self.video_frame.winfo_id())
            self.play_button.config(text="Play")
    
    def man_toggle_play(self):
        if self.player.is_playing():
            self.player.pause()
            self.play_button.config(text="Play")
            self.face_detection_paused_until = time.time() + 60
        else:
            self.player.play()
            self.play_button.config(text="Pause")
            self.face_detection_paused_until = 0

    def toggle_play(self):
        if self.player.is_playing():
            self.player.pause()
            self.play_button.config(text="Play")
        else:
            self.player.play()
            self.play_button.config(text="Pause")

    def stop_video(self):
        self.player.stop()
        self.play_button.config(text="Play")
        self.seek_var.set(0)
        self.time_label.config(text="00:00 / 00:00")

    def seek_video(self, value):
        total_time = self.player.get_length() / 1000
        new_time = float(value) / 100 * total_time
        self.player.set_time(int(new_time * 1000))

    def set_volume(self, value):
        self.player.audio_set_volume(int(float(value)))

    def adjust_volume(self, change):
        new_volume = max(0, min(100, self.player.audio_get_volume() + change))
        self.player.audio_set_volume(new_volume)
        self.volume_var.set(new_volume)

    def seek_adjust(self, change):
        current_time = self.player.get_time() / 1000
        self.player.set_time(int((current_time + change) * 1000))

    def change_speed(self, event):
        speed = float(self.speed_var.get().replace("x", ""))
        self.player.set_rate(speed)

    def change_speed_hotkey(self, change):
        speeds = [0.5, 1.0, 1.5, 2.0]
        current_speed = self.player.get_rate()
        if change == 1 and current_speed < 2.0:
            new_speed = speeds[speeds.index(current_speed) + 1]
        elif change == -1 and current_speed > 0.5:
            new_speed = speeds[speeds.index(current_speed) - 1]
        else:
            return
        self.player.set_rate(new_speed)
        self.speed_var.set(f"{new_speed}x")

    def toggle_fullscreen(self):
        self.root.attributes("-fullscreen", not self.root.attributes("-fullscreen"))
    
    def detect_faces_and_eyes(self):
        while self.running:
            if time.time() < self.face_detection_paused_until:
                time.sleep(1)
                continue
            ret, img = self.cap.read()
            if not ret:
                continue

            # Flip the frame horizontally
            img = cv2.flip(img, 1)

            # Apply gamma correction and adaptive histogram equalization
            adjusted = self.adjust_gamma(img, gamma=1.5)
            gray = cv2.cvtColor(adjusted, cv2.COLOR_BGR2GRAY)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            gray = clahe.apply(gray)

            faces = self.face_cascade.detectMultiScale(
                gray, scaleFactor=1.2, minNeighbors=5, minSize=(50, 50)
            )

            # Sort faces by size and focus on the largest one
            faces = sorted(faces, key=lambda x: x[2] * x[3], reverse=True)
            face_detected = False

            if len(faces) > 0:
                (x, y, w, h) = faces[0]
                roi_gray = gray[y:y + h, x:x + w]

                # Detect eyes within the face region
                eyes = self.eye_cascade.detectMultiScale(
                    roi_gray, scaleFactor=1.1, minNeighbors=10, minSize=(15, 15)
                )

                if len(eyes) > 0:
                    self.last_eye_detection_time = time.time()
                    face_detected = True

            if time.time() - self.last_eye_detection_time <= self.eye_detection_timeout:
                face_detected = True

            self.detection_queue.append(face_detected)

            if sum(self.detection_queue) / len(self.detection_queue) > 0.5:
                if not self.player.is_playing():
                    self.player.play()
                    self.play_button.config(text="Pause")
            else:
                if self.player.is_playing():
                    self.player.pause()
                    self.play_button.config(text="Play")

            time.sleep(0.1)
        
    def update_seek_bar(self):
        while True:
            if self.player.is_playing():
                total_time = self.player.get_length() / 1000
                current_time = self.player.get_time() / 1000
                if total_time > 0:
                    self.seek_var.set((current_time / total_time) * 100)
                self.time_label.config(text=f"{int(current_time // 60)}:{int(current_time % 60):02d} / {int(total_time // 60)}:{int(total_time % 60):02d}")
            time.sleep(0.5)

    def on_close(self):
        self.running = False
        self.cap.release()
        self.player.stop()
        self.root.destroy()

# Run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = FaceDetectionVideoPlayer(root)
    root.mainloop()
