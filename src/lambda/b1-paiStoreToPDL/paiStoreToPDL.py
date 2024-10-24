# First lambda function in the batch processing sequence.
# Loads CSV data from S3 and uploads it into PDL on DeT.

import os
import sys
import logging
from urllib.parse import urljoin

import requests
import pymysql
# import boto3
# from botocore.client import Config

# Environment
PDL_TABLE_NAME = "periodic_processing_x1"
AGENT_ID = "gccAgentT1"
API_URL = 'https://en-apigateway.research.global.fujitsu.com'
TOKEN = 'eyJhbGciOiJSUzI1NiIsImtpZCI6IjFWRURpWGtVWXZpaHFnOGRyRmU2dDBBYUhUSVVRT29Ia2t4TDhkN1EtNG8iLCJ0eXAiOiJKV1QifQ.eyJhdWQiOiI3Zjk2MTc3Yy1mZWU3LTQyYjktYTA0Ny1jZDIzZDJlZDhiM2QiLCJpc3MiOiJodHRwczovL2ZqcmVzZWFyY2hwb3J0YWwuYjJjbG9naW4uY29tL2M4ZDJmN2E4LWNhOTAtNDdhMC1hZjhlLTg4NmQ1MmM0NDRmMC92Mi4wLyIsImV4cCI6MTcyOTg2NTY2MCwibmJmIjoxNzI5Nzc5MjYwLCJ0aWQiOiJhMTlmMTIxZC04MWUxLTQ4NTgtYTlkOC03MzZlMjY3ZmQ0YzciLCJvaWQiOiJlNGFjYjIyMS0yMjM4LTQ4YWMtOTk3Ny1lODYzYjcwMmNmYzIiLCJzdWIiOiJlNGFjYjIyMS0yMjM4LTQ4YWMtOTk3Ny1lODYzYjcwMmNmYzIiLCJleHRlbnNpb25fdXNlcl9pZCI6ImU0YWNiMjIxLTIyMzgtNDhhYy05OTc3LWU4NjNiNzAyY2ZjMiIsImV4dGVuc2lvbl91c2VyX3JvbGUiOiJ1c2VyIiwiZXh0ZW5zaW9uX2FnZW50MV9pZCI6InNhbmRib3gwMDEiLCJleHRlbnNpb25fYWdlbnQxX3JvbGUiOiJhZG1pbmlzdHJhdG9yLHRzZWFsX3VzZXIiLCJleHRlbnNpb25fYWdlbnQyX2lkIjoiZ2NjQWdlbnRUMSIsImV4dGVuc2lvbl9hZ2VudDJfcm9sZSI6ImFkbWluaXN0cmF0b3IsdHNlYWxfdXNlciIsImV4dGVuc2lvbl9hZ2VudDNfaWQiOiJwYWlBZ2VudFQxIiwiZXh0ZW5zaW9uX2FnZW50M19yb2xlIjoiYWRtaW5pc3RyYXRvcix0c2VhbF91c2VyIiwiZXh0ZW5zaW9uX2FnZW50NF9pZCI6InNhbmRib3gwMDQiLCJleHRlbnNpb25fYWdlbnQ0X3JvbGUiOiJhZG1pbmlzdHJhdG9yLHRzZWFsX3VzZXIiLCJkb21haW4iOiJmdWppdHN1LmNvbSIsInRmcCI6IkIyQ18xQV9TaWduSW5fVXNlcm5hbWVfR2xvYmFsIiwic2NwIjoiYXBpIiwiYXpwIjoiN2Y5NjE3N2MtZmVlNy00MmI5LWEwNDctY2QyM2QyZWQ4YjNkIiwidmVyIjoiMS4wIiwiaWF0IjoxNzI5Nzc5MjYwfQ.SiLODq3b8jkZifutsd_Sh_5Nwvd2nhiSgoz7wqO-QAQ1PjwEOLWqUrRHp80byefmmVzSuKZWQXRgNB22tLggw8XYD4zMbEuSePDhX6NPuZBkCMuY0oAyeJx9X9acpb7k2PlC7jQcp03-LzjeyLSg6UlKZ7GVUobCsRL10nBpc3R_lwrjroSK-3wIaXOQ7aPaLUEUlXtBdE4gW4lMuGDXovLWgGm36ABI_xYFr6KSXkP1uY5ecd5_Wphey-h88wAmCDhUXSVgYNUu5Jo1wOCnSQBAuVYCVsHspogwXaqhYElx_uhi7a9BtQlpAhu_8zRwT7j6DzOMqdnsf2-FCvc6vg'
DB_USER_NAME = "root"
DB_PASSWORD = "my-secret-pw"
DB_HOST = "127.0.0.1"
DB_NAME = "PaiDB"
# DB_USER_NAME = os.environ['DB_USER_NAME']
# DB_PASSWORD = os.environ['DB_PASSWORD']
# DB_HOST = os.environ['DB_HOST']
# DB_NAME = os.environ['DB_NAME']

# Logger configuration
logging.basicConfig(level=logging.DEBUG,  # Set the logging level
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# Configure DB connection (common)
try:
    dbConnection = pymysql.connect(host=DB_HOST, user=DB_USER_NAME,
                                   passwd=DB_PASSWORD, db=DB_NAME, connect_timeout=5)
except pymysql.MySQLError as e:
    logger.error(
        "Could not connect to the MySQL instance.")
    logger.error(e)
    sys.exit(1)

logger.info("Connected to the MySQL instance.")

def init_db():
    """
    Create external_service_id and external_service_linkages tables if they don't exist yet.
    Insert sample data into them.

    TODO: Remove if more production-grade way of DB init is used.
    """

    with dbConnection.cursor() as cursor:
        cursor.execute("SHOW TABLES LIKE 'external_service_linkages';")
        result = cursor.fetchone()

        if result:
            logger.info("DB already initialized.")
            return
        else:
            # Create table external_service_id
            cursor.execute("""
            CREATE TABLE external_service_id (
                id INT AUTO_INCREMENT PRIMARY KEY,
                value VARCHAR(255) NOT NULL
            );
            """)

            # Create table external_service_linkages
            cursor.execute("""
            CREATE TABLE external_service_linkages (
                id INT AUTO_INCREMENT PRIMARY KEY,
                pai_user_id VARCHAR(255) NOT NULL,
                external_service_id INT NOT NULL,
                external_service_linked_id VARCHAR(255) NOT NULL,
                is_linked BOOL NOT NULL,
                FOREIGN KEY (external_service_id) REFERENCES external_service_id(id)
            );
            """)

            # Insert initial data
            insert_external_service_id_sql = """
            INSERT INTO external_service_id (value) 
            VALUES (%s);
            """
            cursor.execute(insert_external_service_id_sql,
                           ("Green Carbon Club"))
            external_service_id = cursor.lastrowid

            insert_external_service_linkages_sql = """
            INSERT INTO external_service_linkages (pai_user_id, external_service_id, external_service_linked_id, is_linked) 
            VALUES (%s, %s, %s, %s);
            """
            cursor.execute(insert_external_service_linkages_sql, ('1234-abcd-5678',
                           external_service_id, '98765432100001200000', True))

            # Commit
            dbConnection.commit()
            logger.info("Tables created and initial data inserted.")


def register_in_pdl(uid, action, eco_action_performed_at, quantity):
    """
    Registers action data to be processed in services PDL.
    """

    data = {
        "register_type": "insert",
        "register_table": [
            {
                "table_name": PDL_TABLE_NAME,
                "data": [
                    [
                        {
                            "colname": "uid",
                            "value": uid
                        },
                        {
                            "colname": "action",
                            "value": action
                        },
                        {
                            "colname": "eco_action_performed_at",
                            "value": eco_action_performed_at
                        },
                        {
                            "colname": "quantity",
                            "value": quantity
                        }
                    ]
                ]
            }
        ]
    }

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {TOKEN}',
        'Trust-Agent-Id': AGENT_ID,
        'Cache-Control': 'no-cache',
    }

    url = urljoin(API_URL, "dataetrust/register_data")
    logger.debug(f"Sending request to {url}")
    response = requests.post(url, json=data, headers=headers)

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

    logger.info(f"Action stored in PDL")


def get_pal_user_id_for_service(external_service_linked_id):
    """
    GET pai_user_id from the DB for specified external service.
    """

    with dbConnection.cursor() as cursor:
        cursor.execute("""
        SELECT pai_user_id 
        FROM external_service_linkages 
        WHERE external_service_linked_id = %s;
        """, external_service_linked_id)

        result = cursor.fetchone()

        if result:
            return result[0]
        else:
            raise Exception(
                f"pai_user_id for service with id{external_service_linked_id} not found!")

# Initialize DB if it's not been done yet.
init_db()

def lambda_handler(event, context):
    """
    Entry point for lambda function execution
    """

    # Test S3
    # Later we will read csv files in here and parse them
    # config = Config(connect_timeout=2, retries={'max_attempts': 0})
    # s3 = boto3.client('s3', config=config)
    # response = s3.list_buckets()
    # print("response", response)

    get_pal_user_id_for_service("98765432100001200000")
    register_in_pdl(
        "1234-abcd-5678", 1, "2022-11-17 13:31:31", 2)
    return "All done."


lambda_handler(1, 1)
