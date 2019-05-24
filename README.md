# ![Automaton](docs/logo.png?raw=true "Automaton") Automaton

Demonstrating event-based automation using Elasticsearch and Ansible

### Build

python setup.py [develop|build]

### Usage

Define relevant environment variables as per the below:

```
export AUTOMATON_LOGLEVEL='DEBUG'
export AUTOMATON_CONFIG='{ "automatons": [
                                {
                                    "automaton_name": "security",
                                    "elasticsearch_url": "http://your_elasticsearch.url",
                                    "elasticsearch_timeout": 10,
                                    "elasticsearch_query": {
                                        "query_interval": 5,
                                        "query_endpoint": "/_search",
                                        "query_type": "aggregation",
                                        "query_name": "your_query_name",
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
							"field": "red_src.keyword",
							"min_doc_count": 1
						    }
						    }
						}
					    },
                                        "query_response_mapping": {
                                              "key": "bad_actor",
                                              "doc_count": "hits"
                                        }

                                    },
                                    "automaton_actions": [
                                        {
                                            "action_name": "notify.rocketchat_webhook",
                                            "action_parameters": {
                                               "rocketchat_webhook": "https://your_rocketchat_webhook.url",
                                               "rocketchat_message": "Alert: your alert message",
                                               "rocketchat_timeout": 10
                                            }
                                        },
                                        {
                                            "action_name": "awx.api_call",
                                            "action_parameters": {
                                               "awx_url": "https://your_awx.url",
                                               "awx_context": "/path/to/your/awx/job_template",
                                               "awx_timeout": 20,
                                               "awx_auth": {
                                                  "username": "username.b64",
                                                  "password": "passwd.b64"
                                               }
                                            }
                                        }
                                    ]
                                }
                            ]
                        }'

$ python auto.py

```

### Notes

None as of yet

### Author
###### LSD Information Technology
2018
 
