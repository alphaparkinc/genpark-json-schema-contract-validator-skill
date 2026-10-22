"""MCP Stdio Server for JSON Schema Contract Validator.
100% Python Standard Library.
"""
import sys
import json
from client import JSONSchemaContractValidator

validator = JSONSchemaContractValidator()

def handle_rpc(line):
    try:
        req = json.loads(line)
    except Exception:
        return
    req_id = req.get("id")
    method = req.get("method")
    params = req.get("params", {})

    if method == "initialize":
        res = {
            "protocolVersion": "2024-11-05",
            "serverInfo": {"name": "genpark-json-schema-contract-validator-skill", "version": "1.0.1"},
            "capabilities": {"tools": {}}
        }
        send_response(req_id, res)
    elif method == "tools/list":
        tools = [
            {
                "name": "validate_contract",
                "description": "Validate data against JSON schema constraints (types, required, enum, bounds)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "data": {},
                        "schema": {"type": "object"}
                    },
                    "required": ["data", "schema"]
                }
            },
            {
                "name": "sanitize_and_repair",
                "description": "Sanitize and repair data by supplying defaults and casting safe types",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "data": {},
                        "schema": {"type": "object"}
                    },
                    "required": ["data", "schema"]
                }
            }
        ]
        send_response(req_id, {"tools": tools})
    elif method == "tools/call":
        name = params.get("name")
        args = params.get("arguments", {})
        if name == "validate_contract":
            out = validator.validate_contract(args.get("data"), args.get("schema", {}))
        elif name == "sanitize_and_repair":
            out = validator.sanitize_and_repair(args.get("data"), args.get("schema", {}))
        else:
            send_error(req_id, -32601, f"Unknown tool: {name}")
            return
        send_response(req_id, {"content": [{"type": "text", "text": json.dumps(out, indent=2)}]})

def send_response(req_id, result):
    sys.stdout.write(json.dumps({"jsonrpc": "2.0", "id": req_id, "result": result}) + "\n")
    sys.stdout.flush()

def send_error(req_id, code, message):
    sys.stdout.write(json.dumps({"jsonrpc": "2.0", "id": req_id, "error": {"code": code, "message": message}}) + "\n")
    sys.stdout.flush()

def main():
    for line in sys.stdin:
        if line.strip():
            handle_rpc(line.strip())

if __name__ == "__main__":
    main()
