import boto3
import json
import os
import traceback
import re

from pycountry import countries
from datetime import datetime

from system import post_message, TeamsWebhookException

TOPIC_ARN = os.environ.get('TOPIC_ARN')
IT_CHANNEL_URL = os.environ['IT_CHANNEL_URL']

sns = boto3.client("sns")

def pre_processor_amazon(data: dict) -> str:
    
    ext_order = {}
    external_order_reference = None
    try:    
        ext_order['raw_response'] = str(data)
        external_order_reference = data['AmazonOrderId']
        ext_order['external_channel_id'] = 'amazon'
        ext_order['ebay_order_id'] = ext_order['external_order_reference'] = external_order_reference
        
        if 'BuyerInfo' in data and data['BuyerInfo'] and 'BuyerEmail' in data['BuyerInfo']:
            ext_order['external_order_user_id'] = data['BuyerInfo']['BuyerEmail']
        
        purchase_date = data['PurchaseDate']
        ext_order['external_order_date'] = purchase_date
        
        try:
            purchase_date = datetime.strptime(purchase_date, "%Y-%m-%dT%H:%M:%S.%fZ")
        except:
            purchase_date = datetime.strptime(purchase_date, "%Y-%m-%dT%H:%M:%SZ")
        
        ext_order['external_order_date_only'] = purchase_date.strftime("%d %b %Y")
        
        shipping_address = data['ShippingAddress']
        
        if 'Name'in shipping_address:
            ext_order['external_customer_name'] = ext_order['external_customer_delivery_name'] = shipping_address['Name']
        else:
            ext_order['state'] = 'exception'
            
        if 'AddressLine1' in shipping_address:
            ext_order['external_customer_street1'] = ext_order['external_customer_delivery_street1'] = shipping_address['AddressLine1']
        
        if 'AddressLine2' in shipping_address:
            ext_order['external_customer_street2'] = ext_order['external_customer_delivery_street2'] = shipping_address['AddressLine2']
        
        ext_order['external_customer_city'] = ext_order['external_customer_delivery_city'] = shipping_address['City']
        
        if 'StateOrRegion' in shipping_address:
            ext_order['external_customer_state'] = ext_order['external_customer_delivery_state'] = shipping_address['StateOrRegion']
        
        ext_order['external_customer_state_zip'] = ext_order['external_customer_delivery_state_zip'] = re.sub(r"[^a-zA-Z0-9]+", ' ', shipping_address['PostalCode'])
        ext_order['external_customer_country'] = ext_order['external_customer_delivery_country'] = countries.get(alpha_2=shipping_address['CountryCode']).name

        ext_order['external_order_payment_currency'] = data['OrderTotal']['CurrencyCode']
        ext_order['external_order_payment_method'] = data['PaymentMethod']
        ext_order['external_order_payment_details'] = data['AmazonOrderId']
        ext_order['external_order_total_amount'] = data['OrderTotal']['Amount']

        ext_order['external_order_recevied_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ext_order['external_customer_new'] = True
        ext_order['external_customer_contact_new'] = True
        ext_order['external_order_state'] = data['OrderStatus']
        ext_order['amazon_fulfillment_channel'] = data['FulfillmentChannel']
        ext_order['external_order_delivery_carrier'] = data['ShipServiceLevel']

        order_lines = []
        
        for line in data['lines']:
                    
            shipping_price = 0.0
            ext_line_vals = {}
            
            try:
                ext_line_vals['external_product_code'] = line['SellerSKU']
                ext_line_vals['external_product_name'] = line['Title']
                ext_line_vals['external_product_qty'] = int(line['QuantityOrdered'])
                ext_line_vals['external_product_tax_precentage'] = 20.00
                ext_line_vals['external_product_sub_total'] = float(line['ItemPrice']['Amount'])
                ext_line_vals['external_sale_order_id'] = None

                if 'ShippingPrice' in line:
                    shipping_price += (float(line['ShippingPrice']['Amount']) - float(line['ShippingDiscount']['Amount']))
                
                order_lines.append(ext_line_vals)
                    
            except Exception as ex:
                message = traceback.format_exc()
                post_message(IT_CHANNEL_URL, message)
                ext_order['state'] = 'exception'
        
            if shipping_price:
                ext_order['external_order_delivery_charge'] = shipping_price

        ext_order['order_lines'] = order_lines
    except Exception as ex:
        message = traceback.format_exc()
        post_message(IT_CHANNEL_URL, message)
        ext_order['state'] = 'exception'
        
    return external_order_reference, ext_order

def handler(event, context):
        
    message = "Pre-Order process successfully done"
    
    for record in event['Records']:
        sns_message = record['Sns']['Message']
        if isinstance(sns_message, dict):
            data = sns_message['default']
        else:
            data = json.loads(sns_message)
            data = data['default']
        del sns_message
        
        data_source = data['source']
        if data_source == 'amazon':
            external_order_reference, processed_order = pre_processor_amazon(data)
        elif data_source == 'ebay':
            raise Exception('eBay: Not yet implemented')
        else:
            raise Exception('Unknow source')
    
        sns.publish(TopicArn=TOPIC_ARN, 
                    Message=json.dumps(
                        {
                            "default": processed_order,
                            "email": f"Order {external_order_reference} "
                            f"is received from {data_source} source"
                        }), 
                    Subject="New Order",)
                
    
    return {'message': message}
