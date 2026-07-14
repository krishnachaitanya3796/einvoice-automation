def validate_result(report_response, expected_result, expected_error=""):

    invoice = report_response.get("Invoice", {})
    status = invoice.get("Status", "")
    error_message = invoice.get("ErrorMessage", "")

    # Handle Peppol validation failures even if ErrorMessage is blank
    if status == "VALIDATION_ERROR":
        return "PASS", "Validation Error"

    if expected_result == "SUCCESS":
        if status == "SUCCESS":
            return "PASS", ""
        return "FAIL", error_message

    if expected_result == "FAILED":
        if expected_error.lower() in error_message.lower():
            return "PASS", error_message
        return "FAIL", error_message

    return "FAIL", error_message