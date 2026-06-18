import json
import os
import pandas as pd
from datetime import datetime
from api_client import TaxillaAPI
from mutation_engine import apply_mutation
from assertions import validate_result


REPORT_FILE = "results/execution_report.xlsx"
START_FROM = 26
END_AT = 33

# Load config
with open("config.json") as f:
    config = json.load(f)

# Load base payload
with open("base_invoice.json") as f:
    base_payload = json.load(f)

# Initialize API
api = TaxillaAPI(config)

# Test scenarios
test_scenarios = [

    {
        "id": "UAE001",
        "scenario": "Valid Invoice",
        "field_path": "",
        "mutation_type": "none",
        "mutation_value": "",
        "expected_result": "SUCCESS"
    },

    {
        "id": "UAE002",
        "scenario": "Blank Invoice Type",
        "field_path": "InvoiceTypeCode",
        "mutation_type": "replace",
        "mutation_value": "",
        "expected_result": "FAILED",
        "expected_error_contains": "Invoice Type Code"
    },

    {
        "id": "UAE003",
        "scenario": "Blank Issue Date",
        "field_path": "IssueDate",
        "mutation_type": "replace",
        "mutation_value": "",
        "expected_result": "FAILED",
        "expected_error_contains": "Issue Date"
    },

    {
        "id": "UAE004",
        "scenario": "Blank Currency",
        "field_path": "DocumentCurrencyCode",
        "mutation_type": "replace",
        "mutation_value": "",
        "expected_result": "FAILED",
        "expected_error_contains": "Currency"
    },

    {
        "id": "UAE005",
        "scenario": "Blank Item Name",
        "field_path": "InvoiceLine[0]>InvoiceLine.LineItem>InvoiceLine.Name",
        "mutation_type": "replace",
        "mutation_value": "",
        "expected_result": "FAILED",
        "expected_error_contains": "Item"
    },

    {
        "id": "UAE006",
        "scenario": "Standard Rate Invalid",
        "field_path": "InvoiceLine[0]>InvoiceLine.LineItem>ClassifiedTaxCategory>ClassifiedTaxCategory.Percent",
        "mutation_type": "replace",
        "mutation_value": "0",
        "expected_result": "FAILED",
        "expected_error_contains": "greater than zero"
    },

    {
        "id": "UAE007",
        "scenario": "Blank Seller Name",
        "field_path": "AccountingSupplierParty>AccountingSupplierParty.PartyLegalEntity>AccountingSupplierParty.RegistrationName",
        "mutation_type": "replace",
        "mutation_value": "",
        "expected_result": "FAILED",
        "expected_error_contains": "Seller"
    },

    {
        "id": "UAE008",
        "scenario": "Blank Buyer Name",
        "field_path": "AccountingCustomerParty>PartyTaxScheme>PartyLegalEntity>RegistrationName",
        "mutation_type": "replace",
        "mutation_value": "",
        "expected_result": "FAILED",
        "expected_error_contains": "Buyer"
    },

    {
        "id": "UAE009",
        "scenario": "Blank Supplier VAT",
        "field_path": "AccountingSupplierParty>AccountingSupplierParty.TaxScheme>SellerTaxidentifier",
        "mutation_type": "replace",
        "mutation_value": "",
        "expected_result": "FAILED",
        "expected_error_contains": "VAT"
    },

    {
        "id": "UAE010",
        "scenario": "Blank Buyer VAT",
        "field_path": "AccountingCustomerParty>PartyTaxScheme>CompanyID",
        "mutation_type": "replace",
        "mutation_value": "",
        "expected_result": "FAILED",
        "expected_error_contains": "VAT"
    },

    {
        "id": "UAE011",
        "scenario": "Negative Price",
        "field_path": "InvoiceLine[0]>InvoiceLine.LineItem>Price>Price.PriceAmount>Price.PriceAmount",
        "mutation_type": "replace",
        "mutation_value": -100,
        "expected_result": "FAILED",
        "expected_error_contains": "Price"
    },

    {
        "id": "UAE012",
        "scenario": "Zero Quantity",
        "field_path": "InvoiceLine[0]>InvoiceLine.InvoicedQuantity>InvoiceLine.Quantity",
        "mutation_type": "replace",
        "mutation_value": "0",
        "expected_result": "FAILED",
        "expected_error_contains": "Quantity"
    },

    {
        "id": "UAE013",
        "scenario": "Negative Quantity",
        "field_path": "InvoiceLine[0]>InvoiceLine.InvoicedQuantity>InvoiceLine.Quantity",
        "mutation_type": "replace",
        "mutation_value": "-1",
        "expected_result": "FAILED",
        "expected_error_contains": "Quantity"
    },

    {
        "id": "UAE014",
        "scenario": "Invalid Currency Code",
        "field_path": "DocumentCurrencyCode",
        "mutation_type": "replace",
        "mutation_value": "XYZ",
        "expected_result": "FAILED",
        "expected_error_contains": "lookup"
    },

    {
        "id": "UAE015",
        "scenario": "Invalid Supplier Country",
        "field_path": "AccountingSupplierParty>AccountingSupplierParty.PostalAddress>AccountingSupplierParty.Country>AccountingSupplierParty.IdentificationCode",
        "mutation_type": "replace",
        "mutation_value": "XX",
        "expected_result": "FAILED",
        "expected_error_contains": "Country"
    },

    {
        "id": "UAE016",
        "scenario": "Invalid Buyer Country",
        "field_path": "AccountingCustomerParty>PostalAddress>Country>IdentificationCode",
        "mutation_type": "replace",
        "mutation_value": "XX",
        "expected_result": "FAILED",
        "expected_error_contains": "Country"
    },
    {
    "id": "UAE017",
    "scenario": "Disclosed Agent without Principle ID",
    "pre_mutations": [{"field_path": "Invoicetransactiontypecode", "mutation_value": "00000100"}],
    "field_path": "PrincipleID",
    "mutation_type": "replace",
    "mutation_value": "",
    "expected_result": "FAILED",
    "expected_error_contains": "Principle"
},
{
    "id": "UAE018",
    "scenario": "Disclosed Agent with valid Principle ID",
    "pre_mutations": [
        {"field_path": "Invoicetransactiontypecode", "mutation_value": "00000100"}
    ],
    "field_path": "PrincipleID",
    "mutation_type": "replace",
    "mutation_value": "123456789012345",
    "expected_result": "SUCCESS"
},
{
    "id": "UAE019",
    "scenario": "Principle ID same as Seller Tax ID",
    "pre_mutations": [
        {"field_path": "Invoicetransactiontypecode", "mutation_value": "00000100"}
    ],
    "field_path": "PrincipleID",
    "mutation_type": "replace",
    "mutation_value": "105018020500003",
    "expected_result": "FAILED",
    "expected_error_contains": "Principle"
},
{
    "id": "UAE020",
    "scenario": "Free Trade Zone without Beneficiary ID",
    "pre_mutations": [
        {"field_path": "Invoicetransactiontypecode", "mutation_value": "10000000"}
    ],
    "field_path": "BeneficiaryID",
    "mutation_type": "replace",
    "mutation_value": "",
    "expected_result": "FAILED",
    "expected_error_contains": "Beneficiary"
},
{
    "id": "UAE021",
    "scenario": "Free Trade Zone with Beneficiary ID",
    "pre_mutations": [
        {"field_path": "Invoicetransactiontypecode", "mutation_value": "10000000"}
    ],
    "field_path": "BeneficiaryID",
    "mutation_type": "replace",
    "mutation_value": "123456789012345",
    "expected_result": "SUCCESS"
},
{
    "id": "UAE022",
    "scenario": "AE Seller without Transaction Type Code",
    "field_path": "Invoicetransactiontypecode",
    "mutation_type": "replace",
    "mutation_value": "",
    "expected_result": "FAILED",
    "expected_error_contains": "transaction"
},
{
    "id": "UAE023",
    "scenario": "AE Seller with valid Transaction Type Code",
    "field_path": "Invoicetransactiontypecode",
    "mutation_type": "replace",
    "mutation_value": "00000000",
    "expected_result": "SUCCESS"
},
{
    "id": "UAE024",
    "scenario": "Deemed Supply without Payment Means",
    "pre_mutations": [
        {"field_path": "Invoicetransactiontypecode", "mutation_value": "01000000"}
    ],
    "field_path": "PaymentMeans>PaymentMeansCode",
    "mutation_type": "replace",
    "mutation_value": "",
    "expected_result": "FAILED",
    "expected_error_contains": "Payment"
},
{
    "id": "UAE025",
    "scenario": "Deemed Supply with Payment Means",
    "pre_mutations": [
        {"field_path": "Invoicetransactiontypecode", "mutation_value": "01000000"}
    ],
    "field_path": "PaymentMeans>PaymentMeansCode",
    "mutation_type": "replace",
    "mutation_value": "30",
    "expected_result": "SUCCESS"
},
{
    "id": "UAE026",
    "scenario": "Margin Scheme without Standard Rate Additional VAT",
    "pre_mutations": [
        {
            "field_path": "Invoicetransactiontypecode",
            "mutation_value": "00100000"
        }
    ],
    "field_path": "InvoiceLine[0]>InvoiceLine.LineItem>ClassifiedTaxCategory>ClassifiedTaxCategory.ID",
    "mutation_type": "replace",
    "mutation_value": "S",
    "expected_result": "FAILED"
},
{
    "id": "UAE027",
    "scenario": "Margin Scheme with Standard Rate Additional VAT",
    "pre_mutations": [
        {
            "field_path": "Invoicetransactiontypecode",
            "mutation_value": "00100000"
        },
        {
            "field_path": "InvoiceLine[0]>InvoiceLine.LineItem>ClassifiedTaxCategory>ClassifiedTaxCategory.ID",
            "mutation_value": "AA"
        }
    ],
    "field_path": "",
    "mutation_type": "none",
    "mutation_value": "",
    "expected_result": "SUCCESS"
},
{
    "id": "UAE028",
    "scenario": "Summary Invoice without Invoicing Period",
    "pre_mutations": [
        {
            "field_path": "Invoicetransactiontypecode",
            "mutation_value": "00010000"
        }
    ],
    "field_path": "InvoicePeriod.StartDate",
    "mutation_type": "replace",
    "mutation_value": "",
    "expected_result": "FAILED"
},
{
    "id": "UAE029",
    "scenario": "Summary Invoice with Invoicing Period",
    "pre_mutations": [
        {
            "field_path": "Invoicetransactiontypecode",
            "mutation_value": "00010000"
        }
    ],
    "field_path": "InvoicePeriod.StartDate",
    "mutation_type": "replace",
    "mutation_value": "2026-04-01",
    "expected_result": "SUCCESS"
},
{
    "id": "UAE030",
    "scenario": "E-commerce without Delivery Street",
    "pre_mutations": [
        {
            "field_path": "Invoicetransactiontypecode",
            "mutation_value": "00000010"
        }
    ],
    "field_path": "Delivery>Delivery.DeliveryLocation>Delivery.PostalAddress>Delivery.StreetName",
    "mutation_type": "replace",
    "mutation_value": "",
    "expected_result": "FAILED"
},
{
    "id": "UAE031",
    "scenario": "E-commerce with Delivery Address",
    "pre_mutations": [
        {
            "field_path": "Invoicetransactiontypecode",
            "mutation_value": "00000010"
        }
    ],
    "field_path": "",
    "mutation_type": "none",
    "mutation_value": "",
    "expected_result": "SUCCESS"
},
{
    "id": "UAE032",
    "scenario": "Export with AE Delivery Country",
    "pre_mutations": [
        {
            "field_path": "Invoicetransactiontypecode",
            "mutation_value": "00000001"
        }
    ],
    "field_path": "Delivery>Delivery.DeliveryLocation>Delivery.PostalAddress>Delivery.Country>Delivery.IdentificationCode",
    "mutation_type": "replace",
    "mutation_value": "AE",
    "expected_result": "FAILED"
},
{
    "id": "UAE033",
    "scenario": "Export with Non-AE Delivery Country",
    "pre_mutations": [
        {
            "field_path": "Invoicetransactiontypecode",
            "mutation_value": "00000001"
        }
    ],
    "field_path": "Delivery>Delivery.DeliveryLocation>Delivery.PostalAddress>Delivery.Country>Delivery.IdentificationCode",
    "mutation_type": "replace",
    "mutation_value": "IN",
    "expected_result": "SUCCESS"
}

]

results = []

# Load old report if exists
if os.path.exists(REPORT_FILE):
    existing_df = pd.read_excel(REPORT_FILE)
else:
    existing_df = pd.DataFrame()

counter = len(existing_df) + 1

for scenario in test_scenarios:
    test_num = int(scenario["id"].replace("UAE", ""))

    if test_num < START_FROM or test_num > END_AT:
        continue

    payload = apply_mutation(
        base_payload,
        scenario,
        counter
    )

    token = api.get_token()

    post_response = api.post_invoice(
    token,
    payload
)

    print("POST Response:", post_response)
    import time
    time.sleep(8)

    print("POST Reference:", payload["ReferenceNumber"])
    print("POST InvoiceTypeCode:", payload.get("InvoiceTypeCode", ""))
    print("POST FinancialYear:", payload["FinancialYear"])
    
    report_response = api.get_report(
    token,
    payload["ReferenceNumber"],
    payload["InvoiceTypeCode"] if "InvoiceTypeCode" in payload else ""
    )

    print(report_response)

    result, actual_error = validate_result(
    report_response,
    scenario["expected_result"],
    scenario.get("expected_error_contains", "")
)

    results.append({
        "Execution Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Test ID": scenario["id"],
        "Scenario": scenario["scenario"],
        "Reference Number": payload["ReferenceNumber"],
        "Invoice ID": payload["InvoiceID"],
        "Field Tested": scenario["field_path"],
        "Mutation Type": scenario["mutation_type"],
        "Mutation Value": scenario["mutation_value"],
        "Expected Result": scenario["expected_result"],
        "Actual Error": actual_error,
        "Defect Status": "YES" if result == "FAIL" else "NO",
        "Final Result": result
    })

    print("FINAL RESULT:", result)

    counter += 1


new_df = pd.DataFrame(results)

final_df = pd.concat([existing_df, new_df], ignore_index=True)

final_df.drop_duplicates(
    subset=["Test ID", "Reference Number"],
    keep="last",
    inplace=True
)

final_df.to_excel(REPORT_FILE, index=False)

print("\nExecution report updated:", REPORT_FILE)