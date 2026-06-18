import json
import os
import pandas as pd
from datetime import datetime
from api_client import TaxillaAPI
from mutation_engine import apply_mutation
from assertions import validate_result


REPORT_FILE = "results/execution_report.xlsx"
START_FROM = 67
END_AT = 76

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
},
{
    "id": "UAE034",
    "scenario": "Document Allowance missing VAT category",
    "field_path": "AllowanceCharge[0]>AllowanceCharge.TaxCategory>AllowanceCharge.ID",
    "mutation_type": "replace",
    "mutation_value": "",
    "expected_result": "FAILED"
},
{
    "id": "UAE035",
    "scenario": "Document Charge missing VAT category",
    "field_path": "AllowanceCharge[1]>AllowanceCharge.TaxCategory>AllowanceCharge.ID",
    "mutation_type": "replace",
    "mutation_value": "",
    "expected_result": "FAILED"
},
{
    "id": "UAE036",
    "scenario": "Allowance Base present without Percentage",
    "field_path": "AllowanceCharge[0]>MultiplierFactorNumeric",
    "mutation_type": "replace",
    "mutation_value": "",
    "expected_result": "FAILED"
},
{
    "id": "UAE037",
    "scenario": "Charge Base present without Percentage",
    "field_path": "AllowanceCharge[1]>MultiplierFactorNumeric",
    "mutation_type": "replace",
    "mutation_value": "",
    "expected_result": "FAILED"
},
{
    "id": "UAE038",
    "scenario": "Line Reverse Charge without VAT Rate",
    "field_path": "InvoiceLine[0]>InvoiceLine.LineItem>ClassifiedTaxCategory>ClassifiedTaxCategory.Percent",
    "pre_mutations": [
        {
            "field_path": "InvoiceLine[0]>InvoiceLine.LineItem>ClassifiedTaxCategory>ClassifiedTaxCategory.ID",
            "mutation_value": "AE"
        }
    ],
    "mutation_type": "replace",
    "mutation_value": "",
    "expected_result": "FAILED"
},
{
    "id": "UAE039",
    "scenario": "Allowance Reverse Charge with zero VAT Rate",
    "pre_mutations": [
        {
            "field_path": "AllowanceCharge[0]>AllowanceCharge.TaxCategory>AllowanceCharge.ID",
            "mutation_value": "AE"
        }
    ],
    "field_path": "AllowanceCharge[0]>AllowanceCharge.TaxCategory>AllowanceCharge.Percent",
    "mutation_type": "replace",
    "mutation_value": "0",
    "expected_result": "FAILED"
},
{
    "id": "UAE040",
    "scenario": "Charge Reverse Charge with zero VAT Rate",
    "pre_mutations": [
        {
            "field_path": "AllowanceCharge[1]>AllowanceCharge.TaxCategory>AllowanceCharge.ID",
            "mutation_value": "AE"
        }
    ],
    "field_path": "AllowanceCharge[1]>AllowanceCharge.TaxCategory>AllowanceCharge.Percent",
    "mutation_type": "replace",
    "mutation_value": "0",
    "expected_result": "FAILED"
},
{
    "id": "UAE041",
    "scenario": "Foreign Currency without VAT Accounting Currency",
    "field_path": "DocumentCurrencyCode",
    "mutation_type": "replace",
    "mutation_value": "USD",
    "expected_result": "FAILED"
},

{
    "id": "UAE042",
    "scenario": "Foreign Currency with VAT Accounting Currency but missing Exchange Rate",
    "pre_mutations": [
        {"field_path": "DocumentCurrencyCode", "mutation_value": "USD"},
        {"field_path": "VATCurrencyCode", "mutation_value": "AED"}
    ],
    "field_path": "ExchangeRate",
    "mutation_type": "replace",
    "mutation_value": "",
    "expected_result": "FAILED"
},

{
    "id": "UAE043",
    "scenario": "Foreign Currency with Exchange Rate but missing VAT Amount in Accounting Currency",
    "pre_mutations": [
        {"field_path": "DocumentCurrencyCode", "mutation_value": "USD"},
        {"field_path": "VATCurrencyCode", "mutation_value": "AED"},
        {"field_path": "ExchangeRate", "mutation_value": "3.670000"}
    ],
    "field_path": "TotalVATamountinAccountingCurrency",
    "mutation_type": "replace",
    "mutation_value": "",
    "expected_result": "FAILED"
},

{
    "id": "UAE044",
    "scenario": "Foreign Currency complete valid setup",
    "pre_mutations": [
        {"field_path": "DocumentCurrencyCode", "mutation_value": "USD"},
        {"field_path": "VATCurrencyCode", "mutation_value": "AED"},
        {"field_path": "ExchangeRate", "mutation_value": "3.670000"}
    ],
    "field_path": "TotalVATamountinAccountingCurrency",
    "mutation_type": "replace",
    "mutation_value": "171.25",
    "expected_result": "SUCCESS"
},

{
    "id": "UAE045",
    "scenario": "Foreign Currency Exchange Rate more than 6 decimals",
    "pre_mutations": [
        {"field_path": "DocumentCurrencyCode", "mutation_value": "USD"},
        {"field_path": "VATCurrencyCode", "mutation_value": "AED"}
    ],
    "field_path": "ExchangeRate",
    "mutation_type": "replace",
    "mutation_value": "3.6700001",
    "expected_result": "FAILED"
},

{
    "id": "UAE046",
    "scenario": "Foreign Currency Exchange Rate exactly 6 decimals",
    "pre_mutations": [
        {"field_path": "DocumentCurrencyCode", "mutation_value": "USD"},
        {"field_path": "VATCurrencyCode", "mutation_value": "AED"}
    ],
    "field_path": "ExchangeRate",
    "mutation_type": "replace",
    "mutation_value": "3.670000",
    "expected_result": "SUCCESS"
},
{
    "id": "UAE047",
    "scenario": "Billing Reference ID without Issue Date",
    "field_path": "BillingReference[0]>BillingReference.InvoiceDocumentReference.IssueDate",
    "mutation_type": "replace",
    "mutation_value": "",
    "expected_result": "FAILED"
},

{
    "id": "UAE048",
    "scenario": "Billing Reference complete",
    "pre_mutations": [
        {"field_path": "BillingReference[0]>BillingReference.InvoiceDocumentReference.ID", "mutation_value": "INV-REF-1001"}
    ],
    "field_path": "BillingReference[0]>BillingReference.InvoiceDocumentReference.IssueDate",
    "mutation_type": "replace",
    "mutation_value": "2026-04-01",
    "expected_result": "SUCCESS"
},

{
    "id": "UAE049",
    "scenario": "Additional Document missing type code",
    "field_path": "AdditionalDocumentDetails[0]>DocumentTypecode",
    "mutation_type": "replace",
    "mutation_value": "",
    "expected_result": "FAILED"
},

{
    "id": "UAE050",
    "scenario": "Additional Document with invalid mime code",
    "field_path": "AdditionalDocumentDetails[0]>mimeCode",
    "mutation_type": "replace",
    "mutation_value": "TXT",
    "expected_result": "FAILED"
},

{
    "id": "UAE051",
    "scenario": "Additional Document valid",
    "field_path": "AdditionalDocumentDetails[0]>mimeCode",
    "mutation_type": "replace",
    "mutation_value": "PDF",
    "expected_result": "SUCCESS"
},

{
    "id": "UAE052",
    "scenario": "Contract Reference missing contract number",
    "field_path": "ContractDocumentReference[0]>ContractDocumentReference.Number",
    "mutation_type": "replace",
    "mutation_value": "",
    "expected_result": "FAILED"
},

{
    "id": "UAE053",
    "scenario": "Contract Reference valid",
    "field_path": "ContractDocumentReference[0]>ContractDocumentReference.Number",
    "mutation_type": "replace",
    "mutation_value": "Contract-456",
    "expected_result": "SUCCESS"
},
{
    "id": "UAE054",
    "scenario": "Purchase Order missing",
    "field_path": "Purchaseorderreference",
    "mutation_type": "replace",
    "mutation_value": "",
    "expected_result": "SUCCESS"
},

{
    "id": "UAE055",
    "scenario": "Sales Order missing",
    "field_path": "Salesorderreference",
    "mutation_type": "replace",
    "mutation_value": "",
    "expected_result": "SUCCESS"
},

{
    "id": "UAE056",
    "scenario": "Despatch Advice missing",
    "field_path": "Despatchadvicereference",
    "mutation_type": "replace",
    "mutation_value": "",
    "expected_result": "SUCCESS"
},
{
    "id": "UAE057",
    "scenario": "Payment Means Code missing",
    "field_path": "PaymentMeans>PaymentMeansCode",
    "mutation_type": "replace",
    "mutation_value": "",
    "expected_result": "FAILED"
},

{
    "id": "UAE058",
    "scenario": "Payment Means valid",
    "field_path": "PaymentMeans>PaymentMeansCode",
    "mutation_type": "replace",
    "mutation_value": "30",
    "expected_result": "SUCCESS"
},

{
    "id": "UAE059",
    "scenario": "Payment Terms note missing",
    "field_path": "PaymentTerms>PaymentTerms.Note",
    "mutation_type": "replace",
    "mutation_value": "",
    "expected_result": "SUCCESS"
},

{
    "id": "UAE060",
    "scenario": "Payee Account ID missing",
    "field_path": "PaymentTerms>PymtTerms.PayeeAccountID",
    "mutation_type": "replace",
    "mutation_value": "",
    "expected_result": "SUCCESS"
},

{
    "id": "UAE061",
    "scenario": "Payment Name missing",
    "field_path": "PaymentMeans>PaymentName",
    "mutation_type": "replace",
    "mutation_value": "",
    "expected_result": "SUCCESS"
},

{
    "id": "UAE062",
    "scenario": "Payment ID missing",
    "field_path": "PaymentMeans>PaymentID",
    "mutation_type": "replace",
    "mutation_value": "",
    "expected_result": "SUCCESS"
},

{
    "id": "UAE063",
    "scenario": "Primary Account Number present without Network ID",
    "pre_mutations": [
        {"field_path": "PaymentMeans>PrimaryAccountNumberID", "mutation_value": "4111111111111111"}
    ],
    "field_path": "PaymentMeans>NetworkID",
    "mutation_type": "replace",
    "mutation_value": "",
    "expected_result": "FAILED"
},

{
    "id": "UAE064",
    "scenario": "Primary Account Number with Network ID",
    "pre_mutations": [
        {"field_path": "PaymentMeans>PrimaryAccountNumberID", "mutation_value": "4111111111111111"}
    ],
    "field_path": "PaymentMeans>NetworkID",
    "mutation_type": "replace",
    "mutation_value": "VISA",
    "expected_result": "SUCCESS"
},

{
    "id": "UAE065",
    "scenario": "Payment Mandate without Payer Account",
    "pre_mutations": [
        {"field_path": "PaymentMeans>PaymentMandate.ID", "mutation_value": "MANDATE001"}
    ],
    "field_path": "PaymentMeans>PayerFinancialAccount.ID",
    "mutation_type": "replace",
    "mutation_value": "",
    "expected_result": "FAILED"
},

{
    "id": "UAE066",
    "scenario": "Payment Mandate with Payer Account",
    "pre_mutations": [
        {"field_path": "PaymentMeans>PaymentMandate.ID", "mutation_value": "MANDATE001"}
    ],
    "field_path": "PaymentMeans>PayerFinancialAccount.ID",
    "mutation_type": "replace",
    "mutation_value": "AE070331234567890123456",
    "expected_result": "SUCCESS"
},
{
    "id": "UAE067",
    "scenario": "Seller Endpoint missing",
    "field_path": "AccountingSupplierParty>AccountingSupplierParty.EndpointID>AccountingSupplierParty.SellerElectronicAddress",
    "mutation_type": "replace",
    "mutation_value": "",
    "expected_result": "FAILED"
},

{
    "id": "UAE068",
    "scenario": "Seller Endpoint Scheme missing",
    "field_path": "AccountingSupplierParty>AccountingSupplierParty.EndpointID>AccountingSupplierParty.schemeID",
    "mutation_type": "replace",
    "mutation_value": "",
    "expected_result": "FAILED"
},

{
    "id": "UAE069",
    "scenario": "Buyer Endpoint missing",
    "field_path": "AccountingCustomerParty>EndpointID>BuyerElectronicAddress",
    "mutation_type": "replace",
    "mutation_value": "",
    "expected_result": "FAILED"
},

{
    "id": "UAE070",
    "scenario": "Buyer Endpoint Scheme missing",
    "field_path": "AccountingCustomerParty>EndpointID>SchemeID",
    "mutation_type": "replace",
    "mutation_value": "",
    "expected_result": "FAILED"
},

{
    "id": "UAE071",
    "scenario": "Seller Contact Name missing",
    "field_path": "AccountingSupplierParty>AccountingSupplierParty.Contact>AccountingSupplierParty.Name",
    "mutation_type": "replace",
    "mutation_value": "",
    "expected_result": "SUCCESS"
},

{
    "id": "UAE072",
    "scenario": "Seller Contact Phone missing",
    "field_path": "AccountingSupplierParty>AccountingSupplierParty.Contact>AccountingSupplierParty.Telephone",
    "mutation_type": "replace",
    "mutation_value": "",
    "expected_result": "SUCCESS"
},

{
    "id": "UAE073",
    "scenario": "Seller Contact Email missing",
    "field_path": "AccountingSupplierParty>AccountingSupplierParty.Contact>AccountingSupplierParty.EmailID",
    "mutation_type": "replace",
    "mutation_value": "",
    "expected_result": "SUCCESS"
},

{
    "id": "UAE074",
    "scenario": "Buyer Contact Name missing",
    "field_path": "AccountingCustomerParty>PartyTaxScheme>Contact>Name",
    "mutation_type": "replace",
    "mutation_value": "",
    "expected_result": "SUCCESS"
},

{
    "id": "UAE075",
    "scenario": "Buyer Contact Phone missing",
    "field_path": "AccountingCustomerParty>PartyTaxScheme>Contact>Telephone",
    "mutation_type": "replace",
    "mutation_value": "",
    "expected_result": "SUCCESS"
},

{
    "id": "UAE076",
    "scenario": "Buyer Contact Email missing",
    "field_path": "AccountingCustomerParty>PartyTaxScheme>Contact>ElectronicEmail",
    "mutation_type": "replace",
    "mutation_value": "",
    "expected_result": "SUCCESS"
},
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
    "Error From": report_response.get("Invoice", {}).get("ErrorFrom", ""),
    "Status": report_response.get("Invoice", {}).get("Status", ""),
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