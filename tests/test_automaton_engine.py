#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Automaton Engine Tests"""
# Author(s): Julian Gericke
# (c) LSD
# julian@lsd.co.za
# https://lsd.co.za

import pytest
import asynctest
import asyncio
from unittest.mock import patch, ANY
from aiohttp.client_exceptions import ClientConnectorError

from automaton_engine import AutomatonEngine


@pytest.fixture()
def automaton_engine_defaults():
    """Test defaults for automaton"""
    automaton_engine_name = "test_automaton_engine"
    automaton_engine_enabled = True
    automaton_engine_runonce = True
    automaton_engine_elasticsearch_url = "http://es.loc:9200"
    automaton_engine_elasticsearch_timeout = 1
    automaton_engine_elasticsearch_query = {
        "query_interval": 5,
        "query_endpoint": "/_search",
        "query_type": "aggregations",
        "query_name": "t_automaton_engine_query",
        "query_payload": {
            "size": 0,
            "query": {"range": {"@timestamp": {"gte": "now-1m"}}},
            "aggregations": {
                "automaton_engine_query": {
                    "terms": {
                        "field": "automaton_engine_query.keyword",
                        "min_doc_count": 1,
                    }
                }
            },
        },
        "query_response_mapping": {"key": "automaton_query", "doc_count": "hits"},
    }
    automaton_engine_actions = [
        {
            "name": "notify.rocketchat_webhook",
            "backoff_seconds": 1,
            "parameters": {
                "rocketchat_webhook": "https://rocket.local/hooks/mock-webhook",
                "rocketchat_message": "mock alert",
                "rocketchat_timeout": 1,
            },
        },
        {
            "name": "awx.api_call",
            "backoff_seconds": 1,
            "parameters": {
                "awx_url": "https://awx.local",
                "awx_context": "/api/v2/job_templates/1/launch/",
                "awx_timeout": 1,
                "awx_auth": {"username": "username", "password": "password"},
            },
        },
    ]

    yield AutomatonEngine(
        automaton_engine_name,
        automaton_engine_enabled,
        automaton_engine_runonce,
        automaton_engine_elasticsearch_url,
        automaton_engine_elasticsearch_timeout,
        automaton_engine_elasticsearch_query,
        automaton_engine_actions,
    )


class TestAutomatonEngine(object):
    def test_automaton_engine_init(self, automaton_engine_defaults):
        assert isinstance(automaton_engine_defaults, AutomatonEngine)
        assert isinstance(automaton_engine_defaults.name, str)
        assert isinstance(automaton_engine_defaults.enabled, bool)
        assert isinstance(automaton_engine_defaults.runonce, bool)
        assert isinstance(automaton_engine_defaults.es_url, str)
        assert isinstance(automaton_engine_defaults.es_query, dict)
        assert isinstance(automaton_engine_defaults.actions, list)

    @pytest.mark.asyncio
    async def test_automaton_engine_queryexecutor(self, automaton_engine_defaults):

        with asynctest.mock.patch(
            "automaton_engine.AutomatonEngine.QueryExecutor",
            side_effect=None,
            return_value=None,
        ) as m_automaton_queryexecutor:
            await AutomatonEngine.QueryExecutor(automaton_engine_defaults)
            m_automaton_queryexecutor.assert_awaited()
            m_automaton_queryexecutor.assert_called_once_with(automaton_engine_defaults)

        with pytest.raises(ClientConnectorError, match=r"Cannot connect to host"):
            await AutomatonEngine.QueryExecutor(automaton_engine_defaults)

    def test_automaton_engine_responsemapper(self, automaton_engine_defaults):
        queryresponse = {
            "aggregations": {
                "t_automaton_engine_query": {
                    "doc_count_error_upper_bound": 0,
                    "sum_other_doc_count": 0,
                    "buckets": [{"key": "test", "doc_count": 1}],
                }
            }
        }

        assert isinstance(
            AutomatonEngine.ResponseMapper(automaton_engine_defaults, queryresponse),
            list,
        )
        assert isinstance(
            AutomatonEngine.ResponseMapper(automaton_engine_defaults, queryresponse)[0][
                "hits"
            ],
            int,
        )
        assert (
            "test"
            == AutomatonEngine.ResponseMapper(automaton_engine_defaults, queryresponse)[
                0
            ]["automaton_query"]
        )
        with pytest.raises(KeyError):
            AutomatonEngine.ResponseMapper(
                automaton_engine_defaults, queryresponse.pop("aggregations", None)
            )

    @pytest.mark.asyncio
    async def test_automaton_engine_actionprocessor(self, automaton_engine_defaults):
        automaton_engine_defaults.actions[0]["executed"] = False
        automaton_engine_defaults.actions[1]["executed"] = True
        with asynctest.mock.patch(
            "automaton_engine.AutomatonEngine.ActionProcessor",
            side_effect=None,
            return_value=None,
        ) as m_automaton_actionprocessor:
            await AutomatonEngine.ActionProcessor(
                automaton_engine_defaults, [{"automaton_query": "test", "hits": 1}]
            )
            m_automaton_actionprocessor.assert_awaited()
            m_automaton_actionprocessor.assert_called_once_with(
                automaton_engine_defaults, [{"automaton_query": "test", "hits": 1}]
            )

        with pytest.raises(asyncio.TimeoutError):
            await AutomatonEngine.ActionProcessor(
                automaton_engine_defaults, [{"automaton_query": "test", "hits": 1}]
            )

        with pytest.raises(TypeError):
            await AutomatonEngine.ActionProcessor(automaton_engine_defaults, None)

    @pytest.mark.asyncio
    async def test_automaton_engine_poller(self, automaton_engine_defaults):

        with asynctest.mock.patch(
            "automaton_engine.AutomatonEngine.Poller",
            side_effect=None,
            return_value=None,
        ) as m_automaton_poller:
            await AutomatonEngine.Poller(automaton_engine_defaults)
            m_automaton_poller.assert_awaited()
            m_automaton_poller.assert_called_once_with(automaton_engine_defaults)

        with pytest.raises(ClientConnectorError, match=r"Cannot connect to host"):
            await AutomatonEngine.Poller(automaton_engine_defaults)
