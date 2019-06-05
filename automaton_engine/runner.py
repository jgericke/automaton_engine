#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import logging
import asyncio
import biome
import os


from automaton_engine import AutomatonEngine

logger = logging.getLogger(__name__)


def runner(argv=None):
    try:
        logging.info("AutomatonEngine starting")
        automaton_engines = []
        """ Fetch automaton configurations from environment
        """
        for cfg in range(len(biome.AUTOMATON_ENGINE.get_dict("config")["automatons"])):
            automaton_engines.append(
                AutomatonEngine(
                    biome.AUTOMATON_ENGINE.get_dict("config")["automatons"][cfg][
                        "name"
                    ],
                    biome.AUTOMATON_ENGINE.get_dict("config")["automatons"][cfg][
                        "enabled"
                    ],
                    biome.AUTOMATON_ENGINE.get_dict("config")["automatons"][cfg][
                        "runonce"
                    ],
                    biome.AUTOMATON_ENGINE.get_dict("config")["automatons"][cfg][
                        "elasticsearch_url"
                    ],
                    biome.AUTOMATON_ENGINE.get_dict("config")["automatons"][cfg][
                        "elasticsearch_timeout"
                    ],
                    biome.AUTOMATON_ENGINE.get_dict("config")["automatons"][cfg][
                        "elasticsearch_query"
                    ],
                    biome.AUTOMATON_ENGINE.get_dict("config")["automatons"][cfg][
                        "actions"
                    ],
                )
            )
        loop = asyncio.get_event_loop()
        """ Call poller with automaton configurations collected from
        environment variables
        """
        automaton_engine_t = [
            (AutomatonEngine.Poller(automaton))
            for index, automaton in enumerate(automaton_engines)
        ]
        """ Start event loop
        """
        loop.run_until_complete(asyncio.gather(*automaton_engine_t))
        loop.close()
    except KeyboardInterrupt:
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
    except Exception as e:
        logging.error(e)
        raise


if __name__ == "__main__":
    try:
        runner()
    except Exception as e:
        logging.error(e)
        raise
