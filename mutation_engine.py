import copy
import uuid


def get_nested_parent(payload, field_path):
    keys = field_path.split(">")
    current = payload

    for key in keys[:-1]:
        if "[" in key and "]" in key:
            list_name = key.split("[")[0]
            index = int(key.split("[")[1].split("]")[0])
            current = current[list_name][index]
        else:
            current = current[key]

    return current, keys[-1]


def apply_mutation(base_payload, scenario, counter):
    payload = copy.deepcopy(base_payload)

    new_id = f"UAE-INV-AUTO-{counter:03}"

    payload["ReferenceNumber"] = new_id
    payload["InvoiceID"] = new_id
    payload["UUID"] = str(uuid.uuid4())
    payload["FinancialYear"] = "2026"

    field_path = scenario["field_path"]
    mutation_type = scenario["mutation_type"]
    mutation_value = scenario["mutation_value"]

    if mutation_type == "none":
        return payload

    parent, final_key = get_nested_parent(payload, field_path)

    if mutation_type == "remove":
        if final_key in parent:
            del parent[final_key]

    if mutation_type == "replace":
        parent[final_key] = mutation_value

    return payload