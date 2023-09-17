import requests
import json
import os
import boto3

from botocore.exceptions import ClientError
from system import post_message
from system.odoo import Odoo


IT_CHANNEL_URL = os.environ.get('IT_CHANNEL_URL')
AMAZON_ORDER_SOURCE_ID = os.environ.get('AMAZON_ORDER_SOURCE_ID')
AMAZON_ORDER_SOURCE_ID = int(AMAZON_ORDER_SOURCE_ID)

def get_secret():

    secret_name = "prod/erp-uk/"
    
    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(service_name='secretsmanager')
    
    try:
    
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name)
    
        # Decrypts secret using the associated KMS key.
        secret = get_secret_value_response['SecretString']
        return json.loads(secret)
    
    except ClientError as e:
        message = traceback.format_exc()
        post_message(IT_CHANNEL_URL, message)
        return {}
    except Exception as e:
        message = traceback.format_exc()
        post_message(IT_CHANNEL_URL, message)
        return {}

erp_credential = get_secret()

url = os.environ.get('ERP_API_URL', None)
url = url if url else erp_credential.get('api_url') 
db = os.environ.get('ERP_DB', None)
db = db if db else erp_credential.get('db')
username = os.environ.get('ERP_USERNAME', None)
username = username if username else erp_credential.get('username')
password = os.environ.get('ERP_PASSWORD', None)
password = password if password else erp_credential.get('password')

odoo = Odoo(url, db, username, password)


def process_amazon(data: dict):
    
    order_ref = data['external_order_reference']
    
    ids = odoo.search('sale.order.external', [('external_order_reference', '=', order_ref)])

    if not ids:
        data['external_channel_id'] = AMAZON_ORDER_SOURCE_ID
        
        order_lines = data['order_lines']
        
        del data['order_lines']
        
        order_id = odoo.create('sale.order.external', data)
        
        for line in order_lines:
            line['external_sale_order_id'] = order_id
            odoo.create('sale.order.line.external', line)


def handler(event, context):
    
    message = "Order process successfully done"        
    
    for record in event['Records']:
        sns_message = record['Sns']['Message']
        if isinstance(sns_message, dict):
            data = sns_message['default']
        else:
            data = json.loads(sns_message)
            data = data['default']
        del sns_message
        
        data_source = data['external_channel_id']
        
        if data_source == 'amazon':
            process_amazon(data)
        elif data_source == 'ebay':
            raise Exception('eBay: Not yet implemented')
        else:
            raise Exception('Unknow source')
        
    return {'message': message}
    