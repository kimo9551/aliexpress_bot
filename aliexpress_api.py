# aliexpress_api.py

import hashlib
import time
import requests
import re

APP_KEY = '505684'
APP_SECRET = 'li42sLpysSjGfKEHteMQsrZeJjC05VJa'

def extract_product_id(url):
    # إذا الرابط مختصر من AliExpress
    if "s.click.aliexpress.com" in url:
        try:
            print(f"🔁 Resolving shortened URL: {url}")
            response = requests.get(url, allow_redirects=True, timeout=10)
            final_url = response.url
            print(f"✅ Final resolved URL: {final_url}")
            url = final_url
        except Exception as e:
            print(f"❌ Error resolving shortlink: {e}")
            return None

    # محاولة استخراج productId
    match = re.search(r'/item/(\d+)\.html', url)
    if match:
        return match.group(1)
    else:
        print(f"❌ Could not extract productId from URL: {url}")
        return None


def get_aliexpress_product_details(product_id):
    api_url = f"https://gw.api.alibaba.com/openapi/param2/2/portals.open/api.product.get/{APP_KEY}"

    params = {
        "productId": product_id,
        "fields": "productTitle,salePrice,discount,discountPrice,storeInfo,originalPrice,shippingInformation",
        "timestamp": int(time.time() * 1000)
    }

    sorted_params = ''.join(f"{k}{params[k]}" for k in sorted(params))
    sign = hashlib.md5((APP_SECRET + sorted_params + APP_SECRET).encode()).hexdigest().upper()
    params["sign"] = sign

    try:
        response = requests.get(api_url, params=params, timeout=10)
        
        # ✅ تحقق: هل الرد فعلاً JSON؟
        content_type = response.headers.get("Content-Type", "")
        if "application/json" not in content_type:
            print("🚨 الرد ليس JSON! محتوى الرد:")
            print(response.text)
            return None

        data = response.json()

        if "result" not in data or data.get("error_code"):
            return None

        result = data["result"]

        return {
            "price": result.get("originalPrice", "؟"),
            "discount_price": result.get("salePrice", "؟"),
            "super_deal_price": result.get("discountPrice", "؟"),
            "limited_offer_price": result.get("discountPrice", "؟"),
            "potential_discount_price": result.get("discountPrice", "؟"),
            "discount_percent": result.get("discount", "؟"),
            "store_name": result.get("storeInfo", {}).get("storeName", "؟"),
            "store_rating": result.get("storeInfo", {}).get("positiveRate", "؟"),
            "shipping_company": result.get("shippingInformation", {}).get("shippingCompany", "؟"),
            "shipping_fee": result.get("shippingInformation", {}).get("freight", "؟")
        }

    except Exception as e:
        print("❌ خطأ أثناء الاتصال بالـ API:", e)
        return None
