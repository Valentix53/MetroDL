#!/usr/bin/env python3
import argparse
import csv
import os
import shlex
import subprocess
import sys
import time
from subprocess import CalledProcessError
from PIL import Image

DEVNULL = subprocess.DEVNULL
TMPDIR = ".tmp_dl"

def sanitize_filename(s: str) -> str:
    return "".join(c if c not in r'\/:*?"<>|' else '_' for c in s)

def main():
    parser = argparse.ArgumentParser(description="Download YouTube audio from CSV playlist")
    parser.add_argument("--playlist", "-p", required=True, help="CSV playlist filename (e.g. @music_2.csv)")
    parser.add_argument("--max", "-m", type=int, default=None, help="Maximum items to process (optional)")
    parser.add_argument("--numeratetracks", "-n", type=int, default=None, help="Start index for track numbering (optional). If set, adds track metadata using CSV order; pass 1 to start at 1.")
    parser.add_argument("--no-covers", action="store_true", default=False, help="Skip downloading and embedding album covers. (optional)")
    parser.add_argument("--cookies", "-c", choices=["brave", "chrome", "chromium", "edge", "firefox", "opera", "safari", "vivaldi", "whale"], default="chrome", help="Browser to use cookies from, default is chrome (optional)")
    parser.add_argument("--cookie-file", "-C", default=None, help="Don't use browser cookies but use a file (optional)")
    parser.add_argument("--ffmpeg", "-f", default="ffmpeg", help="Sets ffmpeg path (/path/to/ffmpeg) (optional)")
    args = parser.parse_args()

    CSV = args.playlist
    if not os.path.exists(CSV):
        print("Playlist file not found:", CSV)
        sys.exit(1)

    cookie_flag = ""
    cookies = ""
    # derive OUTDIR from playlist basename (without extension)
    base = os.path.splitext(os.path.basename(CSV))[0]
    OUTDIR = base  # e.g., "@playlist"
    MAX = args.max
    start_idx = args.numeratetracks
    no_covers = args.no_covers
    if args.cookie_file == None:
        cookie_flag = "--cookies-from-browser"
        cookies = args.cookies
    else:
        cookie_flag = "--cookies"
        cookies = args.cookie_file

    ffmpeg = args.ffmpeg

    print(f'yt-dlp --quiet -f bestaudio --output "{TMPDIR}/%(id)s.%(ext)s" --write-thumbnail --skip-download  {cookie_flag} {cookies}')

    os.makedirs(OUTDIR, exist_ok=True)
    os.makedirs(TMPDIR, exist_ok=True)

    with open(CSV, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if MAX is not None and i >= MAX:
                break

            title = row.get('Title', '').strip()
            artist = row.get('Artist', '').strip()
            album = row.get('Album', '').strip()
            vid = row.get('YouTube Video ID', '').strip()
            if not vid:
                print(f"Skipping line with empty ID: {title or artist or i}")
                continue

            safe = (artist + ' - ' + title) if artist else title
            safe = sanitize_filename(safe) or vid
            out_mp3 = os.path.join(OUTDIR, f"{safe}.mp3")
            if os.path.exists(out_mp3):
                continue

            print("Processing:", safe)

            # 1) download thumbnail (quiet, no-part)
            try:
                if not no_covers:
                    subprocess.run(
                        shlex.split(
                            f'yt-dlp --quiet -f bestaudio --output "{TMPDIR}/%(id)s.%(ext)s" --write-thumbnail --skip-download {cookie_flag} {cookies} --no-warnings https://www.youtube.com/watch?v={vid}'
                        ),
                        check=True
                    )
            except CalledProcessError:
                pass

            # 2) download audio (quiet, no-part) — fail this item on error
            try:
                subprocess.run(
                    shlex.split(
                        f'yt-dlp -t mp3 -f bestaudio --output "{TMPDIR}/%(id)s.%(ext)s" http://www.youtube.com/watch?v={vid} {cookie_flag} {cookies} --fragment-retries 3'
                    ),
                    check=True
                )
            except CalledProcessError:
                print("Audio download failed for", vid)
                for fn in os.listdir(TMPDIR):
                    if fn.startswith(vid):
                        try: os.remove(os.path.join(TMPDIR, fn))
                        except: pass
                continue

            audio_path = os.path.join(TMPDIR, vid + ".mp3")

            # metadata args
            meta = []
            if title: meta += ['-metadata', f'title={title}']
            if artist: meta += ['-metadata', f'artist={artist}']
            if album: meta += ['-metadata', f'album={album}']

            # find thumbnail image if any
            thumb = None
            for ext in ('jpg', 'jpeg', 'webp', 'png'):
                p = os.path.join(TMPDIR, f'{vid}.{ext}')
                if os.path.exists(p):
                    thumb = p
                    break

                cover = None
            if thumb:
                # open with Pillow
                with Image.open(thumb) as im:
                    # ensure RGB for JPEG output
                    im = im.convert("RGB")
                    w, h = im.size
                    s = min(w, h)
                    # center crop coords
                    left = (w - s) // 2
                    top = (h - s) // 2
                    right = left + s
                    bottom = top + s
                    im = im.crop((left, top, right, bottom))
                    # resize to 600x600 with high-quality resampling
                    im = im.resize((600, 600), resample=Image.LANCZOS)
                    sq = os.path.join(TMPDIR, f'{vid}_square.jpg')
                    im.save(sq, format="JPEG", quality=90)
                    cover = sq

            # encode to temporary output then atomically move on success
            tmp_out = out_mp3

            if cover:
                print("cover found")
                if start_idx is not None:
                    track_num = i + start_idx
                    cmd = [ffmpeg, '-y', '-loglevel', 'error', '-i', audio_path, '-i', cover,
                        '-map', '0:a', '-map', '1', '-c:a', 'libmp3lame', '-q:a', '2'] + meta + [
                        '-id3v2_version', '3', '-metadata', f'track={track_num}',
                        '-metadata:s:v', 'title=Album cover',
                        '-metadata:s:v', 'comment=Cover (front)', '-f', 'mp3', tmp_out]
                else:
                    cmd = [ffmpeg, '-y', '-loglevel', 'error', '-i', audio_path, '-i', cover,
                        '-map', '0:a', '-map', '1', '-c:a', 'libmp3lame', '-q:a', '2'] + meta + [
                        '-id3v2_version', '3', '-metadata:s:v', 'title=Album cover',
                        '-metadata:s:v', 'comment=Cover (front)', '-f', 'mp3', tmp_out]

            else:
                print("cover not found")

                if start_idx is not None:
                    track_num = i + start_idx
                    cmd = [ffmpeg, '-y', '-loglevel', 'error', '-i', audio_path,
                        '-c:a', 'libmp3lame', '-q:a', '2'] + meta + ['-id3v2_version', '3', '-metadata', f'track={track_num}', '-f', 'mp3', tmp_out]
                else:
                    cmd = [ffmpeg, '-y', '-loglevel', 'error', '-i', audio_path,
                        '-c:a', 'libmp3lame', '-q:a', '2'] + meta + ['-id3v2_version', '3', '-f', 'mp3', tmp_out]

            if not os.path.exists(audio_path) or os.path.getsize(audio_path) == 0:
                print("Missing/empty audio file:", audio_path)
                for fn in os.listdir(TMPDIR):
                    if fn.startswith(vid):
                        try:
                            os.remove(os.path.join(TMPDIR, fn))
                        except:
                            pass
                continue

            try:
                proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                if proc.returncode == 0:
                    os.replace(tmp_out, out_mp3)
                    print("Saved ->", out_mp3)
                else:
                    errlog = os.path.join(OUTDIR, f'{vid}_ffmpeg_error.log')
                    with open(errlog, 'w', encoding='utf-8') as e:
                        e.write(proc.stderr)
                    print("Encoding failed for", vid, f"(see {errlog})")
            finally:
                for fn in os.listdir(TMPDIR):
                    if fn.startswith(vid):
                        try:
                            os.remove(os.path.join(TMPDIR, fn))
                        except: pass

    print("Done.")

if __name__ == "__main__":
    main()
