#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import logging
from os import environ

from automaton_engine.engine import AutomatonEngine

try:
    if "AUTOMATON_ENGINE_LOGLEVEL" in environ:
        logging.basicConfig(
            stream=sys.stdout,
            level=environ.get("AUTOMATON_ENGINE_LOGLEVEL"),
            format="%(asctime)s %(name)s %(levelname)s" + " %(message)s ",
        )
    else:
        logging.basicConfig(
            stream=sys.stdout,
            level="INFO",
            format="%(asctime)s %(name)s %(levelname)s" + " %(message)s ",
        )
    logger = logging.getLogger(__name__)
except (KeyError, ValueError, AttributeError, Exception):
    raise
