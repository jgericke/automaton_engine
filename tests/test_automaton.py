#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Automaton unit tests"""
# Author(s): Julian Gericke
# (c) LSD
# julian@lsd.co.za
# https://lsd.co.za

import pytest
import asynctest
import asyncio
from unittest.mock import patch, ANY
from aiohttp.client_exceptions import ClientConnectorError

from automaton import Automaton


@pytest.fixture()
def t_automaton_defaults():
    """Test defaults for automaton"""
    t_automaton_name = "t_automaton"
    t_automaton_enabled = True
    t_automaton_runonce = True
    t_elasticsearch_url = "http://es.loc:9200"
    t_elasticsearch_timeout = 1
    t_elasticsearch_query = {
        "query_interval": 5,
        "query_endpoint": "/_search",
        "query_type": "aggregations",
        "query_name": "t_automaton_query",
        "query_payload": {
            "size": 0,
            "query": {"range": {"@timestamp": {"gte": "now-1m"}}},
            "aggregations": {
                "t_automaton_query": {
                    "terms": {"field": "t_automaton_query.keyword", "min_doc_count": 1}
                }
            },
        },
        "query_response_mapping": {"key": "automaton_query", "doc_count": "hits"},
    }
    t_automaton_actions = [
        {
            "action_name": "notify.rocketchat_webhook",
            "action_backoff_seconds": 1,
            "action_parameters": {
                "rocketchat_webhook": "https://rocket.local/hooks/mock-webhook",
                "rocketchat_message": "t_automaton_action_notify mock alert",
                "rocketchat_timeout": 1,
            },
        },
        {
            "action_name": "awx.api_call",
            "action_backoff_seconds": 1,
            "action_parameters": {
                "awx_url": "https://awx.local",
                "awx_context": "/api/v2/job_templates/1/launch/",
                "awx_timeout": 1,
                "awx_auth": {"username": "username", "password": "password"},
            },
        },
    ]

    yield Automaton(
        t_automaton_name,
        t_automaton_enabled,
        t_automaton_runonce,
        t_elasticsearch_url,
        t_elasticsearch_timeout,
        t_elasticsearch_query,
        t_automaton_actions,
    )


class TestAutomaton(object):
    def test_automaton_init(self, t_automaton_defaults):
        assert isinstance(t_automaton_defaults, Automaton)
        assert isinstance(t_automaton_defaults.name, str)
        assert isinstance(t_automaton_defaults.enabled, bool)
        assert isinstance(t_automaton_defaults.runonce, bool)
        assert isinstance(t_automaton_defaults.es_url, str)
        assert isinstance(t_automaton_defaults.es_query, dict)
        assert isinstance(t_automaton_defaults.actions, list)

    @pytest.mark.asyncio
    async def test_automaton_queryexecutor(self, t_automaton_defaults):

        with asynctest.mock.patch(
            "automaton.Automaton.QueryExecutor", side_effect=None, return_value=None
        ) as m_automaton_queryexecutor:
            await Automaton.QueryExecutor(t_automaton_defaults)
            m_automaton_queryexecutor.assert_awaited()
            m_automaton_queryexecutor.assert_called_once_with(t_automaton_defaults)
        with pytest.raises(ClientConnectorError, match=r"Cannot connect to host"):
            await Automaton.QueryExecutor(t_automaton_defaults)

    def test_automaton_responsemapper(self, t_automaton_defaults):
        t_queryresponse = {
            "aggregations": {
                "t_automaton_query": {
                    "doc_count_error_upper_bound": 0,
                    "sum_other_doc_count": 0,
                    "buckets": [{"key": "test", "doc_count": 1}],
                }
            }
        }

        assert isinstance(
            Automaton.ResponseMapper(t_automaton_defaults, t_queryresponse), list
        )
        assert isinstance(
            Automaton.ResponseMapper(t_automaton_defaults, t_queryresponse)[0]["hits"],
            int,
        )
        assert (
            "test"
            == Automaton.ResponseMapper(t_automaton_defaults, t_queryresponse)[0][
                "automaton_query"
            ]
        )
        with pytest.raises(KeyError):
            Automaton.ResponseMapper(
                t_automaton_defaults, t_queryresponse.pop("aggregations", None)
            )

    @pytest.mark.asyncio
    async def test_automaton_actionprocessor(self, t_automaton_defaults):
        t_automaton_defaults.actions[0]["executed"] = False
        t_automaton_defaults.actions[1]["executed"] = True
        with asynctest.mock.patch(
            "automaton.Automaton.ActionProcessor", side_effect=None, return_value=None
        ) as m_automaton_actionprocessor:
            await Automaton.ActionProcessor(
                t_automaton_defaults, [{"automaton_query": "test", "hits": 1}]
            )
            m_automaton_actionprocessor.assert_awaited()
            m_automaton_actionprocessor.assert_called_once_with(
                t_automaton_defaults, [{"automaton_query": "test", "hits": 1}]
            )

        with pytest.raises(asyncio.TimeoutError):
            await Automaton.ActionProcessor(
                t_automaton_defaults, [{"automaton_query": "test", "hits": 1}]
            )
        with pytest.raises(TypeError):
            await Automaton.ActionProcessor(t_automaton_defaults, None)

    @pytest.mark.asyncio
    async def test_automaton_poller(self, t_automaton_defaults):

        with asynctest.mock.patch(
            "automaton.Automaton.Poller", side_effect=None, return_value=None
        ) as m_automaton_poller:
            await Automaton.Poller(t_automaton_defaults)
            m_automaton_poller.assert_awaited()
            m_automaton_poller.assert_called_once_with(t_automaton_defaults)

        with pytest.raises(ClientConnectorError, match=r"Cannot connect to host"):
            await Automaton.Poller(t_automaton_defaults)
