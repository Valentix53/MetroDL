# MetroDL
Download your [Metrolist](https://github.com/MetrolistGroup/Metrolist) playlists with ease.

## 📜 About the Project
MetroDL is a command-line tool designed to solve the pain point of manually tracking and downloading playlists created in Metrolist. It takes your exported `.csv` file and downloads music with related cover image and stores them in a folder with the playlist name, saving you time and hassle.

---

## 🚀 Installation
**0. Prerequisites**
Before running the script, ensure you have the following software installed on your system:

- **Python >= 3.11:** The environment for the script
    * **yt-dlp:** Effective downloader, get it form the official repository https://github.com/yt-dlp/yt-dlp
    * **Pillow:** To manage the thumbnails
    * **Venv:** If you don't want to install the packages on your system but you prefer a virtual environment
- **FFmpeg:** Essential for media encoding and format conversion
    * (Installation instructions vary by OS follow some guide online)

**1. Download**

Navigate to your project directory and install the necessary Python packages:

```bash
git clone https://github.com/Valentix53/MetroDL
cd MetroDL
pip install -r requirements.txt
```

Or use the script to create the virtual environment and execute the script

``` bash
git clone https://github.com/Valentix53/MetroDL
cd MetroDL
./MetroDL # will create the environment, download the packages and execute
```

---
## 📑 Usage

### 1. Exporting the playlist from Metrolist

Select and export your playlist in csv format form Metrolist (`playlist.csv`) it should contain the following columns:

| Video Title | Artist | Album Title | YouTube URL |
| :--- | :--- | :--- | :--- |
| Song Title 1 | Artist Name | Album Name | https://... |
| Song Title 2 | Another Artist | Another Album | https://... |

### 2. Running the Script

Execute the script from your terminal, passing the name of your CSV file:

```bash
python MetroDL.py -p /path/to/playlist.csv
# or
./MetroDL -p /path/to/playlist.csv
```

---

## Command Line Arguments
- `--playlist` or `-p` Path to `csv` file (e.g. `~/music/playlist.csv`)
- `--max` or `-m` Maximum items to process (optional)
- `--numeratetracks` or `-n` Start index for track numbering, good for album playlists. If set, adds track metadata using CSV order; pass 1 to start at 1.(optional)
- `--no-covers` Skip downloading and embedding album covers. (optional)
- `--cookies` or `-c` Browser to use cookies from, default is chrome (optional)

### Key Parameters & Logic

*   **Metadata Handling:** The script uses the provided `Artist` and `Album Title` to write comprehensive tags to the media files, making them instantly recognizable in media players (iTunes, VLC, etc.).

---

## ⚠️ Troubleshooting

| Problem | Cause | Solution |
| :--- | :--- | :--- |
| `No module named '...'` | Missing Python dependency. | Re-run `pip install -r requirements.txt`. |
| `ffmpeg: command not found` | FFmpeg is not installed or not in your system PATH. | Install FFmpeg and ensure it is accessible from your terminal. |
| `ERROR: [youtube:'...'` | The YouTube URL might be private, deleted, or the required video-info page structure has changed. | Manually verify the URLs in the CSV file or delete from playlist |
| `ERROR: unable to download video data: HTTP Error 403: Forbidden` | Youtube is being flacky | Try setting --cookies from your browser (e.g. `-c chromium`) |

## Notes about AI usage in this project
I made this project in my freetime between study sessions with the assistance of a *local AI model* gemma4:e4b running on *my pc*
