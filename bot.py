import TelegramTextApp
from api import shops
from api.request import request
from TelegramTextApp.utils.database import SQL_request as SQL  # type: ignore


def get_cities(tta):
    keyboard = {}
    cities = shops.get_cities()
    for city in cities.get("data", []):
        keyboard[f"pos|{city['id']}"] = city["name"]
    return keyboard


def get_pos(tta):
    city_id = tta.city_id
    pos_data = shops.get_pos_info(city_id)[0]
    keyboard = {}
    if pos_data.get("video_url"):
        keyboard[f"url:{pos_data.get('video_url', '')}"] = "Подглядывать 👀"
    if keyboard:
        pos_data["keyboard"] = keyboard
    return pos_data


def get_user(tta):
    data = request("/api/aggregator/customer/", TOKEN=tta.user.token)
    return data


def check_number(tta):
    if tta.user.phone_number:
        return {"keyboard": {"authorization_check": f"+{tta.user.phone_number}"}}


def check_authorization(tta):
    data = request("/api/tg/get_token/", body={"phone": f"+{tta.user.phone_number}"})
    if data.get("token"):
        SQL(
            "UPDATE TTA SET token = ?, city_id = ? WHERE telegram_id = ?",
            (data["token"], 3, tta.user.telegram_id),
        )
        return {"keyboard": {"main": "Авторизация успешна ✅"}}


def get_categories(tta):
    data = request(f"/api/foods/?city_id={tta.user.city_id}", TOKEN=tta.user.token)
    categories = {}
    categories_emoji = {
        "Пицца 20 см": "🍕",
        "Комбо": "🍽️",
        "Пицца": "🍕",
        "Детское меню": "🍼",
        "Завтраки": "🥤",
        "Десерты": "🍰",
        "Хот-дог": "🌭",
        "Закуски": "🍿",
        "Напитки": "🍹",
        "Соусы": "🧂",
    }
    for item in data.get("data", []):
        if item["name"] in ["Скрытая категория", "Пицца 20 см", "Соусы"]:
            continue
        categories[f"shop|{item['id']}"] = f"{categories_emoji.get(item['name'], '')}"

    return categories


def get_foods(tta):
    keyboard = {}
    categories = get_categories(tta)
    keyboard.update(categories)
    if tta.category_id == "None":
        products = {"placeholder": "Выберите категорию, что бы увидеть товары"}
        keyboard.update(products)
    else:
        data = request(
            f"/api/foods/products/?city_id={tta.user.city_id}&cat_id={tta.category_id}",
            TOKEN=tta.user.token,
        )
        for idx, item in enumerate(data):
            name = item["name"]
            if idx > 0 and idx % 1 == 0:
                name = "\\" + name
            keyboard[f"product|{tta.category_id}|{item['id']}"] = (
                f"{name} - {item['price']}₽"
            )
    return keyboard


def get_product(tta):
    product_id = tta.product_id
    categories_id_emoji = {
        "15": "🍕",
        "6": "🍽️",
        "1": "🍕",
        "21": "🍼",
        "18": "🥤",
        "17": "🍰",
        "14": "🌭",
        "3": "🍿",
        "2": "🍹",
        "4": "🧂",
    }
    data = request(
        f"/api/foods/products/?city_id={tta.user.city_id}&cat_id={tta.category_id}",
        TOKEN=tta.user.token,
    )
    for item in data:
        if str(item["id"]) == str(product_id):
            if item.get("sizes"):
                keyboard = {}
                for size in item["sizes"]:
                    if str(size["size"]) == tta.size:
                        item = size["product"]
                    keyboard[
                        f"product|{tta.category_id}|{tta.product_id}|{size['size']}"
                    ] = f"{size['size']} - {size['product']['price']}₽"
                item["keyboard"] = keyboard

            item["info_KBZHU"] = "> " + item["info_KBZHU"].replace("\r\n", "\r\n> ")
            item["description"] = "> " + item["description"].replace("\r\n", "\r\n> ")
            item["name"] = (
                f"[{categories_id_emoji.get(tta.category_id, '')}]({item['img']}) "
                + item["name"]
            )
            print(item)
            return item
    return {"error": "Товар не найден"}


def check_token(tta):
    if not tta.user.token:
        return {
            "keyboard": {"authorization": "Авторизоваться 📲"},
        }


if __name__ == "__main__":
    try:
        SQL("ALTER TABLE TTA ADD COLUMN token TEXT;")
        SQL("ALTER TABLE TTA ADD COLUMN city_id INTEGER;")
    except Exception:
        pass
    TelegramTextApp.start()  # type: ignore
