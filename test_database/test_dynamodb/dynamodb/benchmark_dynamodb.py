import time
import boto3

from botocore.client import BaseClient
from botocore.exceptions import ClientError

from helpers import measure_time, parse_args


def create_dymanodb_client() -> BaseClient:
    return boto3.client(
        'dynamodb',
        region_name='us-west-2',
        endpoint_url="http://dynamodb-local:8000",
        aws_access_key_id="fakeAccessKey",
        aws_secret_access_key="fakeSecretKey"
    )


def create_table(client: BaseClient, table_name: str):
    response = client.list_tables()

    if table_name not in response['TableNames']:
        client.create_table(
            TableName=table_name,
            AttributeDefinitions=[
                {
                    'AttributeName': 'USER_ID',
                    'AttributeType': 'N'
                },
            ],
            KeySchema=[
                {
                    'AttributeName': 'USER_ID',
                    'KeyType': 'HASH'
                },
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )


def delete_table(client: BaseClient, table_name: str):
    try:
        client.delete_table(TableName=table_name)
    except ClientError:
        pass


def get_test_insert_data(iteration: int) -> list:
    data = []
    chunk_size = 25
    last_number = iteration * chunk_size

    for i in range(1, chunk_size):
        data.append(
            {
                'PutRequest': {
                    'Item': create_item(
                        user_id=last_number + i
                    )
                }
            }
        )

    return data


def get_test_update_data(iteration: int) -> dict:
    return {
        'Key': {
            'USER_ID': {
                'N': str(iteration + 1)
            }
        },
        'UpdateExpression': 'SET EVENT = :event',
        'ExpressionAttributeValues': {
            ':event': {
                'S': 'double_click'
            }
        },
    }


def create_item(user_id: int) -> dict:
    return {
        'USER_ID': {
            'N': str(user_id)
        },
        'TIMESTAMP': {
            'S': str(time.time())
        },
        'EVENT': {
            'S': 'click'
        }
    }


@measure_time('Вставка')
def run_test_insert_data(client: BaseClient, table_name: str, total: int):
    for i in range(0, int(total / 25)):
        data = get_test_insert_data(i)

        try:
            client.batch_write_item(
                RequestItems={
                    table_name: data
                }
            )
        except ClientError as e:
            print(f"Error inserting items: {e.response['Error']['Message']}")


@measure_time('Обновление')
def run_test_update_data(client: BaseClient, table_name: str, total: int):
    for iteration in range(total):
        item = get_test_update_data(iteration)
        client.update_item(
            TableName=table_name,
            Key=item['Key'],
            UpdateExpression=item['UpdateExpression'],
            ExpressionAttributeValues=item['ExpressionAttributeValues']
        )


@measure_time('Чтение')
def run_test_scan_data(client: BaseClient, table_name: str, total: int):
    client.scan(
        TableName=table_name,
        Limit=total
    )


if __name__ == '__main__':
    args = parse_args()
    table_name = 'event'
    total = args.total

    dymanodb_client = create_dymanodb_client()

    delete_table(dymanodb_client, table_name)
    create_table(dymanodb_client, table_name)

    run_test_insert_data(
        client=dymanodb_client,
        table_name=table_name,
        total=total
    )
    run_test_scan_data(
        client=dymanodb_client,
        table_name=table_name,
        total=total
    )
    run_test_update_data(
        client=dymanodb_client,
        table_name=table_name,
        total=total
    )

    delete_table(dymanodb_client, table_name)
