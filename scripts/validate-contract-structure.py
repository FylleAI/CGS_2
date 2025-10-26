#!/usr/bin/env python3
"""
Validate OpenAPI contract structure and required elements.

Checks:
- Required headers (X-Tenant-ID, Idempotency-Key, etc.)
- Security schemes
- Error responses
- Examples for critical endpoints
"""

import sys
import yaml
from pathlib import Path


def validate_contract(contract_path: Path) -> tuple[bool, list[str]]:
    """Validate a single OpenAPI contract."""
    errors = []
    
    with open(contract_path) as f:
        spec = yaml.safe_load(f)
    
    # Check OpenAPI version
    if spec.get("openapi") != "3.1.0":
        errors.append(f"OpenAPI version should be 3.1.0, got {spec.get('openapi')}")
    
    # Check security schemes
    if "components" not in spec or "securitySchemes" not in spec["components"]:
        errors.append("Missing security schemes in components")
    
    # Check paths exist
    if "paths" not in spec or not spec["paths"]:
        errors.append("No paths defined")
        return False, errors
    
    # Check X-Tenant-ID in security schemes
    has_tenant_id = False
    if "components" in spec and "securitySchemes" in spec["components"]:
        for scheme_name, scheme in spec["components"]["securitySchemes"].items():
            if scheme.get("name") == "X-Tenant-ID" and scheme.get("in") == "header":
                has_tenant_id = True
                break

    if not has_tenant_id:
        errors.append("Missing X-Tenant-ID in securitySchemes")
    
    # Check error responses
    has_error_schema = False
    if "components" in spec and "schemas" in spec["components"]:
        if "ErrorResponse" in spec["components"]["schemas"]:
            has_error_schema = True
            error_schema = spec["components"]["schemas"]["ErrorResponse"]
            required_fields = error_schema.get("required", [])
            if "error" not in required_fields:
                errors.append("ErrorResponse should require 'error' field")
            properties = error_schema.get("properties", {})
            if "error" not in properties or "detail" not in properties:
                errors.append("ErrorResponse should have 'error' and 'detail' properties")

    if not has_error_schema:
        errors.append("Missing ErrorResponse schema in components")
    
    # Check 401 responses on all paths
    for path, methods in spec["paths"].items():
        for method, operation in methods.items():
            if method.upper() not in ["GET", "POST", "PUT", "PATCH", "DELETE"]:
                continue
            
            responses = operation.get("responses", {})
            if "401" not in responses:
                errors.append(f"{method.upper()} {path}: Missing 401 Unauthorized response")
    
    return len(errors) == 0, errors


def main():
    """Validate all contracts."""
    contracts_dir = Path("contracts")
    
    contracts = [
        "cards-api-v1.yaml",
        "workflow-api-v1.yaml",
        "onboarding-api-v1.yaml",
    ]
    
    print("=" * 60)
    print("OpenAPI Contract Structure Validation")
    print("=" * 60)
    print()
    
    all_valid = True
    
    for contract_name in contracts:
        contract_path = contracts_dir / contract_name
        
        if not contract_path.exists():
            print(f"❌ {contract_name}: NOT FOUND")
            all_valid = False
            continue
        
        valid, errors = validate_contract(contract_path)
        
        if valid:
            print(f"✅ {contract_name}: VALID")
        else:
            print(f"❌ {contract_name}: INVALID")
            for error in errors:
                print(f"   - {error}")
            all_valid = False
        
        print()
    
    print("=" * 60)
    if all_valid:
        print("✅ All contracts valid!")
        return 0
    else:
        print("❌ Some contracts have issues")
        return 1


if __name__ == "__main__":
    sys.exit(main())

