#!/usr/bin/env python3
"""Render the bring-the-humans-03 TikTok ad (18 s, 1080x1920, 60 fps).

Composes four still scenes, the make.fun brand badge and the referral end
card into one vertical video with ffmpeg. The filter graph itself lives in
build/filter.txt next to this script; this file only drives ffmpeg and
checks the result.

Layout (seconds): s1 0-4, s2 4-8, s3 8-12, s4 12-16, each with a slow
zoom and a 0.4 s fade into the next; the badge sits on screen 0-16; the
referral end card covers 16-18 over a blurred, desaturated freeze of the
last scene, with the referral code typed into its field near the end.

The render is bounded: -t 18 caps the output at 18 seconds and the fast
preset keeps the encode to a few minutes, so it can never run away.
"""

import subprocess
import sys
from pathlib import Path

# Repository root is the parent of the build/ directory holding this file.
REPO_ROOT = Path(__file__).resolve().parent.parent
BUILD_DIR = REPO_ROOT / "build"
SCENES_DIR = BUILD_DIR / "scenes"

# Press-pack assets (badge, end card, font) live in the sibling build/
# directory next to the repository, where they were fetched.
ASSETS_DIR = REPO_ROOT.parent / "build"

FILTER_FILE = BUILD_DIR / "filter.txt"
OUTPUT_FILE = REPO_ROOT / "ad.mp4"

DURATION_SECONDS = 18
RENDER_TIMEOUT_SECONDS = 600


def require_file(path: Path) -> None:
    """Fail loudly when an input the render needs is missing."""
    if not path.is_file():
        print(f"missing input file: {path}", file=sys.stderr)
        sys.exit(1)


def main() -> int:
    scene_files = [SCENES_DIR / f"s{n}.png" for n in (1, 2, 3, 4)]
    for path in scene_files + [
        ASSETS_DIR / "badge-9x16.png",
        ASSETS_DIR / "card-9x16-transparent.webm",
        ASSETS_DIR / "JetBrainsMono-Bold.ttf",
        FILTER_FILE,
    ]:
        require_file(path)

    # One looped still per scene, then the badge still, then the card
    # video (VP9 with transparency, decoded by libvpx-vp9).
    command = [
        "ffmpeg", "-y", "-v", "error",
        "-loop", "1", "-i", str(scene_files[0]),
        "-loop", "1", "-i", str(scene_files[1]),
        "-loop", "1", "-i", str(scene_files[2]),
        "-loop", "1", "-i", str(scene_files[3]),
        "-i", str(ASSETS_DIR / "badge-9x16.png"),
        "-c:v", "libvpx-vp9",
        "-i", str(ASSETS_DIR / "card-9x16-transparent.webm"),
        "-filter_complex_script", str(FILTER_FILE),
        "-map", "[v]",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-crf", "18",
        "-preset", "veryfast",
        "-movflags", "+faststart",
        "-t", str(DURATION_SECONDS),
        str(OUTPUT_FILE),
    ]

    print(f"rendering {OUTPUT_FILE} ({DURATION_SECONDS}s, 1080x1920, 60fps)")
    try:
        subprocess.run(
            command, check=True, timeout=RENDER_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired:
        print(
            f"render ran past {RENDER_TIMEOUT_SECONDS}s, stopped",
            file=sys.stderr,
        )
        return 1
    except subprocess.CalledProcessError as exc:
        print(f"ffmpeg failed with exit code {exc.returncode}", file=sys.stderr)
        return 1

    if not OUTPUT_FILE.is_file() or OUTPUT_FILE.stat().st_size == 0:
        print(f"render produced no output at {OUTPUT_FILE}", file=sys.stderr)
        return 1

    print(f"render done: {OUTPUT_FILE} ({OUTPUT_FILE.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
