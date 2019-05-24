[![Codeship Status for jgericke/automaton](https://app.codeship.com/projects/d8f9a710-6020-0137-cdfe-427ad6051c19/status?branch=master)](https://app.codeship.com/projects/343973) [!Docs](https://readthedocs.com/projects/lsd-automaton/badge/?version=latest) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) 
[![Code style](https://img.shields.io/badge/code%20style-black-000000.svg)

# Automaton
__Simple, Event-driven Automation in Python__

Automaton makes use of Elasticsearch as a general data aggregation layer. You feed your Automaton(s) queries
via environment variables (formatted in JSON). Based on the query result, you can chain actions together which
Automaton will act on, passing query metadata off to action handlers and generally having a good time.

Basically Automaton is ***all*** about the following:

1. Query Elasticsearch on a defined schedule
2. Upon receiving a query response, execute defined actions and wait for a defined backoff period
3. Return to querying
4. ???
5. Profit!

## Current Actions 

* `notify` - Send a Rocket Chat webhook.
* `awx` - Calls an Ansible AWX API endpoint.

## Example Workflow

    1. Create an Elasticsearch query to read the number of orders being processed (assuming you have some sort of order system thats sending metrics to Elasticsearch...)
    2. Create an Ansible AWX job template to scale up pods running in Kubernetes based (using say, extra_parameters or something)
    3. Create an Automaton that runs the above query, with an action to call the AWX job template based on query result
    4. Good gravy, your pods are scaling on a transactional metric!

## Automaton Features

* Runs on python 3.7
* Fully asynchronous.
* Extendable (actions are functions created under automaton/actions).
* Not your Grandad's Automaton.

## Adding Actions to Automaton

* Create a new action file: automaton/actions/my_action.py
* Actions are defined as a list within your `automaton` environment variable, and can be chained, for example the below action fires off a rocket chat webhook (this forms part of your AUTOMATON_CONFIG environment variable):

```
"automaton_actions": [
    {
        "action_name": "notify.rocketchat_webhook",
        "action_backoff_seconds": 300, 
        "action_parameters": {
            "rocketchat_webhook": "https://my.rocketchat/hooks/my_webhook_id",
            "rocketchat_message": "@here Things are happening!\nView dashboard: https://my.kibana/goto/my_dashboard_id",
            "rocketchat_timeout": 20
        }
    }
]
```

* When adding or extending an action, you need to make Automaton aware of the new action by adding it to automaton/automaton.py within the action_dispatcher (This will be simplified in the future). The below represents the action file and function name for ```actions/notify.py```.

```
action_dispatcher = {
    "notify.rocketchat_webhook": notify.rocketchat_webhook 
}
```

## Creating An Automaton

You can launch Automaton by defining the AUTOMATON_CONFIG environment variable, which has an expected structure as outlined below. When you're good to go, you can execute bin/auto.py which will gather all of the automatons you've defined and run them through the execution chain.

Have a look at samples provided (```samples/```) to get a feel for scaffolding Automatons

```
export AUTOMATON_LOGLEVEL='DEBUG'
export AUTOMATON_CONFIG='{ 
    "automatons": [
        {
            "automaton_name": "my_neat_automaton",
            "automaton_enabled": True,
            "automaton_runonce": False,
            "elasticsearch_url": "http://my.elasticsearch:9200",
            "elasticsearch_timeout": 10,
            "elasticsearch_query": {
                "query_interval": 5,
                "query_endpoint": "/_search",
                "query_type": "aggregations",
                "query_name": "my_automaton_query",
                "query_payload": {
						"size": 0,
						"query": {
						    "range": {
                                "@timestamp": {
                                    "gte": "now-1m"
                                }
                            }
						},
						"aggregations": {
						    "bad_actors": {
                                "terms": {
                                    "field": "my_automaton_query.keyword",
                                    "min_doc_count": 1000
                                }
						    }
						}
                },
                "query_response_mapping": { 
                        "key": "go_automaton_go", 
                        "doc_count": "hits"
                }
            },
            "automaton_actions": [
                {
                    "action_name": "notify.rocketchat_webhook",
                    "action_backoff_seconds": 60,
                    "action_parameters": {
                        "rocketchat_webhook": "https://my.rocketchat/hooks/my_webhook_id",
                        "rocketchat_message": "@here Things are happening, Imma do stuff!",
                        "rocketchat_timeout": 10
                    }
                },
                {
                    "action_name": "awx.api_call",
                    "action_backoff_seconds": 60,
                    "action_parameters": {
                        "awx_url": "https://my.awx.url",
                        "awx_context": "/api/v2/job_templates/1/launch/",
                        "awx_timeout": 20,
                        "awx_auth": {
                            "username": "YXV0b21hdG9u",
                            "password": "ZDY5VG5vZUdZYjdU"
                        }
                    }
                }
            ]
        }
    ]
}'
```



#### Original Author(s)

###### Julian Gericke
###### (c) LSD
###### [julian@lsd.co.za](mailto:julian@lsd.co.za)
###### [Checkout LSD, your friendly OSS DevOps company!](https://lsd.co.za "LSD Homepage")

#### Contributors

- Maybe you?!
