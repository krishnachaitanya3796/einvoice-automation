import json
import os
import pandas as pd
from datetime import datetime
from api_client import TaxillaAPI
from mutation_engine import apply_mutation

REPORT_FILE = "results/oman_execution_report.xlsx"
START_FROM = 1
END_AT = 1075

# Load configurations and data
with open("config.json") as f:
    config = json.load(f)

with open("base_invoice.json") as f:
    base_payload = json.load(f)

with open("oman_689_business_validation_scenarios.json") as f:
    test_scenarios = json.load(f)

# Initialize API
api = TaxillaAPI(config)
results = []

# Load old report if it exists
if os.path.exists(REPORT_FILE):
    existing_df = pd.read_excel(REPORT_FILE)
else:
    existing_df = pd.DataFrame()

# -----------------------------
# Execute Scenarios
# -----------------------------
for scenario in test_scenarios:
    test_id = scenario["id"]

    if test_id == "OM0000":
        test_num = 0
    else:
        test_num = int(test_id.replace("OM", ""))

    if test_num < START_FROM or test_num > END_AT:
        continue

    print("\n" + "=" * 70)
    print(f"Running: {scenario['id']}")
    print(scenario["scenario"])
    print("=" * 70)

    try:
        # Generate payload and make API calls
        payload = apply_mutation(base_payload, scenario, test_num)
        token = api.get_token()
        
        post_response = api.post_invoice(token, payload)
        print("POST Response:", post_response)

        ref_num = payload.get("ReferenceNumber", "")
        invoice_type = payload.get("Invoicetypecode", "")
        
        # Fetch Report 
        report_json = api.get_report(token, ref_num, invoice_type)

        print("\nFULL REPORT RESPONSE:")
        print(json.dumps(report_json, indent=4) if report_json else "None")
        
        print("\nERROR MESSAGE FROM RESPONSE:")
        print(report_json.get("Invoice", {}).get("ErrorMessage") if report_json else None)

        # -----------------------------
        # Parse Oman Report
        # -----------------------------
        if report_json is None:
            report_data = {
                "status": "FAILED",
                "error_from": "SYSTEM",
                "error_message": "Oman report not generated"
            }
        else:
            invoice_data = report_json.get("Invoice", {})

            # Strictly rely on ErrorMessage as the source of truth
            error_message = invoice_data.get("ErrorMessage", "")
            if error_message is None:
                error_message = ""

            error_message = str(error_message).replace("|", "").strip(",").strip()

            if error_message:
                actual_status = "FAILED"
            else:
                actual_status = "SUCCESS"

            report_data = {
                "status": actual_status,
                "error_from": "Taxilla",
                "error_message": error_message if error_message else "No Error"
            }

        print("Report Data:", report_data)

        # -----------------------------
        # Result Calculation
        # -----------------------------
        expected = str(scenario.get("expected_result", "")).strip().upper()
        actual = str(report_data.get("status", "")).strip().upper()

        print("Expected =", expected)
        print("Actual =", actual)

        result = "PASS" if expected == actual else "FAIL"
        print("FINAL RESULT =", result)

        # -----------------------------
        # Save Result
        # -----------------------------
        results.append({
            "Execution Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Test ID": scenario["id"],
            "Scenario": scenario["scenario"],
            "Reference Number": payload.get("ReferenceNumber", ""),
            "Invoice Number": payload.get("Invoicenumber", ""),
            "Field Tested": scenario.get("field_path", ""),
            "Mutation Type": scenario.get("mutation_type", ""),
            "Mutation Value": scenario.get("mutation_value", ""),
            "Expected Result": expected,
            "Actual Result": actual,
            "Error From": report_data["error_from"],
            "Actual Error": report_data["error_message"],
            "Defect Status": "YES" if result == "FAIL" else "NO",
            "Final Result": result
        })

    except Exception as e:
        print("Execution Failed:", e)
        results.append({
            "Execution Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Test ID": scenario["id"],
            "Scenario": scenario["scenario"],
            "Reference Number": "",
            "Invoice Number": "",
            "Field Tested": scenario.get("field_path", ""),
            "Mutation Type": scenario.get("mutation_type", ""),
            "Mutation Value": scenario.get("mutation_value", ""),
            "Expected Result": scenario.get("expected_result", ""),
            "Actual Result": "EXCEPTION",
            "Error From": "PYTHON",
            "Actual Error": str(e),
            "Defect Status": "YES",
            "Final Result": "FAIL"
        })

# -----------------------------
# Save Excel
# -----------------------------
new_df = pd.DataFrame(results)
final_df = pd.concat([existing_df, new_df], ignore_index=True)
final_df.to_excel(REPORT_FILE, index=False)

print(f"\nExecution report updated: {REPORT_FILE}")