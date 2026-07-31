"""Tests for the pure image helpers.

imaging.py is loaded straight off disk rather than imported as part of the
package, because custom_components/idotmatrix/__init__.py pulls in Home
Assistant and these helpers deliberately do not need it.
"""

import importlib.util
from pathlib import Path

import pytest
from PIL import Image

_PATH = Path(__file__).parent.parent / "custom_components" / "idotmatrix" / "imaging.py"
_spec = importlib.util.spec_from_file_location("idotmatrix_imaging", _PATH)
assert _spec and _spec.loader
_imaging = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_imaging)
tint_image = _imaging.tint_image

GOLD = (255, 200, 80)


def _solid(rgb, size=(4, 4)):
    return Image.new("RGB", size, rgb)


def test_white_becomes_the_tint():
    out = tint_image(_solid((255, 255, 255)), GOLD)
    assert out.getpixel((0, 0)) == GOLD


def test_black_is_left_alone():
    """The moon render's background is pure black and must stay that way."""
    out = tint_image(_solid((0, 0, 0)), GOLD)
    assert out.getpixel((0, 0)) == (0, 0, 0)


def test_grey_scales_proportionally():
    out = tint_image(_solid((128, 128, 128)), GOLD)
    assert out.getpixel((0, 0)) == (128, 100, 40)


def test_full_white_tint_is_a_no_op():
    out = tint_image(_solid((123, 45, 67)), (255, 255, 255))
    assert out.getpixel((0, 0)) == (123, 45, 67)


def test_greyscale_input_is_converted_to_rgb():
    out = tint_image(Image.new("L", (2, 2), 255), GOLD)
    assert out.mode == "RGB"
    assert out.getpixel((0, 0)) == GOLD


def test_size_and_mode_are_preserved():
    out = tint_image(_solid((200, 200, 200), size=(64, 64)), GOLD)
    assert out.size == (64, 64)
    assert out.mode == "RGB"


@pytest.mark.parametrize("bad", [(256, 0, 0), (-1, 0, 0), (0, 0, 300)])
def test_out_of_range_channels_are_rejected(bad):
    with pytest.raises(ValueError):
        tint_image(_solid((255, 255, 255)), bad)
