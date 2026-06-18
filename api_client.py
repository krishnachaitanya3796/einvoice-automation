import requests
import time


class TaxillaAPI:
    def __init__(self, config):
        self.base_url = config["base_url"]
        self.token_endpoint = config["token_endpoint"]
        self.post_endpoint = config["post_endpoint"]
        self.report_endpoint = config["report_endpoint"]
        self.client_id = config["client_id"]
        self.client_secret = config["client_secret"]
        self.financial_year = config["financial_year"]
        self.transformation_name = config["transformation_name"]

    def get_token(self):
        url = self.base_url + self.token_endpoint

        response = requests.post(
            url,
            auth=(self.client_id, self.client_secret),
            data={
                "grant_type": "client_credentials"
            }
        )

        return response.json()["access_token"]

    def post_invoice(self, token, payload):
        url = self.base_url + self.post_endpoint

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        params = {
            "autoExecuteRules": "true",
            "transformationName": self.transformation_name
        }

        response = requests.post(
            url,
            headers=headers,
            params=params,
            json=payload
        )

        return response.json()

    def get_report(self, token, reference_number, invoice_type_code):
        url = self.base_url + self.report_endpoint

        headers = {
            "Authorization": f"Bearer {token}"
        }

        params = {
            "referencenumber": reference_number,
            "InvoiceTypeCode": invoice_type_code,
            "financialyear": self.financial_year
        }

        max_retries = 10

        for attempt in range(max_retries):
            response = requests.get(
                url,
                headers=headers,
                params=params
            )

            report_json = response.json()

            if report_json.get("taxillaErrorCode") == "INSTANCE_INPROGRESS":
                print(f"Waiting... Attempt {attempt + 1}")
                time.sleep(5)
                continue

            return report_json

        return report_json