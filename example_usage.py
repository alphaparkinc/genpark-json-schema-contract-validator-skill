"""Example usage for GenPark JSON Schema Contract Validator."""
from client import JSONSchemaContractValidator

def main():
    schema = {
        "type": "object",
        "required": ["action", "target_id", "priority"],
        "properties": {
            "action": {"type": "string", "enum": ["create", "update", "delete"]},
            "target_id": {"type": "integer", "minimum": 1},
            "priority": {"type": "string", "default": "medium"}
        }
    }

    test_input = {"action": "create", "target_id": "105"} # target_id as string
    print("Validating raw LLM response...")
    val = JSONSchemaContractValidator.validate_contract(test_input, schema)
    print("Valid:", val["valid"], "| Errors:", val["errors"])

    print("
Sanitizing and repairing payload...")
    repair = JSONSchemaContractValidator.sanitize_and_repair(test_input, schema)
    print("Repaired Data:", repair["repaired_data"])
    print("Applied Repairs:", repair["modifications"])

    print("
Re-validating repaired data...")
    val_after = JSONSchemaContractValidator.validate_contract(repair["repaired_data"], schema)
    print("Valid after repair:", val_after["valid"])

if __name__ == "__main__":
    main()
