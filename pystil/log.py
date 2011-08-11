# -*- coding: utf-8 -*-
# Copyright (C) 2011 by Florian Mounier, Kozea
# This file is part of brigit, licensed under a 3-clause BSD license.
"""
Brigit logger

"""
import sys
import logging

from logging import StreamHandler

BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)
COLORS = {
    'WARNING': YELLOW,
    'INFO': GREEN,
    'DEBUG': BLUE,
    'CRITICAL': YELLOW,
    'ERROR': RED,
    'RED': RED,
    'GREEN': GREEN,
    'YELLOW': YELLOW,
    'BLUE': BLUE,
    'MAGENTA': MAGENTA,
    'CYAN': CYAN,
    'WHITE': WHITE}
RESET_SEQ = '\033[0m'
COLOR_SEQ = '\033[1;%dm'
BOLD_SEQ = '\033[1m'


class ColorFormatter(logging.Formatter):
    """Logging formatter adding console colors to the output.
    """
    def format(self, record):
        """Format the record with colors."""
        color = COLOR_SEQ % (30 + COLORS[record.levelname])
        message = logging.Formatter.format(self, record)
        message = message.replace('$RESET', RESET_SEQ)\
            .replace('$BOLD', BOLD_SEQ)\
            .replace('$COLOR', color)
        for color, value in COLORS.items():
            message = message.replace('$' + color, COLOR_SEQ % (value + 30))\
                .replace('$BG' + color, COLOR_SEQ % (value + 40))\
                .replace('$BG-' + color, COLOR_SEQ % (value + 40))
        return message + RESET_SEQ


def get_default_handler():
    """Return the default handler"""
    handler = StreamHandler(sys.stderr)
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(
        ColorFormatter(
            '$COLOR%(levelname)s %(asctime)s '
            '$BOLD$COLOR%(name)s$RESET %(message)s'))
    return handler
