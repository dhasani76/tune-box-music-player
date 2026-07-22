import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pygame

from player import AudioEngine, MUSIC_END_EVENT
from playlist import PlaylistManager


class MusicPlayerGUI:
    """Tkinter Graphical User Interface for Music Player."""

    def __init__(self, root: tk.Tk, player: AudioEngine, playlist: PlaylistManager):
        self.root = root
        self.player = player
        self.playlist = playlist

        self.root.title("Tune Box")
        self.root.geometry("780x540")
        self.root.minsize(700, 480)

        self.is_seeking: bool = False  # Flag to prevent slider feedback loops during dragging

        # Load PNG Icons if available
        self.play_img = self._load_image("icons8-play.png", fallback="▶")
        self.pause_img = self._load_image("icons8-pause.png", fallback="⏸")
        self.stop_img = self._load_image("icons8-stop.png", fallback="⏹")

        # Catppuccin Mocha Inspired Dark Theme Palette
        self.colors = {
            "bg": "#1e1e2e",
            "card": "#181825",
            "panel": "#2a2a3c",
            "text": "#cdd6f4",
            "subtext": "#a6adc8",
            "accent": "#89b4fa",
            "accent_hover": "#b4befe",
            "active": "#a6e3a1",
            "btn_bg": "#313244",
            "btn_fg": "#cdd6f4",
            "border": "#45475a"
        }

        self.root.configure(bg=self.colors["bg"])

        # Build UI Structure
        self._create_menu()
        self._create_styles()
        self._create_layout()

        # Initial Volume Display
        self.volume_scale.set(self.player.get_volume_percent())

        # Start GUI Update Loop
        self.root.after(100, self._update_loop)

    def _load_image(self, path: str, fallback: str):
        if os.path.exists(path):
            try:
                img = tk.PhotoImage(file=path)
                if img.width() > 48 or img.height() > 48:
                    img = img.subsample(max(1, img.width() // 32), max(1, img.height() // 32))
                return img
            except Exception:
                return fallback
        return fallback

    def _create_menu(self):
        menubar = tk.Menu(self.root)

        # File Menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Open File(s)...", command=self.add_files)
        file_menu.add_command(label="Open Folder...", command=self.add_folder)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.destroy)
        menubar.add_cascade(label="File", menu=file_menu)

        # Controls Menu
        controls_menu = tk.Menu(menubar, tearoff=0)
        controls_menu.add_command(label="Play / Pause", command=self.toggle_play_pause)
        controls_menu.add_command(label="Stop", command=self.stop_music)
        controls_menu.add_command(label="Next Track", command=self.next_track)
        controls_menu.add_command(label="Previous Track", command=self.prev_track)
        menubar.add_cascade(label="Controls", menu=controls_menu)

        # Options Menu
        options_menu = tk.Menu(menubar, tearoff=0)
        options_menu.add_command(label="Toggle Shuffle", command=self.toggle_shuffle)
        options_menu.add_command(label="Cycle Repeat Mode", command=self.cycle_repeat)
        menubar.add_cascade(label="Options", menu=options_menu)

        # Help Menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="Help", menu=help_menu)

        self.root.config(menu=menubar)

    def _create_styles(self):
        style = ttk.Style()
        style.theme_use("default")
        style.configure(
            "TScale",
            background=self.colors["bg"],
            troughcolor=self.colors["border"],
            sliderlength=14
        )

    def _create_layout(self):
        # 2 Column Main Layout: Left = Player Controls, Right = Playlist
        self.root.columnconfigure(0, weight=3)
        self.root.columnconfigure(1, weight=2)
        self.root.rowconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=0)

        # --- Left Panel ---
        left_panel = tk.Frame(self.root, bg=self.colors["bg"], padx=20, pady=20)
        left_panel.grid(row=0, column=0, sticky="nsew")
        left_panel.columnconfigure(0, weight=1)

        # Track Info Card
        info_card = tk.Frame(left_panel, bg=self.colors["card"], padx=20, pady=25, highlightbackground=self.colors["border"], highlightthickness=1)
        info_card.grid(row=0, column=0, sticky="ew", pady=(0, 20))

        note_icon = tk.Label(info_card, text="🎵", font=("Segoe UI Emoji", 42), bg=self.colors["card"], fg=self.colors["accent"])
        note_icon.pack(pady=(0, 10))

        self.track_title_var = tk.StringVar(value="No Track Playing")
        track_title_label = tk.Label(
            info_card, textvariable=self.track_title_var,
            font=("Segoe UI", 13, "bold"), bg=self.colors["card"], fg=self.colors["text"],
            wraplength=360, justify="center"
        )
        track_title_label.pack(fill="x")

        self.track_status_var = tk.StringVar(value="Select or open songs to play")
        track_status_label = tk.Label(
            info_card, textvariable=self.track_status_var,
            font=("Segoe UI", 9), bg=self.colors["card"], fg=self.colors["subtext"]
        )
        track_status_label.pack(pady=(4, 0))

        # Progress / Seek Bar Frame
        progress_frame = tk.Frame(left_panel, bg=self.colors["bg"])
        progress_frame.grid(row=1, column=0, sticky="ew", pady=(0, 15))
        progress_frame.columnconfigure(1, weight=1)

        self.elapsed_time_var = tk.StringVar(value="00:00")
        elapsed_label = tk.Label(
            progress_frame, textvariable=self.elapsed_time_var,
            font=("Consolas", 10), bg=self.colors["bg"], fg=self.colors["subtext"]
        )
        elapsed_label.grid(row=0, column=0, padx=(0, 10))

        self.seek_slider = ttk.Scale(
            progress_frame, from_=0, to=100, orient="horizontal", command=self._on_seek_drag
        )
        self.seek_slider.grid(row=0, column=1, sticky="ew")
        self.seek_slider.bind("<ButtonRelease-1>", self._on_seek_release)

        self.total_time_var = tk.StringVar(value="00:00")
        total_label = tk.Label(
            progress_frame, textvariable=self.total_time_var,
            font=("Consolas", 10), bg=self.colors["bg"], fg=self.colors["subtext"]
        )
        total_label.grid(row=0, column=2, padx=(10, 0))

        # Playback Control Buttons Frame
        controls_frame = tk.Frame(left_panel, bg=self.colors["bg"])
        controls_frame.grid(row=2, column=0, pady=(0, 20))

        self.shuffle_btn = tk.Button(
            controls_frame, text="🔀", font=("Segoe UI Emoji", 12),
            bg=self.colors["btn_bg"], fg=self.colors["btn_fg"],
            activebackground=self.colors["border"], activeforeground=self.colors["text"],
            bd=0, padx=8, pady=6, cursor="hand2", command=self.toggle_shuffle
        )
        self.shuffle_btn.grid(row=0, column=0, padx=6)

        prev_btn = tk.Button(
            controls_frame, text="⏮", font=("Segoe UI Emoji", 14),
            bg=self.colors["btn_bg"], fg=self.colors["btn_fg"],
            activebackground=self.colors["border"], activeforeground=self.colors["text"],
            bd=0, padx=12, pady=6, cursor="hand2", command=self.prev_track
        )
        prev_btn.grid(row=0, column=1, padx=6)

        self.play_btn = tk.Button(
            controls_frame,
            image=self.play_img if isinstance(self.play_img, tk.PhotoImage) else None,
            text="" if isinstance(self.play_img, tk.PhotoImage) else "▶",
            font=("Segoe UI Emoji", 16, "bold"), bg=self.colors["accent"], fg=self.colors["card"],
            activebackground=self.colors["accent_hover"], bd=0, padx=14, pady=6, cursor="hand2",
            command=self.toggle_play_pause
        )
        self.play_btn.grid(row=0, column=2, padx=8)

        stop_btn = tk.Button(
            controls_frame,
            image=self.stop_img if isinstance(self.stop_img, tk.PhotoImage) else None,
            text="" if isinstance(self.stop_img, tk.PhotoImage) else "⏹",
            font=("Segoe UI Emoji", 14), bg=self.colors["btn_bg"], fg=self.colors["btn_fg"],
            activebackground=self.colors["border"], activeforeground=self.colors["text"],
            bd=0, padx=10, pady=6, cursor="hand2", command=self.stop_music
        )
        stop_btn.grid(row=0, column=3, padx=6)

        next_btn = tk.Button(
            controls_frame, text="⏭", font=("Segoe UI Emoji", 14),
            bg=self.colors["btn_bg"], fg=self.colors["btn_fg"],
            activebackground=self.colors["border"], activeforeground=self.colors["text"],
            bd=0, padx=12, pady=6, cursor="hand2", command=self.next_track
        )
        next_btn.grid(row=0, column=4, padx=6)

        self.repeat_btn = tk.Button(
            controls_frame, text="🔁", font=("Segoe UI Emoji", 12),
            bg=self.colors["btn_bg"], fg=self.colors["subtext"],
            activebackground=self.colors["border"], activeforeground=self.colors["text"],
            bd=0, padx=8, pady=6, cursor="hand2", command=self.cycle_repeat
        )
        self.repeat_btn.grid(row=0, column=5, padx=6)

        # Volume & Mute Bar
        volume_frame = tk.Frame(left_panel, bg=self.colors["bg"])
        volume_frame.grid(row=3, column=0, sticky="ew")
        volume_frame.columnconfigure(1, weight=1)

        self.mute_btn = tk.Button(
            volume_frame, text="🔊", font=("Segoe UI Emoji", 12),
            bg=self.colors["bg"], fg=self.colors["text"],
            activebackground=self.colors["bg"], activeforeground=self.colors["accent"],
            bd=0, cursor="hand2", command=self.toggle_mute
        )
        self.mute_btn.grid(row=0, column=0, padx=(0, 8))

        self.volume_scale = ttk.Scale(
            volume_frame, from_=0, to=100, orient="horizontal", command=self.set_volume
        )
        self.volume_scale.grid(row=0, column=1, sticky="ew")

        self.volume_label_var = tk.StringVar(value="70%")
        volume_label = tk.Label(
            volume_frame, textvariable=self.volume_label_var,
            font=("Segoe UI", 9, "bold"), bg=self.colors["bg"], fg=self.colors["subtext"], width=5
        )
        volume_label.grid(row=0, column=2, padx=(8, 0))

        # --- Right Panel (Playlist) ---
        right_panel = tk.Frame(self.root, bg=self.colors["panel"], padx=15, pady=15)
        right_panel.grid(row=0, column=1, sticky="nsew")
        right_panel.rowconfigure(1, weight=1)
        right_panel.columnconfigure(0, weight=1)

        # Playlist Header
        playlist_header = tk.Frame(right_panel, bg=self.colors["panel"])
        playlist_header.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        playlist_title = tk.Label(
            playlist_header, text="Playlist", font=("Segoe UI", 12, "bold"),
            bg=self.colors["panel"], fg=self.colors["text"]
        )
        playlist_title.pack(side="left")

        tb_frame = tk.Frame(playlist_header, bg=self.colors["panel"])
        tb_frame.pack(side="right")

        add_file_btn = tk.Button(
            tb_frame, text="➕ File", font=("Segoe UI", 9),
            bg=self.colors["btn_bg"], fg=self.colors["btn_fg"],
            bd=0, padx=6, pady=2, cursor="hand2", command=self.add_files
        )
        add_file_btn.pack(side="left", padx=2)

        add_folder_btn = tk.Button(
            tb_frame, text="📁 Folder", font=("Segoe UI", 9),
            bg=self.colors["btn_bg"], fg=self.colors["btn_fg"],
            bd=0, padx=6, pady=2, cursor="hand2", command=self.add_folder
        )
        add_folder_btn.pack(side="left", padx=2)

        del_btn = tk.Button(
            tb_frame, text="🗑", font=("Segoe UI Emoji", 9),
            bg=self.colors["btn_bg"], fg=self.colors["btn_fg"],
            bd=0, padx=6, pady=2, cursor="hand2", command=self.remove_selected
        )
        del_btn.pack(side="left", padx=2)

        # Playlist Listbox & Scrollbar
        list_container = tk.Frame(right_panel, bg=self.colors["panel"])
        list_container.grid(row=1, column=0, sticky="nsew")
        list_container.rowconfigure(0, weight=1)
        list_container.columnconfigure(0, weight=1)

        self.playlist_box = tk.Listbox(
            list_container, bg=self.colors["card"], fg=self.colors["text"],
            selectbackground=self.colors["accent"], selectforeground=self.colors["card"],
            activestyle="none", bd=0, highlightthickness=1, highlightbackground=self.colors["border"],
            font=("Segoe UI", 10)
        )
        self.playlist_box.grid(row=0, column=0, sticky="nsew")
        self.playlist_box.bind("<Double-Button-1>", self._on_playlist_double_click)

        scrollbar = ttk.Scrollbar(list_container, orient="vertical", command=self.playlist_box.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.playlist_box.config(yscrollcommand=scrollbar.set)

        # Bottom Status Bar
        self.statusbar = tk.Label(
            self.root, text=" Welcome to Tune Box", font=("Segoe UI", 9),
            bg=self.colors["card"], fg=self.colors["subtext"], anchor="w",
            padx=10, pady=4, bd=1, relief="solid"
        )
        self.statusbar.grid(row=1, column=0, columnspan=2, sticky="ew")

    # --- Playback Callbacks ---

    def play_track(self, index: int):
        if not (0 <= index < len(self.playlist.tracks)):
            return

        track_path = self.playlist.tracks[index]
        if not os.path.exists(track_path):
            messagebox.showerror("Error Loading File", f"The file could not be found:\n{track_path}")
            return

        success = self.player.load_and_play(track_path)
        if not success:
            messagebox.showerror("Playback Error", f"Unable to play file:\n{track_path}")
            return

        self.playlist.current_index = index

        # Update Listbox Selection
        self.playlist_box.selection_clear(0, tk.END)
        self.playlist_box.selection_set(index)
        self.playlist_box.activate(index)
        self.playlist_box.see(index)

        # Update UI Labels
        track_name = os.path.basename(track_path)
        self.track_title_var.set(track_name)
        self.track_status_var.set(f"Playing track {index + 1} of {len(self.playlist.tracks)}")
        self.total_time_var.set(self.player.format_time(self.player.track_length))

        self._set_play_button_visual(playing=True)
        self.statusbar.config(text=f" Playing: {track_name}")

    def toggle_play_pause(self):
        if not self.playlist.tracks:
            self.add_files()
            if not self.playlist.tracks:
                return

        if self.player.is_stopped:
            sel = self.playlist_box.curselection()
            start_idx = sel[0] if sel else 0
            self.play_track(start_idx)

        elif self.player.is_paused:
            self.player.resume()
            self.track_status_var.set(f"Playing track {self.playlist.current_index + 1} of {len(self.playlist.tracks)}")
            self._set_play_button_visual(playing=True)
            self.statusbar.config(text=f" Playing: {os.path.basename(self.playlist.get_current_track())}")

        else:
            self.player.pause()
            self.track_status_var.set("Paused")
            self._set_play_button_visual(playing=False)
            self.statusbar.config(text=" Paused")

    def stop_music(self):
        self.player.stop()
        self.seek_slider.set(0)
        self.elapsed_time_var.set("00:00")
        self.track_status_var.set("Stopped")
        self._set_play_button_visual(playing=False)
        self.statusbar.config(text=" Stopped")

    def next_track(self):
        next_idx = self.playlist.get_next_index()
        if next_idx is not None:
            self.play_track(next_idx)
        else:
            self.stop_music()

    def prev_track(self):
        elapsed = self.player.get_elapsed_seconds()
        prev_idx = self.playlist.get_prev_index(elapsed)
        if prev_idx is not None:
            self.play_track(prev_idx)

    # --- Seek Drag/Release & Updates ---

    def _on_seek_drag(self, val):
        self.is_seeking = True
        if self.player.track_length > 0:
            target_sec = (float(val) / 100.0) * self.player.track_length
            self.elapsed_time_var.set(self.player.format_time(target_sec))

    def _on_seek_release(self, event):
        if self.player.track_length > 0 and self.playlist.current_index != -1:
            val = self.seek_slider.get()
            target_sec = (float(val) / 100.0) * self.player.track_length
            self.player.seek(target_sec)
        self.is_seeking = False

    def _update_loop(self):
        # Poll Pygame Events
        for event in pygame.event.get():
            if event.type == MUSIC_END_EVENT:
                if not self.player.is_stopped and not self.player.is_paused:
                    self.next_track()

        # Update Seek Slider & Elapsed Time
        if not self.player.is_stopped and not self.player.is_paused and self.player.track_length > 0:
            elapsed = self.player.get_elapsed_seconds()
            if elapsed >= self.player.track_length:
                elapsed = self.player.track_length

            if not self.is_seeking:
                pct = (elapsed / self.player.track_length) * 100.0
                self.seek_slider.set(pct)
                self.elapsed_time_var.set(self.player.format_time(elapsed))

        self.root.after(100, self._update_loop)

    # --- Playlist Operations ---

    def add_files(self):
        files = filedialog.askopenfilenames(
            title="Select Audio Files",
            filetypes=[("Audio Files", "*.mp3 *.wav *.ogg"), ("MP3 Files", "*.mp3"), ("All Files", "*.*")]
        )
        if files:
            added = self.playlist.add_files(files)
            self._refresh_playlist_box()
            self.statusbar.config(text=f" Added {len(added)} track(s) to playlist. Total: {len(self.playlist.tracks)}")

    def add_folder(self):
        folder = filedialog.askdirectory(title="Select Folder with Audio Files")
        if folder:
            added = self.playlist.add_folder(folder)
            self._refresh_playlist_box()
            self.statusbar.config(text=f" Added {len(added)} track(s) from folder. Total: {len(self.playlist.tracks)}")

    def remove_selected(self):
        sel = self.playlist_box.curselection()
        if not sel:
            return

        idx = sel[0]
        was_playing = self.playlist.remove_track(idx)
        self._refresh_playlist_box()

        if was_playing:
            self.stop_music()
            self.track_title_var.set("No Track Playing")

    def _refresh_playlist_box(self):
        self.playlist_box.delete(0, tk.END)
        for i, path in enumerate(self.playlist.tracks):
            self.playlist_box.insert(tk.END, f" {i + 1}. {os.path.basename(path)}")
        if 0 <= self.playlist.current_index < len(self.playlist.tracks):
            self.playlist_box.selection_set(self.playlist.current_index)

    def _on_playlist_double_click(self, event):
        sel = self.playlist_box.curselection()
        if sel:
            self.play_track(sel[0])

    # --- Volume & Options ---

    def set_volume(self, val):
        self.player.set_volume(val)
        pct = self.player.get_volume_percent()
        self.volume_label_var.set(f"{pct}%")
        if pct > 0:
            self.mute_btn.config(text="🔊")

    def toggle_mute(self):
        muted = self.player.toggle_mute()
        if muted:
            self.mute_btn.config(text="🔇")
            self.volume_scale.set(0)
            self.volume_label_var.set("0%")
        else:
            self.mute_btn.config(text="🔊")
            pct = self.player.get_volume_percent()
            self.volume_scale.set(pct)
            self.volume_label_var.set(f"{pct}%")

    def toggle_shuffle(self):
        is_shuffle = self.playlist.toggle_shuffle()
        if is_shuffle:
            self.shuffle_btn.config(fg=self.colors["accent"], bg=self.colors["border"])
            self.statusbar.config(text=" Shuffle Enabled")
        else:
            self.shuffle_btn.config(fg=self.colors["btn_fg"], bg=self.colors["btn_bg"])
            self.statusbar.config(text=" Shuffle Disabled")

    def cycle_repeat(self):
        mode = self.playlist.cycle_repeat()
        if mode == "Playlist":
            self.repeat_btn.config(text="🔁", fg=self.colors["accent"])
            self.statusbar.config(text=" Repeat Mode: Entire Playlist")
        elif mode == "Track":
            self.repeat_btn.config(text="🔂", fg=self.colors["accent"])
            self.statusbar.config(text=" Repeat Mode: Current Track")
        else:
            self.repeat_btn.config(text="🔁", fg=self.colors["subtext"])
            self.statusbar.config(text=" Repeat Mode: Off")

    def _set_play_button_visual(self, playing: bool):
        if playing and not self.player.is_paused:
            if isinstance(self.pause_img, tk.PhotoImage):
                self.play_btn.config(image=self.pause_img, text="")
            else:
                self.play_btn.config(text="⏸", image="")
        else:
            if isinstance(self.play_img, tk.PhotoImage):
                self.play_btn.config(image=self.play_img, text="")
            else:
                self.play_btn.config(text="▶", image="")

    def show_about(self):
        messagebox.showinfo(
            "About Music Player",
            "Tune Box v2.0\n\n"
            "Features:\n"
            "• Modern Interface\n"
            "• Playlist & Folder Loading\n"
            "• Audio Seek Progress Bar\n"
            "• Auto-Next Track & Seek Controls\n"
            "• Shuffle & Repeat Modes\n\n"
            "Built with Python, Tkinter & Pygame."
        )
