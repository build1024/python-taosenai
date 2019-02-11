# -*- coding: utf-8 -*-

import os
# make shared modules available (especially on cygwin)
os.environ["PATH"] = os.path.dirname(__file__) + ":" + os.environ.get("PATH", "")

from _TaosenaiPlaying import TaosenaiPlaying
from _PenaltyTable import PenaltyTable
