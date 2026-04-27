"""
idotmatrix.

Library to configure any iDotMatrix compatible pixel display without the
iDotMatrix android / iOS app.
"""

from .connectionManager import ConnectionManager
from .modules.common import Common
from .modules.gif import Gif

__author__ = "Kalle Minkner, Jon-Mailes Graeffe"
__credits__ = "everyone who thankfully helped with the reverse-engineering. You are awesome!"
__all__ = [
    "Common",
    "ConnectionManager",
    "Gif",
]
