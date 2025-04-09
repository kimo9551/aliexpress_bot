# aliexpress_api.py

import hashlib
import time
import requests
import re

APP_KEY = '505684'
APP_SECRET = 'li42sLpysSjGfKEHteMQsrZeJjC05VJa'

def extract_product_id(url):
    match = re.search(r'/item/(\d+)\.html', url)
    if match:
        return match.group(1)
    return None

def get_aliexpress_product_details(product_id):
    api_name = "api.getPromotionProductDetail"
    base_url = f"https://api-gw.aliexpress.com/openapi/param2/2/portals.open/{api_name}/{APP_KEY}"
    
    timestamp = int(time.time() * 1000)
    params = {
        "app_key": APP_KEY,
        "productId": product_id,
        "timestamp": timestamp,
        "sign_method": "md5"
    }

    sign_str = APP_SECRET + ''.join(f"{k}{params[k]}" for k in sorted(params)) + APP_SECRET
    params["sign"] = hashlib.md5(sign_str.encode('utf-8')).hexdigest().upper()

    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        return None
