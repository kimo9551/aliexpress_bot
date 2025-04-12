import re
import requests
import hashlib
import time
import urllib.parse

# AliExpress API credentials
APP_KEY = '505684'
APP_SECRET = 'li42sLpysSjGfKEHteMQsrZeJjC05VJa'

# استخراج productId من الرابط (حتى المختصر)
def extract_product_id(url):
    # حل الرابط المختصر إن وجد
    if "s.click.aliexpress.com" in url:
        try:
            response = requests.get(url, allow_redirects=True, timeout=5)
            url = response.url
        except:
            return None

    # استخراج productId من الرابط الطويل
    match = re.search(r'/item/(\d+)\.html', url)
    if match:
        return match.group(1)
    return None

# جلب بيانات المنتج من AliExpress API
def get_product_details(product_id):
    api_url = f"https://gw.api.alibaba.com/openapi/param2/2/portals.open/api.product.get/{APP_KEY}"

    params = {
        "productId": product_id,
        "fields": "productTitle,salePrice,discount,discountPrice,storeInfo,originalPrice,shippingInformation",
        "timestamp": int(time.time() * 1000)
    }

    # توليد توقيع التحقق
    sorted_params = ''.join(f"{k}{params[k]}" for k in sorted(params))
    sign = hashlib.md5((APP_SECRET + sorted_params + APP_SECRET).encode()).hexdigest().upper()
    params["sign"] = sign

    try:
        response = requests.get(api_url, params=params, timeout=10)

        # تأكد أن الرد JSON
        if "application/json" not in response.headers.get("Content-Type", ""):
            print("❌ الرد ليس JSON:\n", response.text)
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
        print("❌ API error:", e)
        return None

# تنسيق الرد باللغة العربية
def format_product_reply(details):
    return f"""📣 سعر المنتج بدون تخفيض: {details['price']}$
💵 سعر التخفيض بالعملات: {details['discount_price']}$
💵 سعر السوبر ديلز: {details['super_deal_price']}$
💵 سعر العرض المحدود: {details['limited_offer_price']}$
💵 سعر التخفيض المحتمل: {details['potential_discount_price']}$

🛍 نسبة التخفيض بالعملات: {details['discount_percent']}
🏪 إسم المتجر: {details['store_name']}
🌟 التقييم الإيجابي للمتجر: {details['store_rating']}%
✈️ شركة الشحن: {details['shipping_company']}
✈️ عمولة الشحن: {details['shipping_fee']}$"""
