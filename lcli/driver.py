import requests


class LocustPageDriver:
    def __init__(self, host: str = None, timeout: int = 5):
        self.host = host
        self.timeout = timeout
        self.headers = {"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"}

    def locust_index(self):
        url = self.host
        response = requests.get(url=url, headers=self.headers, timeout=self.timeout)
        if response.status_code == 200:
            return response.content

        if response:
            raise RuntimeError(
                f"Error occurred while retrieving locust stats: status_code[{response.status_code}], body:\n{response.content}"
            )

        raise RuntimeError("Request returned a null response")
