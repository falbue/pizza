import requests

def request(
    command="", body: bool | dict | None = None, TOKEN="", localize="ru"
) -> dict:
    """ "Отправляет запрос к API api.pizza.newiris.ru"""
    if command.startswith("/"):
        command = command[1:]

    if body:
        if body is True:
            response = requests.post(
                f"https://api.pizza.newiris.ru/{command}",
                headers={"x-token": TOKEN},
            )
        else:
            response = requests.post(
                f"https://api.pizza.newiris.ru/{command}",
                headers={"x-token": TOKEN},
                json=body,
            )
    else:
        response = requests.get(
            f"https://api.pizza.newiris.ru/{command}",
            headers={"x-token": TOKEN},
        )

    data = response.json()
    return data
