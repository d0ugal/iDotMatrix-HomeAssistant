"""Pure image helpers, kept free of Home Assistant imports so they can be
tested on their own."""

from __future__ import annotations

from PIL import Image

RGB = tuple[int, int, int]


def tint_image(image: Image.Image, rgb: RGB) -> Image.Image:
    """Scale each channel towards `rgb`, so white becomes `rgb` and black stays black.

    A per-channel multiply rather than a blend, which suits the moon render:
    its background is pure black and is left untouched, while the greyscale
    disc takes on the colour at full strength.
    """
    for channel in rgb:
        if not 0 <= channel <= 255:
            raise ValueError(f"tint channel out of range: {rgb}")

    image = image.convert("RGB")
    lut: list[int] = []
    for channel in rgb:
        scale = channel / 255.0
        lut.extend(round(value * scale) for value in range(256))
    return image.point(lut)
