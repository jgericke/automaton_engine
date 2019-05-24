#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Automaton."""
# Author(s): Julian Gericke
# (c) LSD
# julian@lsd.co.za
# https://lsd.co.za

import asyncio
import async_timeout
from aiohttp import ClientSession
from dataclasses import dataclass

import json
import logging
import datetime

from .actions import notify
from .actions import awx

logger = logging.getLogger(__name__)

"""Automaton actions which can be effected
- actions.notify : send webhook notification to RocketChat
- actions.awx    : send api call to ansible awx
"""
action_dispatcher = {
    "notify.rocketchat_webhook": notify.rocketchat_webhook,
    "awx.api_call": awx.api_call,
}


@dataclass
class Automaton:
    """Automaton.
    """

    name: str
    enabled: bool
    runonce: bool
    es_url: str
    es_tmo: int
    es_query: dict
    actions: list

    async def QueryExecutor(self) -> dict:
        """Runs query_payload and returns query_response.

            Args:
                None
            Returns:
                dict:    query_response (elasticsearch query response)
            Raises:
                asyncio.TimeoutError
                General Exception
        """
        try:
            async with ClientSession(skip_auto_headers=["User-Agent"]) as session:
                with async_timeout.timeout(self.es_tmo):
                    async with session.post(
                        self.es_url + self.es_query["query_endpoint"],
                        data=json.dumps(self.es_query["query_payload"]),
                        headers={"content-type": "application/json"},
                    ) as response:
                        assert response.status == 200
                        query_response = await response.json()
                        return query_response
        except asyncio.TimeoutError as tmo_e:
            logging.error(tmo_e)
            raise
        except Exception as e:
            logging.error(e)
            raise

    def ResponseMapper(self, query_response: list) -> list:
        """Map an elasticsearch query response using query_response_mapping.

            Args:
                list:    query_response (elasticsearch query response)
            Returns:
                list:    mapped_responses (query_response_mapping)
            Raises:
                General Exception
        """
        try:
            mapped_responses = []
            for bucket in query_response[self.es_query["query_type"]][
                self.es_query["query_name"]
            ]["buckets"]:
                mapped_response = {
                    self.es_query["query_response_mapping"].get(key, key): value
                    for key, value in bucket.items()
                }
                mapped_responses.append(mapped_response)
            return mapped_responses
        except Exception as e:
            logging.error(e)
            raise

    async def ActionProcessor(self, action_metadata: list):
        """Execute actions defined in automaton_actions.
        Actions are functions expressed in action_dispatcher,
        and are passed action_name, action_parameters and
        action_metadata.

        For first time execution, action processor will add an
        exec and timestamp key to the executed automaton. Execution
        will only re-occur once the time period expressed in
        action_backoff_seconds is reached.


            Args:
                list:    action_metadata (mapped_responses from ResponseMapper)
            Returns:
                None
            Raises:
                General Exception
        """
        try:
            for index, action in enumerate(self.actions):
                if action["action_name"] in action_dispatcher:
                    if "executed" in action:
                        if action["executed"] is False:
                            logging.info(
                                "automaton: {} executing action: {}".format(
                                    self.name, action["action_name"]
                                )
                            )
                            await action_dispatcher[action["action_name"]](
                                action["action_parameters"], action_metadata
                            )
                            action["executed"] = True
                            action["exec_time"] = datetime.datetime.now()
                            logging.info(
                                "automaton: {} execution of action: {} completed".format(
                                    self.name, action["action_name"]
                                )
                            )
                    if "exec_time" in action:
                        if action[
                            "exec_time"
                        ] < datetime.datetime.now() - datetime.timedelta(
                            seconds=action["action_backoff_seconds"]
                        ):
                            logging.debug("backoff for executed action has elapsed")
                            action["executed"] = False
        except Exception as e:
            logging.error(e)
            raise

    async def Poller(self):
        """Automatons mainloop.
        1. Calls QueryExecutor
        2. If automatons query returns valid data, call ResponseMapper
        3. Send mapped response to action processor which calls defined actions

        If no response is retrieved from QueryExecutor the automaton waits
        for the duration of the query_interval period.


            Args:
                None
            Returns:
                None
            Raises:
                General Exception
        """
        try:
            while self.enabled:
                query_response = await self.QueryExecutor()
                if (
                    query_response["aggregations"][self.es_query["query_name"]][
                        "buckets"
                    ]
                    and len(
                        query_response["aggregations"][self.es_query["query_name"]][
                            "buckets"
                        ]
                    )
                    > 0
                ):
                    action_metadata = self.ResponseMapper(query_response)
                    logging.info(
                        "automaton: {} activity detected with metadata: {}".format(
                            self.name, action_metadata
                        )
                    )
                    await self.ActionProcessor(action_metadata)
                else:
                    logging.debug(
                        "automaton: {} has detected no activity".format(self.name)
                    )
                if self.runonce:
                    break
                else:
                    await asyncio.sleep(self.es_query["query_interval"])
        except Exception as e:
            logging.error(e)
            raise
