#!/usr/bin/env python
# -*- coding: utf-8 -*-

import asyncio
import async_timeout
from aiohttp import ClientSession

import json
import logging

logger = logging.getLogger(__name__)


async def rocketchat_webhook(action_parameters, action_metadata):
    """Send notification via rocketchat webhook.

        Args:
            list:    action_parameters (rocketchat action parameters)
            list:    action_metadata (mapped_responses from ResponseMapper)
        Returns:
            None
        Raises:
            asyncio.TimeoutError
            General Exception
    """
    try:
        for index, action_obj in enumerate(action_metadata):
            notification = {
                "text": action_parameters["rocketchat_message"]
                + "\naction metadata: {}".format(action_obj)
            }
            logging.debug(
                "sending rocketchat notfication with action metadata: {}".format(
                    action_obj
                )
            )
            async with ClientSession(skip_auto_headers=["User-Agent"]) as session:
                with async_timeout.timeout(action_parameters["rocketchat_timeout"]):
                    async with session.post(
                        action_parameters["rocketchat_webhook"],
                        data=json.dumps(notification),
                        headers={"content-type": "application/json"},
                    ) as response:
                        assert response.status == 200
            logging.info("rocketchat notification has been sent")
    except asyncio.TimeoutError as timeout_ex:
        logging.error(timeout_ex)
        raise
    except Exception as ex:
        logging.error(ex)
        raise
