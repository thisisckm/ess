import boto3
import json
import os
import traceback

from botocore.exceptions import ClientError
from datetime import datetime, timedelta
from sp_api.api import Orders
from sp_api.base import Marketplaces

from system import post_message, TeamsWebhookException
from system.odoo import Odoo

SP_API_CONFIG = {
    'refresh_token': os.environ.get('REFRESH_TOKEN'),
    'lwa_app_id': os.environ.get('LWA_APP_ID'),
    'lwa_client_secret': os.environ.get('LWA_CLIENT_SECRET'),
    'aws_access_key': os.environ.get('AMAZON_AWS_ACCESS_KEY'),
    'aws_secret_key': os.environ.get('AMAZON_AWS_SECRET_KEY'),
    'sp_role_arn': os.environ.get('SP_ROLE_ARN'), # IAM Role ARN
}

TOPIC_ARN = os.environ.get('TOPIC_ARN')
IT_CHANNEL_URL = os.environ.get('IT_CHANNEL_URL')
order_api = Orders(credentials=SP_API_CONFIG, marketplace=Marketplaces.UK)
sns = boto3.client("sns")

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

def handler(event, context):
        
    message = "Fetch successfully"
    
    current_datetime = datetime.utcnow()
    two_days_ago = current_datetime - timedelta(days=2)
    two_days_ago = two_days_ago.strftime("%Y-%m-%dT%H:%M:%SZ")
    
    try:
        response = order_api.get_orders(CreatedAfter=two_days_ago, OrderStatuses=['Unshipped'])

        for row in response.payload['Orders']:
            order_id = row['AmazonOrderId']
            
            ids = odoo.search('sale.order.external', [('external_order_reference', '=', order_id)])
            if not ids:
                row['source'] = 'amazon'
                order_lines_response = order_api.get_order_items(order_id=order_id)

                lines = []
                for line in order_lines_response.payload['OrderItems']:
                    if 'BuyerInfo' in line and not line['BuyerInfo']:
                        line['BuyerInfo'] = None
                    elif 'BuyerInfo' not in line:
                        line['BuyerInfo'] = None
                    lines.append(line)
                row['lines'] = lines
                
                sns.publish(TopicArn=TOPIC_ARN, 
                    Message=json.dumps(
                        {
                            "default": row,
                            "email": f"Order {order_id} is received"
                        }), 
                    Subject="New Order",)
    except Exception as ex:
        try:
            message = traceback.format_exc()
            post_message(IT_CHANNEL_URL, message)
            raise ex
        except TeamsWebhookException as ex:
            raise ex
            
    return {'message': message}
