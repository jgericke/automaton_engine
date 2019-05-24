#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""auto.py"""
# Author(s): Julian Gericke
# (c) LSD
# julian@lsd.co.za
# https://lsd.co.za

import sys
import logging
import asyncio
import biome
import os


from automaton import Automaton


try:
    """ Set default loglevel
    """
    if "AUTOMATON_LOGLEVEL" in os.environ:
        logging.basicConfig(
            stream=sys.stdout,
            level=os.environ.get("AUTOMATON_LOGLEVEL"),
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

if __name__ == "__main__":
    try:
        logging.info("Automaton starting")
        automatons = []
        """ Fetch automaton configurations from environment
        """
        for cfg in range(len(biome.AUTOMATON.get_dict("config")["automatons"])):
            automatons.append(
                Automaton(
                    biome.AUTOMATON.get_dict("config")["automatons"][cfg][
                        "automaton_name"
                    ],
                    biome.AUTOMATON.get_dict("config")["automatons"][cfg][
                        "automaton_enabled"
                    ],
                    biome.AUTOMATON.get_dict("config")["automatons"][cfg][
                        "automaton_runonce"
                    ],
                    biome.AUTOMATON.get_dict("config")["automatons"][cfg][
                        "elasticsearch_url"
                    ],
                    biome.AUTOMATON.get_dict("config")["automatons"][cfg][
                        "elasticsearch_timeout"
                    ],
                    biome.AUTOMATON.get_dict("config")["automatons"][cfg][
                        "elasticsearch_query"
                    ],
                    biome.AUTOMATON.get_dict("config")["automatons"][cfg][
                        "automaton_actions"
                    ],
                )
            )
        loop = asyncio.get_event_loop()
        """ Call poller with automaton configurations collected from
        environment variables
        """
        automaton_t = [
            (Automaton.Poller(automaton)) for index, automaton in enumerate(automatons)
        ]
        """ Start event loop
        """
        loop.run_until_complete(asyncio.gather(*automaton_t))
        loop.close()
    except KeyboardInterrupt:
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
    except Exception as e:
        logging.error(e)
        raise
