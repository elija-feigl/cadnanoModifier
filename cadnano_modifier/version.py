#! /usr/bin/env python
# -*- coding: utf-8 -*-

from typing import List


__version__ = "1.1"
__authors__ = ["Elija Feigl"]
__copyright__ = "Copyright 2021, Dietzlab (TUM)"
__license__ = "GNU General Public License Version 3"
__email__ = "elija.feigl@tum.de"
__status__ = "alpha"


def get_version() -> str:
    return __version__


def get_authors() -> List[str]:
    return __authors__
