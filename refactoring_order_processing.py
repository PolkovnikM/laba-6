TAX_RATE = 0.21

DISCOUNT_RATES = {
    "SAVE10": 0.10,
    "SAVE20": 0.20,  # для заказов >= 200
    "SAVE20_MIN": 0.05,  # для заказов < 200
    "VIP": 50,
    "VIP_MIN": 10,
}

VIP_THRESHOLD = 100
SAVE20_THRESHOLD = 200
DEFAULT_CURRENCY = "USD"


def parse_request(request: dict) -> tuple:
    user_id = request.get("user_id")
    items = request.get("items")
    coupon = request.get("coupon")
    currency = request.get("currency")

    return user_id, items, coupon, currency


def validate_request(user_id, items, currency):
    if user_id is None:
        raise ValueError("user_id is required")

    if items is None:
        raise ValueError("items is required")

    if not isinstance(items, list):
        raise ValueError("items must be a list")

    if len(items) == 0:
        raise ValueError("items must not be empty")

    for item in items:
        validate_item(item)

    if currency is None:
        currency = DEFAULT_CURRENCY

    return currency


def validate_item(item: dict):
    if "price" not in item or "qty" not in item:
        raise ValueError("item must have price and qty")

    if item["price"] <= 0:
        raise ValueError("price must be positive")

    if item["qty"] <= 0:
        raise ValueError("qty must be positive")


def calculate_subtotal(items: list) -> int:
    subtotal = 0
    for item in items:
        subtotal += item["price"] * item["qty"]
    return subtotal


def calculate_discount(coupon: str, subtotal: int) -> int:

    if not coupon or coupon == "":
        return 0

    if coupon == "SAVE10":
        return int(subtotal * DISCOUNT_RATES["SAVE10"])

    elif coupon == "SAVE20":
        if subtotal >= SAVE20_THRESHOLD:
            return int(subtotal * DISCOUNT_RATES["SAVE20"])
        else:
            return int(subtotal * DISCOUNT_RATES["SAVE20_MIN"])

    elif coupon == "VIP":
        if subtotal >= VIP_THRESHOLD:
            return DISCOUNT_RATES["VIP"]
        else:
            return DISCOUNT_RATES["VIP_MIN"]

    else:
        raise ValueError("unknown coupon")


def calculate_tax(amount: int) -> int:

    return int(amount * TAX_RATE)


def generate_order_id(user_id, items_count: int) -> str:

    return f"{user_id}-{items_count}-X"


def process_checkout(request: dict) -> dict:
    user_id, items, coupon, currency = parse_request(request)

    currency = validate_request(user_id, items, currency)

    subtotal = calculate_subtotal(items)

    discount = calculate_discount(coupon, subtotal)

    total_after_discount = subtotal - discount
    if total_after_discount < 0:
        total_after_discount = 0

    tax = calculate_tax(total_after_discount)

    total = total_after_discount + tax

    order_id = generate_order_id(user_id, len(items))

    return {
        "order_id": order_id,
        "user_id": user_id,
        "currency": currency,
        "subtotal": subtotal,
        "discount": discount,
        "tax": tax,
        "total": total,
        "items_count": len(items),
    }
