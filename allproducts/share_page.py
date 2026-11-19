from html import escape
from urllib.parse import quote

from django.http import HttpResponse, JsonResponse

from .views import MODEL_MAPPING, get_product_variants_list

PACKAGE_ID = "com. herokuapp.aswaqmozhela"
PLAY_STORE = (
    "https://play.google.com/store/apps/details?id=" + quote(PACKAGE_ID)
)


def _image(request, field):
    if not field:
        return ""
    url = field.url
    if url.startswith("http://") or url.startswith("https://"):
        return url
    return request.build_absolute_uri(url)


def _product(model_name, product_id):
    model = MODEL_MAPPING.get(model_name)
    if model is None:
        return None
    return model.objects.filter(id=product_id, is_active=True).first()


def _payload(request, product):
    return {
        "id": product.id,
        "name": product.name,
        "model_name": product.model_name,
        "price": float(product.price),
        "original_price": float(product.original_price),
        "discount_percentage": float(product.discount_percentage),
        "primary_image": _image(request, product.primary_image),
        "secondary_image1": _image(request, product.secondary_image1),
        "secondary_image2": _image(request, product.secondary_image2),
        "description": product.description or "",
        "stock": product.stock,
        "is_active": product.is_active,
        "is_available": product.is_available,
        "variants": get_product_variants_list(product, request),
    }


def share_product_json(request, model_name, product_id):
    product = _product(model_name, product_id)
    if product is None:
        return JsonResponse({"error": "Product not found"}, status=404)
    return JsonResponse(_payload(request, product))


def share_product_page(request, model_name, product_id):
    product = _product(model_name, product_id)
    if product is None:
        html = _page(
            title="أسواق مذهلة",
            description="المنتج غير متاح",
            image="",
            price="",
            old_price="",
            discount="",
            app_link=PLAY_STORE,
            page_url=request.build_absolute_uri(),
            missing=True,
        )
        return HttpResponse(html, status=404, content_type="text/html; charset=utf-8")

    data = _payload(request, product)
    price = f"{data['price']:.2f} L.E"
    old_price = ""
    discount = ""
    if data["discount_percentage"] > 0:
        old_price = f"{data['original_price']:.2f} L.E"
        discount = f"-{data['discount_percentage']:.0f}%"
    description = (data["description"] or data["name"])[:180]
    app_link = f"aswaq://product/{quote(product.model_name)}/{product.id}"
    html = _page(
        title=data["name"],
        description=description,
        image=data["primary_image"],
        price=price,
        old_price=old_price,
        discount=discount,
        app_link=app_link,
        page_url=request.build_absolute_uri(),
        missing=False,
    )
    return HttpResponse(html, content_type="text/html; charset=utf-8")


def _page(title, description, image, price, old_price, discount, app_link, page_url, missing):
    safe_title = escape(title)
    safe_description = escape(description)
    safe_image = escape(image)
    safe_price = escape(price)
    safe_old = escape(old_price)
    safe_discount = escape(discount)
    safe_app = escape(app_link)
    safe_page = escape(page_url)
    safe_store = escape(PLAY_STORE)
    image_block = (
        f'<img src="{safe_image}" alt="{safe_title}">'
        if image
        else '<div class="placeholder">أسواق مذهلة</div>'
    )
    discount_block = f'<span class="off">{safe_discount}</span>' if discount else ""
    old_block = f'<span class="old">{safe_old}</span>' if old_price else ""
    body = (
        f"""
        {image_block}
        <div class="sheet">
          <p class="brand">أسواق مذهلة</p>
          <h1>{safe_title}</h1>
          <p class="price">{safe_price} {old_block} {discount_block}</p>
          <p class="desc">{safe_description}</p>
          <a class="open" id="open-app" href="{safe_app}">فتح المنتج في التطبيق</a>
          <a class="store" href="{safe_store}">تحميل التطبيق من جوجل بلاي</a>
        </div>
        """
        if not missing
        else """
        <div class="sheet">
          <p class="brand">أسواق مذهلة</p>
          <h1>المنتج غير متاح</h1>
          <a class="store" href="%s">تحميل التطبيق</a>
        </div>
        """
        % safe_store
    )
    return f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{safe_title}</title>
  <meta name="description" content="{safe_description}">
  <meta property="og:type" content="product">
  <meta property="og:site_name" content="أسواق مذهلة">
  <meta property="og:title" content="{safe_title}">
  <meta property="og:description" content="{safe_description}">
  <meta property="og:url" content="{safe_page}">
  <meta property="og:image" content="{safe_image}">
  <meta property="og:image:alt" content="{safe_title}">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{safe_title}">
  <meta name="twitter:description" content="{safe_description}">
  <meta name="twitter:image" content="{safe_image}">
  <style>
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; font-family: Tahoma, Arial, sans-serif; background: #f4f7f8; color: #102027; }}
    img {{ width: 100%; max-height: 420px; object-fit: cover; background: #fff; display: block; }}
    .placeholder {{ height: 220px; display: grid; place-items: center; background: #073b4c; color: white; font-weight: 800; }}
    .sheet {{ margin: -28px 16px 32px; padding: 22px 18px; background: white; border-radius: 22px; box-shadow: 0 12px 30px rgba(7,59,76,.08); }}
    .brand {{ margin: 0; color: #5f7a84; font-size: 13px; font-weight: 700; }}
    h1 {{ margin: 8px 0; font-size: 24px; line-height: 1.35; }}
    .price {{ font-size: 22px; font-weight: 800; margin: 8px 0; }}
    .old {{ color: #90a4ae; text-decoration: line-through; font-size: 14px; font-weight: 600; margin-right: 8px; }}
    .off {{ background: #e11d48; color: white; border-radius: 8px; padding: 2px 8px; font-size: 13px; }}
    .desc {{ color: #546e7a; line-height: 1.6; }}
    a {{ display: block; text-align: center; text-decoration: none; border-radius: 14px; padding: 14px; font-weight: 800; margin-top: 10px; }}
    .open {{ background: #073b4c; color: white; }}
    .store {{ background: #e8f4f7; color: #073b4c; }}
  </style>
</head>
<body>
  {body}
  <script>
    var open = document.getElementById('open-app');
    if (open) {{
      open.addEventListener('click', function (event) {{
        event.preventDefault();
        var started = Date.now();
        window.location = open.getAttribute('href');
        setTimeout(function () {{
          if (Date.now() - started < 1600) window.location = '{safe_store}';
        }}, 1200);
      }});
    }}
  </script>
</body>
</html>"""
