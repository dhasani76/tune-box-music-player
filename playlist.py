import os
import random


class PlaylistManager:
    """Manages the list of audio tracks, track selection index, file imports, and repeat/shuffle modes."""

    def __init__(self):
        self.tracks: list[str] = []
        self.current_index: int = -1
        self.repeat_mode: str = "Off"  # "Off", "Track", "Playlist"
        self.shuffle_mode: bool = False

    def add_files(self, paths: tuple[str, ...] | list[str]) -> list[str]:
        added = []
        for p in paths:
            norm_path = os.path.normpath(p)
            if norm_path not in self.tracks:
                self.tracks.append(norm_path)
                added.append(norm_path)
        return added

    def add_folder(self, folder_path: str) -> list[str]:
        added = []
        if not os.path.exists(folder_path):
            return added

        for root_dir, _, files in os.walk(folder_path):
            for file in sorted(files):
                if file.lower().endswith((".mp3", ".wav", ".ogg")):
                    full_path = os.path.normpath(os.path.join(root_dir, file))
                    if full_path not in self.tracks:
                        self.tracks.append(full_path)
                        added.append(full_path)
        return added

    def remove_track(self, index: int) -> bool:
        """Removes track at index. Returns True if current playing track was removed."""
        if 0 <= index < len(self.tracks):
            del self.tracks[index]
            if index == self.current_index:
                self.current_index = -1
                return True
            elif index < self.current_index:
                self.current_index -= 1
        return False

    def clear(self):
        self.tracks.clear()
        self.current_index = -1

    def get_current_track(self) -> str | None:
        if 0 <= self.current_index < len(self.tracks):
            return self.tracks[self.current_index]
        return None

    def get_next_index(self) -> int | None:
        if not self.tracks:
            return None

        if self.repeat_mode == "Track" and self.current_index != -1:
            return self.current_index

        if self.shuffle_mode and len(self.tracks) > 1:
            indices = [i for i in range(len(self.tracks)) if i != self.current_index]
            return random.choice(indices)

        next_idx = self.current_index + 1
        if next_idx >= len(self.tracks):
            if self.repeat_mode == "Playlist":
                return 0
            return None

        return next_idx

    def get_prev_index(self, elapsed_sec: float) -> int | None:
        if not self.tracks:
            return None

        # If played > 3 seconds, restart current track
        if elapsed_sec > 3.0 and self.current_index != -1:
            return self.current_index

        if self.shuffle_mode and len(self.tracks) > 1:
            indices = [i for i in range(len(self.tracks)) if i != self.current_index]
            return random.choice(indices)

        prev_idx = self.current_index - 1
        if prev_idx < 0:
            return len(self.tracks) - 1

        return prev_idx

    def cycle_repeat(self) -> str:
        if self.repeat_mode == "Off":
            self.repeat_mode = "Playlist"
        elif self.repeat_mode == "Playlist":
            self.repeat_mode = "Track"
        else:
            self.repeat_mode = "Off"
        return self.repeat_mode

    def toggle_shuffle(self) -> bool:
        self.shuffle_mode = not self.shuffle_mode
        return self.shuffle_mode
