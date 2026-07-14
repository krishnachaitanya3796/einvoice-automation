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

    # -----------------------------------
    # OAuth Token
    # -----------------------------------
    def get_token(self):
        url = self.base_url + self.token_endpoint
        
        response = requests.post(
            url,
            auth=(self.client_id, self.client_secret),
            data={"grant_type": "client_credentials"}
        )
        response.raise_for_status()
        
        return response.json()["access_token"]

    # -----------------------------------
    # Submit Invoice
    # -----------------------------------
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
        response.raise_for_status()
        
        return response.json()

    # -----------------------------------
    # Fetch Oman Report
    # -----------------------------------
    def get_report(self, token, reference_number, invoice_type_code):
        url = self.base_url + self.report_endpoint
        
        headers = {
            "Authorization": f"Bearer {token}"
        }
        
        params = {
            "referencenumber": reference_number,
            "Invoicetypecode": invoice_type_code,
            "financialyear": self.financial_year
        }

        max_retries = 12
        report_json = None

        for attempt in range(max_retries):
            print(f"Fetching Oman JSON report for {reference_number} (Attempt {attempt + 1}/{max_retries})")

            try:
                response = requests.get(url, headers=headers, params=params)
                report_json = response.json()
                
                invoice_data = report_json.get("Invoice", {})
                
                error_message = invoice_data.get("ErrorMessage", "")
                if error_message is None:
                    error_message = ""
                    
                error_message = str(error_message).strip()

                # Error generated
                if error_message != "":
                    print("Validation completed with errors.")
                    return report_json

                # Wait a few retries before assuming success (min 10 seconds of processing time)
                if attempt >= 2:
                    print("Validation completed successfully.")
                    return report_json

            except Exception as e:
                print(f"Waiting for Oman report generation (Attempt {attempt + 1}) : {e}")

            # 5-second sleep between polling attempts
            time.sleep(5)

        print("Unable to fetch Oman report after maximum retries.")
        return report_json