"""Constants for the iDotMatrix integration."""

DOMAIN = "idotmatrix"
CONF_MAC = "mac_address"
CONF_NAME = "name"

DEFAULT_NAME = "iDotMatrix"
CONF_MAC = "mac_address"

# Data Storage Keys
STORAGE_VERSION = 1
STORAGE_KEY_PREFIX = "idotmatrix_settings_"

# New Constants for Display Face
CONF_DISPLAY_FACE = "display_face"
CONF_DISPLAY_MODE = "display_mode"

DISPLAY_MODE_TEXT = "text"
DISPLAY_MODE_DESIGN = "design"
DISPLAY_MODE_EXTERNAL = "external"    # display managed externally; coordinator skips updates
DISPLAY_MODE_MOON = "moon"            # moon phase renderer built into coordinator
DISPLAY_MODE_NOW_PLAYING = "now_playing"  # media player art; set by service, reverts on stop
DISPLAY_MODE_OPTIONS = {
    DISPLAY_MODE_TEXT: "Display Text Field",
    DISPLAY_MODE_DESIGN: "Display design from the Card",
    DISPLAY_MODE_MOON: "Moon Phase",
}
LAYER_TYPE_TEXT = "text"
LAYER_TYPE_IMAGE = "image"
LAYER_TYPE_SHAPE = "shape"

ANIMATION_MODES = {
    "Hold": 0,
    "Left": 1,
    "Right": 2,
    "Up": 3,
    "Down": 4,
    "Blink": 5,
    "Fade": 6,
    "Tetris": 7,
    "Fill": 8,
}

COLOR_MODES = {
    "White": 0,
    "Custom Color": 1,
    "Rainbow 1": 2,
    "Rainbow 2": 3,
    "Rainbow 3": 4,
    "Rainbow 4": 5,
}
