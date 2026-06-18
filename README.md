# E-Invoice Automation Framework

A generic automation framework for validating e-invoice payloads through API-driven testing.

## Overview

This framework automates end-to-end invoice validation workflows by:

* Mutating base payloads
* Submitting payloads to APIs
* Retrieving validation reports
* Comparing expected vs actual outcomes
* Generating execution reports

It is designed for scalable regression testing of e-invoice business rules, schema validations, and dependency validations.

---

## Features

* Payload mutation engine
* Positive and negative testcase execution
* Rule-based validation testing
* Dependency testing between fields
* Transaction type testing
* Automated execution reporting
* Reusable framework for multiple invoice standards

---

## Project Structure

```text
einvoice-automation/
│── api_client.py
│── assertions.py
│── mutation_engine.py
│── test_runner.py
│── base_invoice.json
│── config.sample.json
│── config.json
│── results/
│── README.md
```

---

## Setup

Clone repository:

```bash
git clone <repository-url>
cd einvoice-automation
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create configuration file:

```bash
cp config.sample.json config.json
```

Update your API credentials and endpoints in `config.json`.

---

## Running Tests

Run all tests:

```bash
python test_runner.py
```

Control execution range:

```python
START_FROM = 1
END_AT = 33
```

Example:

```python
START_FROM = 17
END_AT = 25
```

This executes only selected testcases.

---

## Test Coverage

### Core validations

* Mandatory fields
* Tax validations
* Quantity validations
* Price validations
* Currency validations
* Country validations

### Dependency validations

* Field interdependency checks
* Conditional mandatory fields
* Transaction-specific rules

### Transaction type validations

* Standard invoices
* Free trade zone
* Deemed supply
* Margin scheme
* Summary invoice
* Continuous supply
* Agent billing
* E-commerce
* Export

---

## Reporting

Execution reports are generated in:

```text
results/execution_report.xlsx
```

Report includes:

* Test ID
* Scenario
* Reference Number
* Expected Result
* Actual Error
* Final Result
* Defect Status

---

## Extensibility

This framework can be extended for:

* Credit Notes
* Debit Notes
* Country-specific invoice standards
* Additional validation engines
* Attachment validations
* Business-specific custom rules

---

## Security

Sensitive files should be excluded from version control:

Use `config.sample.json` as the template for configuration setup.
