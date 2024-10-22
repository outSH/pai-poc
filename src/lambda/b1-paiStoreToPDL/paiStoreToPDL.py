import sys
import logging
import pymysql
from botocore.client import Config
import boto3
# import json
import os

# rds settings
user_name = os.environ['USER_NAME']
password = os.environ['PASSWORD']
rds_host = os.environ['RDS_HOST']
db_name = os.environ['DB_NAME']

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# create the database connection outside of the handler to allow connections to be
# re-used by subsequent function invocations.
try:
    conn = pymysql.connect(host=rds_host, user=user_name,
                           passwd=password, db=db_name, connect_timeout=5)
except pymysql.MySQLError as e:
    logger.error(
        "ERROR: Unexpected error: Could not connect to MySQL instance.")
    logger.error(e)
    sys.exit(1)

logger.info("SUCCESS: Connection to RDS for MySQL instance succeeded")


bucket_name = 'pai-poc-service-input0044'

# TODO - Move to separate one-time lambda.


def init_db():
    with conn.cursor() as cursor:
        cursor.execute("SHOW TABLES LIKE 'external_service_linkages';")
        result = cursor.fetchone()

        if result:
            print("Table already exists.")
            return
        else:

            create_table_query = """
            CREATE TABLE external_service_linkages (
                id INT AUTO_INCREMENT PRIMARY KEY,
                pai_user_id VARCHAR(255) NOT NULL,
                external_service_id INT NOT NULL,
                external_service_linked_id VARCHAR(255) NOT NULL,
                is_linked BOOL NOT NULL
            );
            """
            cursor.execute(create_table_query)

            # Insert initial data
            insert_data_query = """
            INSERT INTO external_service_linkages (pai_user_id, external_service_id, external_service_linked_id, is_linked) 
            VALUES 
            ('1234-abcd-5678', 1, '98765432100001200000', true);
            """

            cursor.execute(insert_data_query)
            conn.commit()
            print("Table created and initial data inserted.")


def lambda_handler(event, context):
    init_db()
    
    config = Config(connect_timeout=2, retries={'max_attempts': 0})
    s3 = boto3.client('s3', config=config)
    response = s3.list_buckets()
    print("response", response)
    return "All done."
