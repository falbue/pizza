from .request import request


def get_cities():
    """Получает список городов с API"""
    return request(command="/api/cities/")


def get_pos_info(city_id):
    """Получает информацию о городе по его ID с API"""
    return request(command=f"/api/aggregator/points_of_sale/?city_id={city_id}")
