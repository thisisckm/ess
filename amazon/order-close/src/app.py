import os
import json
import traceback
import requests

from datetime import datetime
from sp_api.api import Orders
from sp_api.base import Marketplaces

from system import post_message

# Set up API credentials
SP_API_CONFIG = {
    'refresh_token': os.environ.get('REFRESH_TOKEN'),
    'lwa_app_id': os.environ.get('LWA_APP_ID'),
    'lwa_client_secret': os.environ.get('LWA_CLIENT_SECRET'),
    'aws_access_key': os.environ.get('AMAZON_AWS_ACCESS_KEY'),
    'aws_secret_key': os.environ.get('AMAZON_AWS_SECRET_KEY'),
    'sp_role_arn': os.environ.get('SP_ROLE_ARN'), # IAM Role ARN
}


IT_CHANNEL_URL = os.environ.get('IT_CHANNEL_URL')
MARKETPLACE_ID = os.environ.get('MARKETPLACE_ID')
order_api = Orders(credentials=SP_API_CONFIG, marketplace=Marketplaces.UK)

def handler(event, context):

    message = "Close Order successfully"
    
    for record in event['Records']:
        sns_message = record['Sns']['Message']
        if isinstance(sns_message, dict):
            data = sns_message['default']
        else:
            data = json.loads(sns_message)
            data = data['default']
        del sns_message

        shipped_on = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")    

        # SP API call to close the order
        try:
            response = order_api.confirm_shipment(order_id=data['order_id'], 
                                                marketplaceId=MARKETPLACE_ID, 
                                                packageDetail={
                                                    'packageReferenceId': 1,
                                                    'carrierCode': data['carrier'], 
                                                    'shippingMethod': data['carrier_service'], 
                                                    'trackingNumber': data['carrier_tracker_ref'], 
                                                    'shipDate': shipped_on,
                                                    'orderItems': data['orderItems']
                                                })
            
        except requests.exceptions.JSONDecodeError as ex:
            print(ex.__class__)
        except Exception as ex:
            message = traceback.format_exc()
            post_message(IT_CHANNEL_URL, message)

    return {'message': message}
