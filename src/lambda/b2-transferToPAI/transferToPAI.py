import time
import logging
from urllib.parse import urljoin

import requests

# Environment
RETRY_COUNT = 5
WAIT_TIME_SECONDS = 5
PDL_TABLE_NAME = "periodic_processing_x1"
AGENT_ID = "gccAgentT1"
PAI_AGENT_ID = "paiAgentT1"
API_URL = 'https://en-apigateway.research.global.fujitsu.com'
TOKEN = 'eyJhbGciOiJSUzI1NiIsImtpZCI6IjFWRURpWGtVWXZpaHFnOGRyRmU2dDBBYUhUSVVRT29Ia2t4TDhkN1EtNG8iLCJ0eXAiOiJKV1QifQ.eyJhdWQiOiI3Zjk2MTc3Yy1mZWU3LTQyYjktYTA0Ny1jZDIzZDJlZDhiM2QiLCJpc3MiOiJodHRwczovL2ZqcmVzZWFyY2hwb3J0YWwuYjJjbG9naW4uY29tL2M4ZDJmN2E4LWNhOTAtNDdhMC1hZjhlLTg4NmQ1MmM0NDRmMC92Mi4wLyIsImV4cCI6MTcyOTg2NTY2MCwibmJmIjoxNzI5Nzc5MjYwLCJ0aWQiOiJhMTlmMTIxZC04MWUxLTQ4NTgtYTlkOC03MzZlMjY3ZmQ0YzciLCJvaWQiOiJlNGFjYjIyMS0yMjM4LTQ4YWMtOTk3Ny1lODYzYjcwMmNmYzIiLCJzdWIiOiJlNGFjYjIyMS0yMjM4LTQ4YWMtOTk3Ny1lODYzYjcwMmNmYzIiLCJleHRlbnNpb25fdXNlcl9pZCI6ImU0YWNiMjIxLTIyMzgtNDhhYy05OTc3LWU4NjNiNzAyY2ZjMiIsImV4dGVuc2lvbl91c2VyX3JvbGUiOiJ1c2VyIiwiZXh0ZW5zaW9uX2FnZW50MV9pZCI6InNhbmRib3gwMDEiLCJleHRlbnNpb25fYWdlbnQxX3JvbGUiOiJhZG1pbmlzdHJhdG9yLHRzZWFsX3VzZXIiLCJleHRlbnNpb25fYWdlbnQyX2lkIjoiZ2NjQWdlbnRUMSIsImV4dGVuc2lvbl9hZ2VudDJfcm9sZSI6ImFkbWluaXN0cmF0b3IsdHNlYWxfdXNlciIsImV4dGVuc2lvbl9hZ2VudDNfaWQiOiJwYWlBZ2VudFQxIiwiZXh0ZW5zaW9uX2FnZW50M19yb2xlIjoiYWRtaW5pc3RyYXRvcix0c2VhbF91c2VyIiwiZXh0ZW5zaW9uX2FnZW50NF9pZCI6InNhbmRib3gwMDQiLCJleHRlbnNpb25fYWdlbnQ0X3JvbGUiOiJhZG1pbmlzdHJhdG9yLHRzZWFsX3VzZXIiLCJkb21haW4iOiJmdWppdHN1LmNvbSIsInRmcCI6IkIyQ18xQV9TaWduSW5fVXNlcm5hbWVfR2xvYmFsIiwic2NwIjoiYXBpIiwiYXpwIjoiN2Y5NjE3N2MtZmVlNy00MmI5LWEwNDctY2QyM2QyZWQ4YjNkIiwidmVyIjoiMS4wIiwiaWF0IjoxNzI5Nzc5MjYwfQ.SiLODq3b8jkZifutsd_Sh_5Nwvd2nhiSgoz7wqO-QAQ1PjwEOLWqUrRHp80byefmmVzSuKZWQXRgNB22tLggw8XYD4zMbEuSePDhX6NPuZBkCMuY0oAyeJx9X9acpb7k2PlC7jQcp03-LzjeyLSg6UlKZ7GVUobCsRL10nBpc3R_lwrjroSK-3wIaXOQ7aPaLUEUlXtBdE4gW4lMuGDXovLWgGm36ABI_xYFr6KSXkP1uY5ecd5_Wphey-h88wAmCDhUXSVgYNUu5Jo1wOCnSQBAuVYCVsHspogwXaqhYElx_uhi7a9BtQlpAhu_8zRwT7j6DzOMqdnsf2-FCvc6vg'
API_REQUEST_HEADERS = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {TOKEN}',
    'Trust-Agent-Id': AGENT_ID,
    'Cache-Control': 'no-cache',
}

# Logger configuration
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


def get_unsynchronized_action_ids():
    """
    Get the list of records that were not send to PAI for processing yet.
    """

    data = {
        "target": [
            {
                "table_name": PDL_TABLE_NAME,
                "column_name": "id"
            }
        ],
        "where": {
            "sync_status": ["unsynchronized"]
        }
    }

    url = urljoin(API_URL, "dataetrust/get_data")
    logger.debug(f"Sending request to {url}")
    response = requests.post(url, json=data, headers=API_REQUEST_HEADERS)

    if response.status_code == 200:
        try:
            json_response = response.json()
            logger.debug(f"Response: {json_response}")
            if json_response.get("result") != "OK" or json_response.get("detail").get("message") != "Success":
                raise Exception(
                    f"Wrong response from DeT (response={response.text})")

            rows = json_response.get("detail").get("data")
            ids = list(map(lambda r: r[0].get("value"), rows))
            logger.info(f"Found unsynchronized IDs: {ids}")
            return ids
        except ValueError:
            raise Exception(
                f"Could not parse response as JSON (response={response.text})")
    else:
        raise Exception(
            f"Request to '{url}' failed (code={response.status_code}) {response.text}")


def transfer_to_pai(ids):
    """
    Transfer specified records to PAI for futher processing.
    """

    records = list(map(lambda id: {
        "key": [
            {
                "name": "id",
                "value": id
            }
        ]
    }, ids))

    data = {
        "agent_id": [PAI_AGENT_ID],
        "data": [
            {
                "table_name": PDL_TABLE_NAME,
                "column": [
                    {
                        "name": "id"
                    },
                    {
                        "name": "uid"
                    },
                    {
                        "name": "action"
                    },
                    {
                        "name": "eco_action_performed_at"
                    },
                    {
                        "name": "quantity"
                    }
                ],
                "record": records
            }
        ]
    }

    url = urljoin(API_URL, "dataetrust/send_data")
    logger.debug(f"Sending request to {url}")
    response = requests.post(
        url, json=data, headers=API_REQUEST_HEADERS)

    if response.status_code == 200:
        try:
            json_response = response.json()
            logger.debug(f"Response: {json_response}")
            if json_response.get("result") != "OK" or json_response.get("detail").get("message") != "Success":
                raise Exception(
                    f"Wrong response from DeT (response={response.text})")
        except ValueError:
            raise Exception(
                f"Could not parse response as JSON (response={response.text})")
    else:
        raise Exception(
            f"Request to '{url}' failed (code={response.status_code}) {response.text}")

    logger.info(f"Transfered {len(ids)} IDs to PAI Agent")


def lambda_handler(event, context):
    logger.debug("transferToPAI started...")
    ids = get_unsynchronized_action_ids()

    transfer_to_pai(ids)

    for _ in range(RETRY_COUNT):
        logger.debug(
            f"Sleeping for {WAIT_TIME_SECONDS}s before checking sync status...")
        time.sleep(WAIT_TIME_SECONDS)
        if len(get_unsynchronized_action_ids()) == 0:
            logger.debug("transferToPAI done.")
            return

    raise Exception(
        f"Timeout while waiting for transfer confirmation")


lambda_handler(1, 2)
