"""Pixel-font text overlay for the iDotMatrix 64x64 display.

Ported from tomglenn/idx-ai (MIT). Each glyph is 3×5 pixels encoded as
5 rows of 3-bit bitmasks (MSB = left column).
"""

from __future__ import annotations

from PIL import Image

SIZE = 64
GLYPH_W = 3
GLYPH_H = 5
SPACING = 1  # px gap between characters
CHAR_ADVANCE = GLYPH_W + SPACING  # 4px per character
LINE_SPACING = 7  # px between line baselines (5px glyph + 2px gap)

GLYPHS: dict[str, list[int]] = {
    "0": [0b111, 0b101, 0b101, 0b101, 0b111],
    "1": [0b010, 0b110, 0b010, 0b010, 0b111],
    "2": [0b111, 0b001, 0b111, 0b100, 0b111],
    "3": [0b111, 0b001, 0b111, 0b001, 0b111],
    "4": [0b101, 0b101, 0b111, 0b001, 0b001],
    "5": [0b111, 0b100, 0b111, 0b001, 0b111],
    "6": [0b111, 0b100, 0b111, 0b101, 0b111],
    "7": [0b111, 0b001, 0b001, 0b001, 0b001],
    "8": [0b111, 0b101, 0b111, 0b101, 0b111],
    "9": [0b111, 0b101, 0b111, 0b001, 0b111],
    ":": [0b000, 0b010, 0b000, 0b010, 0b000],
    "A": [0b111, 0b101, 0b111, 0b101, 0b101],
    "B": [0b110, 0b101, 0b110, 0b101, 0b110],
    "C": [0b111, 0b100, 0b100, 0b100, 0b111],
    "D": [0b110, 0b101, 0b101, 0b101, 0b110],
    "E": [0b111, 0b100, 0b110, 0b100, 0b111],
    "F": [0b111, 0b100, 0b110, 0b100, 0b100],
    "G": [0b111, 0b100, 0b101, 0b101, 0b111],
    "H": [0b101, 0b101, 0b111, 0b101, 0b101],
    "I": [0b111, 0b010, 0b010, 0b010, 0b111],
    "J": [0b111, 0b001, 0b001, 0b101, 0b111],
    "K": [0b101, 0b101, 0b110, 0b101, 0b101],
    "L": [0b100, 0b100, 0b100, 0b100, 0b111],
    "M": [0b101, 0b111, 0b111, 0b101, 0b101],
    "N": [0b101, 0b111, 0b111, 0b111, 0b101],
    "O": [0b111, 0b101, 0b101, 0b101, 0b111],
    "P": [0b110, 0b101, 0b110, 0b100, 0b100],
    "Q": [0b111, 0b101, 0b101, 0b111, 0b011],
    "R": [0b110, 0b101, 0b110, 0b101, 0b101],
    "S": [0b111, 0b100, 0b111, 0b001, 0b111],
    "T": [0b111, 0b010, 0b010, 0b010, 0b010],
    "U": [0b101, 0b101, 0b101, 0b101, 0b111],
    "V": [0b101, 0b101, 0b101, 0b101, 0b010],
    "W": [0b101, 0b101, 0b111, 0b111, 0b101],
    "X": [0b101, 0b101, 0b010, 0b101, 0b101],
    "Y": [0b101, 0b101, 0b010, 0b010, 0b010],
    "Z": [0b111, 0b001, 0b010, 0b100, 0b111],
    " ": [0b000, 0b000, 0b000, 0b000, 0b000],
    ".": [0b000, 0b000, 0b000, 0b000, 0b010],
    "-": [0b000, 0b000, 0b111, 0b000, 0b000],
    "'": [0b010, 0b010, 0b000, 0b000, 0b000],
    "!": [0b010, 0b010, 0b010, 0b000, 0b010],
    "?": [0b111, 0b001, 0b011, 0b000, 0b010],
    "&": [0b110, 0b110, 0b011, 0b101, 0b011],
    "+": [0b000, 0b010, 0b111, 0b010, 0b000],
    "/": [0b001, 0b001, 0b010, 0b100, 0b100],
}

# Maximum chars that fit in the usable text width (60px / 4px per char = 15)
MAX_TEXT_WIDTH = SIZE - 2 - 2  # = 60px
MAX_CHARS = MAX_TEXT_WIDTH // CHAR_ADVANCE  # = 15

START_X = 2  # left margin for text
START_Y = 2  # top margin for text


def _text_width(text: str) -> int:
    """Pixel width of a string (no trailing spacing)."""
    if not text:
        return 0
    return len(text) * CHAR_ADVANCE - SPACING


def truncate(text: str) -> str:
    """Truncate text to fit within MAX_TEXT_WIDTH pixels."""
    upper = text.upper()
    if _text_width(upper) <= MAX_TEXT_WIDTH:
        return upper
    # Trim char by char until it fits (accounts for unknown glyphs same width)
    for i in range(len(upper), 0, -1):
        if _text_width(upper[:i]) <= MAX_TEXT_WIDTH:
            return upper[:i]
    return ""


def apply_now_playing_overlay(img: Image.Image, track: str, artist: str) -> Image.Image:
    """Draw darkened background + white pixel-font track/artist text onto img.

    Modifies img in place and returns it.
    """
    track_str = truncate(track)
    artist_str = truncate(artist)

    if not track_str and not artist_str:
        return img

    pix = img.load()
    total_h = (LINE_SPACING if track_str else 0) + (GLYPH_H if artist_str else 0)
    track_w = _text_width(track_str)
    artist_w = _text_width(artist_str)
    bg_w = max(track_w, artist_w) + 2  # 1px padding each side

    # Darken background (each channel → channel >> 2, i.e. 25% brightness)
    for dy in range(-1, total_h + 1):
        for dx in range(-1, bg_w + 1):
            px = START_X - 1 + dx
            py = START_Y + dy
            if 0 <= px < SIZE and 0 <= py < SIZE:
                r, g, b = pix[px, py]
                pix[px, py] = (r >> 2, g >> 2, b >> 2)

    # Draw glyphs
    def draw_string(text: str, y: int) -> None:
        cursor_x = START_X
        for ch in text:
            rows = GLYPHS.get(ch)
            if rows is None:
                cursor_x += CHAR_ADVANCE
                continue
            for row_idx, row_bits in enumerate(rows):
                for col in range(GLYPH_W):
                    if row_bits & (1 << (GLYPH_W - 1 - col)):
                        px, py = cursor_x + col, y + row_idx
                        if 0 <= px < SIZE and 0 <= py < SIZE:
                            pix[px, py] = (255, 255, 255)
            cursor_x += CHAR_ADVANCE

    if track_str:
        draw_string(track_str, START_Y)
    if artist_str:
        draw_string(artist_str, START_Y + LINE_SPACING)

    return img


def render_now_playing_frames(
    base_img: Image.Image,
    track: str,
    artist: str,
    frame_delay: int = 100,
    pause_ms: int = 2000,
    scroll_speed: int = 2,
) -> list[tuple[Image.Image, int]]:
    """Return (frame, duration_ms) pairs for now-playing display.

    If both lines fit within MAX_TEXT_WIDTH, returns a single static frame.
    Otherwise generates a scrolling animation: initial pause at the start of
    the text, then scrolls left until the end of the longest line is visible,
    then a shorter end-pause before looping.
    """
    track_upper = track.upper()
    artist_upper = artist.upper()

    track_w = _text_width(track_upper)
    artist_w = _text_width(artist_upper)

    # Static: both lines fit without scrolling
    if track_w <= MAX_TEXT_WIDTH and artist_w <= MAX_TEXT_WIDTH:
        frame = base_img.copy()
        apply_now_playing_overlay(frame, track, artist)
        return [(frame, frame_delay)]

    # Animated scroll
    has_track = bool(track_upper)
    has_artist = bool(artist_upper)
    total_h = (LINE_SPACING if has_track else 0) + (GLYPH_H if has_artist else 0)

    max_line_w = max(track_w, artist_w)
    # Scroll just enough to reveal the full end of the longest line + one char gap
    end_offset = -(max_line_w - MAX_TEXT_WIDTH + CHAR_ADVANCE)

    def make_frame(offset: int) -> Image.Image:
        frame = base_img.copy()
        pix = frame.load()
        # Darken a full-width strip behind the text area
        for dy in range(-1, total_h + 1):
            for dx in range(SIZE):
                py = START_Y + dy
                if 0 <= py < SIZE:
                    r, g, b = pix[dx, py]
                    pix[dx, py] = (r >> 2, g >> 2, b >> 2)

        # Draw glyphs at scrolled x position
        def draw_str(text: str, y: int) -> None:
            cx = START_X + offset
            for ch in text:
                rows = GLYPHS.get(ch)
                if rows is None:
                    cx += CHAR_ADVANCE
                    continue
                for ri, rb in enumerate(rows):
                    for col in range(GLYPH_W):
                        if rb & (1 << (GLYPH_W - 1 - col)):
                            px, py = cx + col, y + ri
                            if 0 <= px < SIZE and 0 <= py < SIZE:
                                pix[px, py] = (255, 255, 255)
                cx += CHAR_ADVANCE

        if has_track:
            draw_str(track_upper, START_Y)
        if has_artist:
            draw_str(artist_upper, START_Y + LINE_SPACING)
        return frame

    frames: list[tuple[Image.Image, int]] = []

    # Initial pause: show start of text
    frames.append((make_frame(0), pause_ms))

    # Scroll from just past start to end_offset
    for offset in range(-scroll_speed, end_offset, -scroll_speed):
        frames.append((make_frame(offset), frame_delay))

    # Final frame at exact end position, shorter pause before looping
    frames.append((make_frame(end_offset), pause_ms // 2))

    return frames
