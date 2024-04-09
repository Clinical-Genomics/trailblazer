import requests


class OrderAPIClient:
    def __init__(self, base_url: str):
        self.base_url = base_url

    def update_order_status(self, delivered_analyses: int, order_id: int) -> None:
        endpoint = f"{self.base_url}/orders/{order_id}/update-delivery-status"
        payload = {"delivered_analyses": delivered_analyses}
        requests.post(endpoint, json=payload)
