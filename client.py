"""JSON Schema Contract Validator.
100% Python Standard Library.
"""
import json
from typing import Dict, Any, List

class JSONSchemaContractValidator:
    """Zero-dependency JSON schema subset validator & contract enforce guard."""

    @classmethod
    def validate_contract(cls, data: Any, schema: Dict[str, Any], path: str = "$") -> Dict[str, Any]:
        errors = []

        expected_type = schema.get("type")
        if expected_type:
            type_map = {
                "string": str,
                "number": (int, float),
                "integer": int,
                "boolean": bool,
                "array": list,
                "object": dict,
                "null": type(None)
            }
            if expected_type in type_map:
                target_cls = type_map[expected_type]
                if expected_type == "integer" and isinstance(data, bool):
                    errors.append(f"{path}: expected integer, got boolean")
                elif expected_type == "number" and isinstance(data, bool):
                    errors.append(f"{path}: expected number, got boolean")
                elif not isinstance(data, target_cls):
                    errors.append(f"{path}: expected {expected_type}, got {type(data).__name__}")

        if isinstance(data, dict):
            for req in schema.get("required", []):
                if req not in data:
                    errors.append(f"{path}: missing required field '{req}'")

            props = schema.get("properties", {})
            for k, val in data.items():
                if k in props:
                    sub_res = cls.validate_contract(val, props[k], f"{path}.{k}")
                    errors.extend(sub_res["errors"])

        elif isinstance(data, list):
            items_schema = schema.get("items")
            if items_schema:
                for idx, item in enumerate(data):
                    sub_res = cls.validate_contract(item, items_schema, f"{path}[{idx}]")
                    errors.extend(sub_res["errors"])

        if "enum" in schema and data not in schema["enum"]:
            errors.append(f"{path}: value {json.dumps(data)} not in enum {schema['enum']}")

        if isinstance(data, (int, float)) and not isinstance(data, bool):
            if "minimum" in schema and data < schema["minimum"]:
                errors.append(f"{path}: value {data} < minimum {schema['minimum']}")
            if "maximum" in schema and data > schema["maximum"]:
                errors.append(f"{path}: value {data} > maximum {schema['maximum']}")

        if isinstance(data, str):
            if "minLength" in schema and len(data) < schema["minLength"]:
                errors.append(f"{path}: string length {len(data)} < minLength {schema['minLength']}")
            if "maxLength" in schema and len(data) > schema["maxLength"]:
                errors.append(f"{path}: string length {len(data)} > maxLength {schema['maxLength']}")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "error_count": len(errors)
        }

    @classmethod
    def sanitize_and_repair(cls, data: Any, schema: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(data, dict) or schema.get("type") != "object":
            return {"repaired_data": data, "modifications": []}

        props = schema.get("properties", {})
        repaired = {}
        mods = []

        for k, prop_schema in props.items():
            if k in data:
                val = data[k]
                exp = prop_schema.get("type")
                if exp == "integer" and isinstance(val, str) and val.isdigit():
                    repaired[k] = int(val)
                    mods.append(f"Cast '{k}' from string to integer")
                elif exp == "number" and isinstance(val, str):
                    try:
                        repaired[k] = float(val)
                        mods.append(f"Cast '{k}' from string to float")
                    except ValueError:
                        repaired[k] = val
                else:
                    repaired[k] = val
            elif "default" in prop_schema:
                repaired[k] = prop_schema["default"]
                mods.append(f"Set default value for '{k}'")

        return {
            "repaired_data": repaired,
            "modifications": mods
        }
