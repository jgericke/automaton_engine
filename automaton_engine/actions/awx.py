#!/usr/bin/env python
# -*- coding: utf-8 -*-

import asyncio
import async_timeout
from aiohttp import ClientSession, BasicAuth, TCPConnector

import base64
import json
import logging

logger = logging.getLogger(__name__)


async def api_call(action_parameters, action_metadata):
    """Calls Ansible AWX API.

        Args:
            list:    action_parameters (awx API action parameters)
            list:    action_metadata (mapped_responses from ResponseMapper)
        Returns:
            None
        Raises:
            asyncio.TimeoutError
            General Exception
    """
    try:
        for index, action_obj in enumerate(action_metadata):
            logging.debug("calling awx api with action metadata: {}".format(action_obj))
            async with ClientSession(
                skip_auto_headers=["User-Agent"],
                auth=BasicAuth(
                    base64.b64decode(action_parameters["awx_auth"]["username"]).decode(
                        "utf-8"
                    ),
                    base64.b64decode(action_parameters["awx_auth"]["password"]).decode(
                        "utf-8"
                    ),
                ),
                connector=TCPConnector(verify_ssl=False),
            ) as session:
                with async_timeout.timeout(action_parameters["awx_timeout"]):
                    async with session.post(
                        action_parameters["awx_url"] + action_parameters["awx_context"],
                        data=json.dumps({"extra_vars": action_obj}),
                        headers={"content-type": "application/json"},
                    ) as response:
                        # Created
                        assert response.status == 201
            logging.info("awx api call has been executed")
    except asyncio.TimeoutError as timeout_ex:
        logging.error(timeout_ex)
        raise
    except Exception as ex:
        logging.error(ex)
        raise
