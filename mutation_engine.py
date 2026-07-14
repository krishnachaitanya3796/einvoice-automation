import copy
import uuid
from datetime import datetime


def get_nested_parent(
    payload,
    field_path
):

    # Support both:
    # SellerDetails.SellerVATIdentifier
    # SellerDetails>SellerVATIdentifier

    field_path = field_path.replace(
        ".",
        ">"
    )

    keys = field_path.split(">")

    current = payload

    for key in keys[:-1]:

        # Handle arrays
        if "[" in key and "]" in key:

            list_name = key.split("[")[0]

            index = int(
                key.split("[")[1]
                .split("]")[0]
            )

            current = current[
                list_name
            ][index]

        else:

            current = current[key]

    return current, keys[-1]


def apply_mutation(
    base_payload,
    scenario,
    counter
):

    payload = copy.deepcopy(
        base_payload
    )

    # --------------------------------
    # Always generate unique invoice
    # --------------------------------

    timestamp = datetime.now().strftime(
        "%Y%m%d%H%M%S"
    )

    unique_suffix = str(
        uuid.uuid4()
    )[:8]

    unique_id = (
        f"OM-"
        f"{timestamp}-"
        f"{unique_suffix}"
    )

    payload[
        "ReferenceNumber"
    ] = unique_id

    payload[
        "Invoicenumber"
    ] = unique_id

    payload[
        "FinancialYear"
    ] = "2026"

    # --------------------------------
    # Mutation details
    # --------------------------------

    field_path = scenario.get(
        "field_path",
        ""
    )

    mutation_type = scenario.get(
        "mutation_type",
        "none"
    )

    mutation_value = scenario.get(
        "mutation_value",
        ""
    )

    # Valid invoice
    if mutation_type == "none":
        return payload

    try:

        parent, final_key = (
            get_nested_parent(
                payload,
                field_path
            )
        )

        # --------------------------
        # Remove field
        # --------------------------

        if mutation_type == "remove":

            if final_key in parent:

                del parent[
                    final_key
                ]

        # --------------------------
        # Replace value
        # --------------------------

        elif mutation_type == "replace":

            parent[
                final_key
            ] = mutation_value

        # --------------------------
        # Rule placeholder
        # --------------------------

        elif mutation_type == "rule":

            print(
                f"Rule mutation not "
                f"implemented yet: "
                f"{scenario['id']}"
            )

    except Exception as e:

        print(
            f"Mutation failed for "
            f"{scenario['id']} "
            f"Field: {field_path}"
        )

        print(
            f"Reason: {e}"
        )

    return payload