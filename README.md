# 🎵 Music Player

A lightweight desktop audio player application built with **Python**, **Tkinter**, and **Pygame Mixer**. 

---

## ✨ Features

- **Audio Playback Controls**: Play, pause, resume, and stop audio tracks.
- **Track Scrubbing & Seeking**: Real-time progress bar with interactive seek capabilities.
- **Volume & Mute**: Volume control slider with a one-click mute/unmute toggle.
- **Playlist Management**:
  - Add individual audio files or entire directories/folders recursively.
  - Remove individual tracks or clear the playlist.
  - Visual track selection and current track highlighting.
- **Playback Modes**:
  - **Repeat Modes**: Cycle through *Off*, *Repeat Playlist*, and *Repeat Track*.
  - **Shuffle Mode**: Toggle randomized playback order.
- **Supported Formats**: `.mp3`, `.wav`, and `.ogg`.

---

## 📁 Project Structure

```text
Music-Player/
│
├── main.py          # Main entry point - initializes components and runs GUI loop
├── player.py        # AudioEngine module using pygame.mixer for audio operations
├── playlist.py      # PlaylistManager handling track queues, repeat, & shuffle logic
├── ui.py            # MusicPlayerGUI building the user interface using Tkinter
│
├── .gitignore       # Git ignore configuration
└── README.md        # Project documentation
```

---

## 🛠️ Prerequisites

- **Python 3.8+**
- **Pygame** library

> Note: **Tkinter** is included with standard Python installations on Windows and macOS. Linux users may need to install `python3-tk` if not already present.

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/Music-Player.git
cd Music-Player
```

### 2. Set Up a Virtual Environment (Optional but Recommended)

#### Windows (PowerShell)
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

#### macOS / Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install pygame
```

### 4. Run the Application

```bash
python main.py
```

---

## 🎮 Usage

1. **Add Music**: Click **Add Files** or **Add Folder** to load `.mp3`, `.wav`, or `.ogg` files into your playlist.
2. **Play Track**: Double-click any track in the playlist listbox or select it and press the **Play** button.
3. **Control Playback**:
   - Use **Pause** / **Play** / **Stop** buttons to control playback state.
   - Drag or click the track progress slider to jump to specific points in the song.
   - Adjust the volume slider or click the speaker icon to mute/unmute.
4. **Repeat & Shuffle**:
   - Click **Repeat** to toggle between `Off` ➔ `Playlist` ➔ `Track`.
   - Click **Shuffle** to toggle randomized playback `ON` / `OFF`.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
