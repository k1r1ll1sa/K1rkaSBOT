import subprocess
import yt_dlp
import threading
from queue import Queue, Empty
import time
import os


class AudioPlayer:
    def __init__(self, initial_volume):
        self.process = None
        self.is_paused = False
        self.song_queue = Queue()
        self.current_song = None
        self.volume = initial_volume
        self.ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
        }
        self.stop_event = threading.Event()
        self.player_thread = threading.Thread(target=self.run_player, daemon=True)
        self.player_thread.start()

    def get_song_info(self, url):
        with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
            try:
                info = ydl.extract_info(url, download=False)
                return {
                    'title': info.get('title', 'Неизвестный трек'),
                    'duration': info.get('duration', 0),
                    'view_count': info.get('view_count', 0),
                    'url': url
                }
            except Exception as e:
                print(f"Ошибка получения информации: {e}")
                return None

    def add_to_queue(self, url):
        song = self.get_song_info(url)
        if not song:
            return False

        if song['duration'] > 300 or song['view_count'] < 50000:
            return False

        self.song_queue.put(song)
        return True

    def play_song(self, song):
        if self.process:
            self.stop_current()

        self.current_song = song
        ipc_pipe = r'\\.\pipe\mpv_pipe'
        self.process = subprocess.Popen(
            [
                "C:\\mpv\\mpv.exe",
                "--no-video",
                "--no-terminal",
                f"--input-ipc-server={ipc_pipe}",
                f"--volume={self.volume}",
                song['url']
            ],
            stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW)

    def set_volume(self, volume):
        self.volume = max(0, min(100, volume))
        if self.process and self.process.poll() is None:
            try:
                with open(r'\\.\pipe\mpv_pipe', 'w') as pipe:
                    pipe.write(f'set volume {self.volume}\n')
            except:
                pass

    def skip(self):
        if self.process:
            self.stop_current()
            time.sleep(0.2)
            if not self.song_queue.empty():
                next_song = self.song_queue.get()
                self.play_song(next_song)
            else:
                self.current_song = None

    def pause(self):
        if self.process and self.process.poll() is None and not self.is_paused:
            try:
                with open(r'\\.\pipe\mpv_pipe', 'w') as pipe:
                    pipe.write('cycle pause\n')
                self.is_paused = True
                return True
            except Exception as e:
                print(f"Ошибка при паузе: {e}")
        return False

    def resume(self):
        if self.process and self.process.poll() is None and self.is_paused:
            try:
                with open(r'\\.\pipe\mpv_pipe', 'w') as pipe:
                    pipe.write('cycle pause\n')
                self.is_paused = False
                return True
            except Exception as e:
                print(f"Ошибка при возобновлении: {e}")
        return False

    def stop_current(self):
        if self.process:
            try:
                with open(r'\\.\pipe\mpv_pipe', 'w') as pipe:
                    pipe.write('stop\n')
            except:
                self.process.terminate()
            self.process.wait()
            self.process = None

    def run_player(self):
        while not self.stop_event.is_set():
            try:
                song = self.song_queue.get(timeout=10)
                self.play_song(song)

                while self.process and self.process.poll() is None:
                    if self.stop_event.is_set():
                        self.stop_current()
                        return
                    time.sleep(0.5)
                self.current_song = None
            except Empty:
                continue
            except KeyboardInterrupt:
                break

    def stop(self):
        self.stop_event.set()
        self.stop_current()
        self.player_thread.join()

    def clear_queue(self):
        while not self.song_queue.empty():
            try:
                self.song_queue.get_nowait()
            except:
                continue