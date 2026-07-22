import time
import pygame

# Pygame end-of-track event
MUSIC_END_EVENT = pygame.USEREVENT + 1


class AudioEngine:
    """Manages audio loading, playback state, seeking, duration calculation, and volume control."""

    def __init__(self):
        pygame.mixer.init()
        pygame.mixer.music.set_endevent(MUSIC_END_EVENT)

        self.is_paused: bool = False
        self.is_stopped: bool = True
        self.is_muted: bool = False
        self.pre_mute_volume: float = 0.7
        self.track_length: float = 0.0  # Total duration in seconds
        self.playback_offset: float = 0.0  # Accumulated playback seconds
        self.play_start_time: float = 0.0  # Timestamp when playback/resume started

        # Set default initial volume
        pygame.mixer.music.set_volume(0.7)

    def load_and_play(self, file_path: str) -> bool:
        """Loads and plays an audio file. Returns True if successful."""
        try:
            sound = pygame.mixer.Sound(file_path)
            self.track_length = sound.get_length()
        except Exception:
            self.track_length = 0.0

        try:
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()
            self.is_paused = False
            self.is_stopped = False
            self.playback_offset = 0.0
            self.play_start_time = time.time()
            return True
        except Exception:
            return False

    def pause(self):
        if not self.is_stopped and not self.is_paused:
            pygame.mixer.music.pause()
            self.is_paused = True
            self.playback_offset += (time.time() - self.play_start_time)

    def resume(self):
        if not self.is_stopped and self.is_paused:
            pygame.mixer.music.unpause()
            self.is_paused = False
            self.play_start_time = time.time()

    def stop(self):
        pygame.mixer.music.stop()
        self.is_stopped = True
        self.is_paused = False
        self.playback_offset = 0.0

    def seek(self, target_seconds: float):
        if self.is_stopped or self.track_length <= 0:
            return

        try:
            pygame.mixer.music.play(start=target_seconds)
            self.playback_offset = target_seconds
            self.play_start_time = time.time()
            if self.is_paused:
                pygame.mixer.music.pause()
        except Exception:
            pass

    def get_elapsed_seconds(self) -> float:
        if self.is_stopped or self.is_paused:
            return self.playback_offset
        return self.playback_offset + (time.time() - self.play_start_time)

    def set_volume(self, val_0_to_100: float):
        vol = max(0.0, min(1.0, float(val_0_to_100) / 100.0))
        pygame.mixer.music.set_volume(vol)
        if vol > 0:
            self.is_muted = False

    def get_volume_percent(self) -> int:
        return int(round(pygame.mixer.music.get_volume() * 100))

    def toggle_mute(self) -> bool:
        if self.is_muted:
            self.is_muted = False
            pygame.mixer.music.set_volume(self.pre_mute_volume)
        else:
            self.is_muted = True
            self.pre_mute_volume = pygame.mixer.music.get_volume()
            pygame.mixer.music.set_volume(0.0)
        return self.is_muted

    @staticmethod
    def format_time(seconds: float) -> str:
        s = max(0.0, seconds)
        mins = int(s // 60)
        secs = int(s % 60)
        return f"{mins:02d}:{secs:02d}"
