import tkinter as tk
from player import AudioEngine
from playlist import PlaylistManager
from ui import MusicPlayerGUI


def main():
    root = tk.Tk()
    playlist = PlaylistManager()
    player = AudioEngine()
    app = MusicPlayerGUI(root, player, playlist)
    root.mainloop()


if __name__ == "__main__":
    main()