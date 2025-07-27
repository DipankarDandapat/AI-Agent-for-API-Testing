import json
from collections import OrderedDict
from typing import Dict, Any

class SimpleTestCaseGenerator:
    """
    Simple test case generator that creates comprehensive test cases
    with proper ordering: Positive, Negative, Boundary, Semantic, Security
    """

    def generate_tests(self, api_info: Dict[str, Any]) -> OrderedDict:
        """
        Generate test cases based on API information
        """
        method = api_info.get('method', 'GET')

        if method.upper() in ['POST', 'PUT', 'PATCH']:
            return self._generate_post_tests(api_info)
        else:
            return self._generate_get_tests(api_info)

    def generate_download_json(self, api_info: Dict[str, Any]) -> OrderedDict:
        """
        Generate test cases specifically for JSON download (without curl_command)
        """
        # Use the same generation logic but ensure no curl_command in output
        result = self.generate_tests(api_info)

        # Remove curl_command from all test cases
        for category in result.values():
            for test_case in category:
                test_case.pop('curl_command', None)

        return result

    def _create_ordered_test_case(self, description, endpoint, method, headers=None,
                                  payload=None, path_params=None, query_params=None,
                                  expected_status=200, expected_schema=None, include_curl=True):
        """
        Create a test case with proper field ordering
        Order: description, endpoint, method, path_params, headers, query_params, payload, expected_status, expected_schema, curl_command
        """
        test_case = OrderedDict()

        # Always include these fields in order
        test_case['description'] = description
        test_case['endpoint'] = endpoint
        test_case['method'] = method

        # Optional fields - only include if they have values
        if path_params:
            test_case['path_params'] = path_params
        if headers:
            test_case['headers'] = headers
        if query_params:
            test_case['query_params'] = query_params
        if payload:
            test_case['payload'] = payload

        test_case['expected_status'] = expected_status

        if expected_schema:
            test_case['expected_schema'] = expected_schema

        # Add curl command if requested
        if include_curl:
            curl_cmd = self._generate_curl_command(endpoint, method, headers, payload, query_params)
            test_case['curl_command'] = curl_cmd

        return test_case

    def _generate_curl_command(self, endpoint, method, headers=None, payload=None, query_params=None):
        """Generate a curl command for the test case"""
        curl_parts = [f"curl -X {method}"]

        if headers:
            for key, value in headers.items():
                curl_parts.append(f"-H '{key}: {value}'")

        if payload:
            curl_parts.append(f"-d '{json.dumps(payload)}'")

        # Add query params to URL
        url = endpoint
        if query_params:
            query_string = "&".join([f"{k}={v}" for k, v in query_params.items()])
            url = f"{endpoint}?{query_string}"

        curl_parts.append(f"'{url}'")

        return " ".join(curl_parts)

    def _generate_post_tests(self, api_info: Dict[str, Any]) -> OrderedDict:
        """
        Generate comprehensive test cases for POST/PUT/PATCH requests with proper ordering
        Order: Positive, Negative, Boundary, Semantic, Security
        Enhanced with additional edge cases and security scenarios
        """
        method = api_info.get('method', 'POST')
        url = api_info.get('url', '')
        headers = api_info.get('headers', {})
        payload = api_info.get('payload', {})
        query_params = api_info.get('query_params', {})
        response = api_info.get('response', {})

        result = OrderedDict()

        # 1. Positive tests (2) - Enhanced
        positive_tests = []

        # Original positive test
        positive_test = self._create_ordered_test_case(
            description="Test with all valid inputs as specified in API information",
            endpoint=url,
            method=method,
            headers=headers,
            query_params=query_params if query_params else None,
            payload=payload,
            expected_status=response.get('status_code', 201)
        )
        positive_tests.append(positive_test)

        # Additional positive test with minimal valid data
        minimal_payload = self._create_minimal_valid_payload(payload)
        positive_test_2 = self._create_ordered_test_case(
            description="Test with minimal valid payload (only required fields)",
            endpoint=url,
            method=method,
            headers=headers,
            query_params=query_params if query_params else None,
            payload=minimal_payload,
            expected_status=response.get('status_code', 201)
        )
        positive_tests.append(positive_test_2)

        result['Positive'] = positive_tests

        # 2. Negative tests (8) - Enhanced from 4 to 8
        negative_tests = []

        # Negative test 1: Empty payload
        negative_test_1 = self._create_ordered_test_case(
            description="Test with empty payload",
            endpoint=url,
            method=method,
            headers=headers,
            query_params=query_params if query_params else None,
            payload={},
            expected_status=422,
            expected_schema={}
        )
        negative_tests.append(negative_test_1)

        # Negative test 2: Missing required fields
        negative_payload_2 = self._remove_required_fields(payload)
        negative_test_2 = self._create_ordered_test_case(
            description="Test with missing required fields",
            endpoint=url,
            method=method,
            headers=headers,
            query_params=query_params if query_params else None,
            payload=negative_payload_2,
            expected_status=422,
            expected_schema={}
        )
        negative_tests.append(negative_test_2)

        # Negative test 3: Invalid data types
        negative_payload_3 = self._invalidate_data_types(payload)
        negative_test_3 = self._create_ordered_test_case(
            description="Test with invalid data types",
            endpoint=url,
            method=method,
            headers=headers,
            query_params=query_params if query_params else None,
            payload=negative_payload_3,
            expected_status=422,
            expected_schema={}
        )
        negative_tests.append(negative_test_3)

        # Negative test 4: Null values
        negative_payload_4 = self._nullify_fields(payload)
        negative_test_4 = self._create_ordered_test_case(
            description="Test with null values in required fields",
            endpoint=url,
            method=method,
            headers=headers,
            query_params=query_params if query_params else None,
            payload=negative_payload_4,
            expected_status=422,
            expected_schema={}
        )
        negative_tests.append(negative_test_4)

        # NEW Negative test 5: Invalid JSON structure
        negative_test_5 = self._create_ordered_test_case(
            description="Test with malformed JSON payload",
            endpoint=url,
            method=method,
            headers=headers,
            query_params=query_params if query_params else None,
            payload="invalid_json_string",
            expected_status=400,
            expected_schema={}
        )
        negative_tests.append(negative_test_5)

        # NEW Negative test 6: Extra/Unknown fields
        negative_payload_6 = self._add_unknown_fields(payload)
        negative_test_6 = self._create_ordered_test_case(
            description="Test with unknown/extra fields in payload",
            endpoint=url,
            method=method,
            headers=headers,
            query_params=query_params if query_params else None,
            payload=negative_payload_6,
            expected_status=422,
            expected_schema={}
        )
        negative_tests.append(negative_test_6)

        # NEW Negative test 7: Invalid enum values
        negative_payload_7 = self._create_invalid_enum_payload(payload)
        negative_test_7 = self._create_ordered_test_case(
            description="Test with invalid enum/choice values",
            endpoint=url,
            method=method,
            headers=headers,
            query_params=query_params if query_params else None,
            payload=negative_payload_7,
            expected_status=422,
            expected_schema={}
        )
        negative_tests.append(negative_test_7)

        # NEW Negative test 8: Invalid format (email, date, etc.)
        negative_payload_8 = self._create_invalid_format_payload(payload)
        negative_test_8 = self._create_ordered_test_case(
            description="Test with invalid format values (email, date, URL)",
            endpoint=url,
            method=method,
            headers=headers,
            query_params=query_params if query_params else None,
            payload=negative_payload_8,
            expected_status=422,
            expected_schema={}
        )
        negative_tests.append(negative_test_8)

        result['Negative'] = negative_tests

        # 3. Boundary tests (12) - Enhanced from 7 to 12
        boundary_tests = []

        # Original boundary tests (1-7)
        boundary_payload_1 = self._create_max_length_payload(payload)
        boundary_test_1 = self._create_ordered_test_case(
            description="Test with maximum length strings (boundary condition)",
            endpoint=url,
            method=method,
            headers=headers,
            query_params=query_params if query_params else None,
            payload=boundary_payload_1,
            expected_status=response.get('status_code', 201)
        )
        boundary_tests.append(boundary_test_1)

        boundary_payload_2 = self._create_min_length_payload(payload)
        boundary_test_2 = self._create_ordered_test_case(
            description="Test with minimum length strings (boundary condition)",
            endpoint=url,
            method=method,
            headers=headers,
            query_params=query_params if query_params else None,
            payload=boundary_payload_2,
            expected_status=response.get('status_code', 201)
        )
        boundary_tests.append(boundary_test_2)

        boundary_payload_3 = self._create_max_numeric_payload(payload)
        boundary_test_3 = self._create_ordered_test_case(
            description="Test with maximum numeric values (boundary condition)",
            endpoint=url,
            method=method,
            headers=headers,
            query_params=query_params if query_params else None,
            payload=boundary_payload_3,
            expected_status=response.get('status_code', 201)
        )
        boundary_tests.append(boundary_test_3)

        boundary_payload_4 = self._create_zero_values_payload(payload)
        boundary_test_4 = self._create_ordered_test_case(
            description="Test with zero values (boundary condition)",
            endpoint=url,
            method=method,
            headers=headers,
            query_params=query_params if query_params else None,
            payload=boundary_payload_4,
            expected_status=response.get('status_code', 201)
        )
        boundary_tests.append(boundary_test_4)

        boundary_payload_5 = self._create_empty_strings_payload(payload)
        boundary_test_5 = self._create_ordered_test_case(
            description="Test with empty strings (boundary condition)",
            endpoint=url,
            method=method,
            headers=headers,
            query_params=query_params if query_params else None,
            payload=boundary_payload_5,
            expected_status=422
        )
        boundary_tests.append(boundary_test_5)

        boundary_payload_6 = self._create_large_payload(payload)
        boundary_test_6 = self._create_ordered_test_case(
            description="Test with very large payload size (boundary condition)",
            endpoint=url,
            method=method,
            headers=headers,
            query_params=query_params if query_params else None,
            payload=boundary_payload_6,
            expected_status=413
        )
        boundary_tests.append(boundary_test_6)

        boundary_payload_7 = self._create_min_numeric_payload(payload)
        boundary_test_7 = self._create_ordered_test_case(
            description="Test with minimum numeric values (boundary condition)",
            endpoint=url,
            method=method,
            headers=headers,
            query_params=query_params if query_params else None,
            payload=boundary_payload_7,
            expected_status=response.get('status_code', 201)
        )
        boundary_tests.append(boundary_test_7)

        # NEW Boundary test 8: Exactly at string length limit
        boundary_payload_8 = self._create_exact_length_payload(payload, 255)
        boundary_test_8 = self._create_ordered_test_case(
            description="Test with strings at exact length limit (255 chars)",
            endpoint=url,
            method=method,
            headers=headers,
            query_params=query_params if query_params else None,
            payload=boundary_payload_8,
            expected_status=response.get('status_code', 201)
        )
        boundary_tests.append(boundary_test_8)

        # NEW Boundary test 9: One character over limit
        boundary_payload_9 = self._create_exact_length_payload(payload, 256)
        boundary_test_9 = self._create_ordered_test_case(
            description="Test with strings one character over limit (256 chars)",
            endpoint=url,
            method=method,
            headers=headers,
            query_params=query_params if query_params else None,
            payload=boundary_payload_9,
            expected_status=422
        )
        boundary_tests.append(boundary_test_9)

        # NEW Boundary test 10: Maximum array/list size
        boundary_payload_10 = self._create_max_array_payload(payload)
        boundary_test_10 = self._create_ordered_test_case(
            description="Test with maximum array/list size (boundary condition)",
            endpoint=url,
            method=method,
            headers=headers,
            query_params=query_params if query_params else None,
            payload=boundary_payload_10,
            expected_status=response.get('status_code', 201)
        )
        boundary_tests.append(boundary_test_10)

        # NEW Boundary test 11: Empty arrays
        boundary_payload_11 = self._create_empty_array_payload(payload)
        boundary_test_11 = self._create_ordered_test_case(
            description="Test with empty arrays (boundary condition)",
            endpoint=url,
            method=method,
            headers=headers,
            query_params=query_params if query_params else None,
            payload=boundary_payload_11,
            expected_status=response.get('status_code', 201)
        )
        boundary_tests.append(boundary_test_11)

        # NEW Boundary test 12: Float precision limits
        boundary_payload_12 = self._create_precision_float_payload(payload)
        boundary_test_12 = self._create_ordered_test_case(
            description="Test with maximum float precision values (boundary condition)",
            endpoint=url,
            method=method,
            headers=headers,
            query_params=query_params if query_params else None,
            payload=boundary_payload_12,
            expected_status=response.get('status_code', 201)
        )
        boundary_tests.append(boundary_test_12)

        result['Boundary'] = boundary_tests

        # 4. Semantic tests (6) - Enhanced from 3 to 6
        semantic_tests = []

        # Original semantic tests (1-3)
        semantic_payload_1 = self._modify_payload_for_semantic(payload)
        semantic_test_1 = self._create_ordered_test_case(
            description="Test with multiline text in description field",
            endpoint=url,
            method=method,
            headers=headers,
            query_params=query_params if query_params else None,
            payload=semantic_payload_1,
            expected_status=response.get('status_code', 201)
        )
        semantic_tests.append(semantic_test_1)

        semantic_payload_2 = self._add_special_chars_to_payload(payload)
        semantic_test_2 = self._create_ordered_test_case(
            description="Test with special characters in input fields",
            endpoint=url,
            method=method,
            headers=headers,
            query_params=query_params if query_params else None,
            payload=semantic_payload_2,
            expected_status=response.get('status_code', 201)
        )
        semantic_tests.append(semantic_test_2)

        semantic_payload_3 = self._add_unicode_to_payload(payload)
        semantic_test_3 = self._create_ordered_test_case(
            description="Test with Unicode characters in text fields",
            endpoint=url,
            method=method,
            headers=headers,
            query_params=query_params if query_params else None,
            payload=semantic_payload_3,
            expected_status=response.get('status_code', 201)
        )
        semantic_tests.append(semantic_test_3)

        # NEW Semantic test 4: Leading/trailing whitespace
        semantic_payload_4 = self._add_whitespace_to_payload(payload)
        semantic_test_4 = self._create_ordered_test_case(
            description="Test with leading and trailing whitespace in text fields",
            endpoint=url,
            method=method,
            headers=headers,
            query_params=query_params if query_params else None,
            payload=semantic_payload_4,
            expected_status=response.get('status_code', 201)
        )
        semantic_tests.append(semantic_test_4)

        # NEW Semantic test 5: Mixed case sensitivity
        semantic_payload_5 = self._create_case_sensitive_payload(payload)
        semantic_test_5 = self._create_ordered_test_case(
            description="Test with mixed case values for case-sensitive fields",
            endpoint=url,
            method=method,
            headers=headers,
            query_params=query_params if query_params else None,
            payload=semantic_payload_5,
            expected_status=response.get('status_code', 201)
        )
        semantic_tests.append(semantic_test_5)

        # NEW Semantic test 6: Numeric strings vs numbers
        semantic_payload_6 = self._create_numeric_string_payload(payload)
        semantic_test_6 = self._create_ordered_test_case(
            description="Test with numeric values as strings vs actual numbers",
            endpoint=url,
            method=method,
            headers=headers,
            query_params=query_params if query_params else None,
            payload=semantic_payload_6,
            expected_status=response.get('status_code', 201)
        )
        semantic_tests.append(semantic_test_6)

        result['Semantic'] = semantic_tests

        # 5. Security tests (12) - Enhanced from 6 to 12
        security_tests = []

        # Original security tests (1-6)
        security_payload_1 = self._create_sql_injection_payload(payload)
        security_test_1 = self._create_ordered_test_case(
            description="Test with SQL injection patterns in input fields",
            endpoint=url,
            method=method,
            headers=headers,
            query_params=query_params if query_params else None,
            payload=security_payload_1,
            expected_status=400
        )
        security_tests.append(security_test_1)

        security_payload_2 = self._create_xss_payload(payload)
        security_test_2 = self._create_ordered_test_case(
            description="Test with XSS (Cross-Site Scripting) patterns in input fields",
            endpoint=url,
            method=method,
            headers=headers,
            query_params=query_params if query_params else None,
            payload=security_payload_2,
            expected_status=400
        )
        security_tests.append(security_test_2)

        security_payload_3 = self._create_command_injection_payload(payload)
        security_test_3 = self._create_ordered_test_case(
            description="Test with command injection patterns in input fields",
            endpoint=url,
            method=method,
            headers=headers,
            query_params=query_params if query_params else None,
            payload=security_payload_3,
            expected_status=400
        )
        security_tests.append(security_test_3)

        security_payload_4 = self._create_path_traversal_payload(payload)
        security_test_4 = self._create_ordered_test_case(
            description="Test with path traversal patterns in input fields",
            endpoint=url,
            method=method,
            headers=headers,
            query_params=query_params if query_params else None,
            payload=security_payload_4,
            expected_status=400
        )
        security_tests.append(security_test_4)

        security_headers_5 = {k: v for k, v in headers.items() if
                              'authorization' not in k.lower() and 'token' not in k.lower()}
        security_test_5 = self._create_ordered_test_case(
            description="Test without authentication headers (security validation)",
            endpoint=url,
            method=method,
            headers=security_headers_5,
            query_params=query_params if query_params else None,
            payload=payload,
            expected_status=401
        )
        security_tests.append(security_test_5)

        security_headers_6 = headers.copy()
        security_headers_6['content-type'] = 'text/plain'
        security_test_6 = self._create_ordered_test_case(
            description="Test with invalid content-type header (security validation)",
            endpoint=url,
            method=method,
            headers=security_headers_6,
            query_params=query_params if query_params else None,
            payload=payload,
            expected_status=415
        )
        security_tests.append(security_test_6)

        # NEW Security test 7: LDAP injection
        security_payload_7 = self._create_ldap_injection_payload(payload)
        security_test_7 = self._create_ordered_test_case(
            description="Test with LDAP injection patterns in input fields",
            endpoint=url,
            method=method,
            headers=headers,
            query_params=query_params if query_params else None,
            payload=security_payload_7,
            expected_status=400
        )
        security_tests.append(security_test_7)

        # NEW Security test 8: NoSQL injection
        security_payload_8 = self._create_nosql_injection_payload(payload)
        security_test_8 = self._create_ordered_test_case(
            description="Test with NoSQL injection patterns in input fields",
            endpoint=url,
            method=method,
            headers=headers,
            query_params=query_params if query_params else None,
            payload=security_payload_8,
            expected_status=400
        )
        security_tests.append(security_test_8)

        # NEW Security test 9: XXE (XML External Entity) injection
        security_payload_9 = self._create_xxe_payload(payload)
        security_test_9 = self._create_ordered_test_case(
            description="Test with XXE (XML External Entity) patterns in input fields",
            endpoint=url,
            method=method,
            headers=headers,
            query_params=query_params if query_params else None,
            payload=security_payload_9,
            expected_status=400
        )
        security_tests.append(security_test_9)

        # NEW Security test 10: Server-Side Template Injection (SSTI)
        security_payload_10 = self._create_ssti_payload(payload)
        security_test_10 = self._create_ordered_test_case(
            description="Test with Server-Side Template Injection patterns",
            endpoint=url,
            method=method,
            headers=headers,
            query_params=query_params if query_params else None,
            payload=security_payload_10,
            expected_status=400
        )
        security_tests.append(security_test_10)

        # NEW Security test 11: Malicious file upload patterns
        security_payload_11 = self._create_malicious_file_payload(payload)
        security_test_11 = self._create_ordered_test_case(
            description="Test with malicious file upload patterns",
            endpoint=url,
            method=method,
            headers=headers,
            query_params=query_params if query_params else None,
            payload=security_payload_11,
            expected_status=400
        )
        security_tests.append(security_test_11)

        # NEW Security test 12: Rate limiting test
        security_test_12 = self._create_ordered_test_case(
            description="Test for rate limiting protection (security validation)",
            endpoint=url,
            method=method,
            headers=headers,
            query_params=query_params if query_params else None,
            payload=payload,
            expected_status=429
        )
        security_tests.append(security_test_12)

        result['Security'] = security_tests

        return result

    # Additional helper methods for new test cases

    def _create_minimal_valid_payload(self, payload: Dict) -> Dict:
        """Create payload with only required fields"""
        # This is a simplified approach - in real implementation,
        # you'd need schema information to determine required fields
        essential_keys = ['id', 'name', 'title', 'email', 'username']
        minimal = {}
        for key, value in payload.items():
            if any(essential in key.lower() for essential in essential_keys):
                minimal[key] = value
        return minimal if minimal else payload

    def _add_unknown_fields(self, payload: Dict) -> Dict:
        """Add unknown/extra fields to payload"""
        modified = payload.copy()
        modified.update({
            "unknown_field_1": "unexpected_value",
            "extra_param": 999,
            "invalid_key": ["unexpected", "array"],
            "nested_unknown": {"surprise": "field"}
        })
        return modified

    def _create_invalid_enum_payload(self, payload: Dict) -> Dict:
        """Create payload with invalid enum values"""
        modified = payload.copy()
        enum_fields = ['status', 'type', 'category', 'role', 'priority']
        for key, value in modified.items():
            if any(enum_field in key.lower() for enum_field in enum_fields):
                modified[key] = "INVALID_ENUM_VALUE"
        return modified

    def _create_invalid_format_payload(self, payload: Dict) -> Dict:
        """Create payload with invalid format values"""
        modified = payload.copy()
        for key, value in modified.items():
            if isinstance(value, str):
                if 'email' in key.lower():
                    modified[key] = "invalid.email.format"
                elif 'date' in key.lower():
                    modified[key] = "not-a-date"
                elif 'url' in key.lower():
                    modified[key] = "not://valid.url"
                elif 'phone' in key.lower():
                    modified[key] = "not-a-phone-number"
        return modified

    def _create_exact_length_payload(self, payload: Dict, length: int) -> Dict:
        """Create payload with strings of exact length"""
        modified = payload.copy()
        for key, value in modified.items():
            if isinstance(value, str):
                modified[key] = "A" * length
        return modified

    def _create_max_array_payload(self, payload: Dict) -> Dict:
        """Create payload with maximum array size"""
        modified = payload.copy()
        large_array = ["item"] * 1000
        for key, value in modified.items():
            if isinstance(value, list):
                modified[key] = large_array
            elif 'tags' in key.lower() or 'items' in key.lower():
                modified[key] = large_array
        return modified

    def _create_empty_array_payload(self, payload: Dict) -> Dict:
        """Create payload with empty arrays"""
        modified = payload.copy()
        for key, value in modified.items():
            if isinstance(value, list):
                modified[key] = []
        return modified

    def _create_precision_float_payload(self, payload: Dict) -> Dict:
        """Create payload with high precision float values"""
        modified = payload.copy()
        for key, value in modified.items():
            if isinstance(value, float):
                modified[key] = 3.141592653589793238462643383279502884197
            elif isinstance(value, (int, str)) and 'price' in key.lower():
                modified[key] = 999999.999999999999999999
        return modified

    def _add_whitespace_to_payload(self, payload: Dict) -> Dict:
        """Add leading/trailing whitespace to payload fields"""
        modified = payload.copy()
        for key, value in modified.items():
            if isinstance(value, str):
                modified[key] = f"  {value}  \t\n"
        return modified

    def _create_case_sensitive_payload(self, payload: Dict) -> Dict:
        """Create payload with mixed case values"""
        modified = payload.copy()
        for key, value in modified.items():
            if isinstance(value, str):
                # Alternate case for each character
                modified[key] = ''.join(c.upper() if i % 2 == 0 else c.lower()for i, c in enumerate(value))
        return modified

    def _create_numeric_string_payload(self, payload: Dict) -> Dict:
        """Create payload with numeric values as strings"""
        modified = payload.copy()
        for key, value in modified.items():
            if isinstance(value, (int, float)):
                modified[key] = str(value)
            elif isinstance(value, str) and value.isdigit():
                modified[key] = int(value)
        return modified

    def _create_ldap_injection_payload(self, payload: Dict) -> Dict:
        """Create payload with LDAP injection patterns"""
        modified = payload.copy()
        ldap_payloads = ["*)(uid=*))(|(uid=*", "admin)(&(password=*))", "*()|%00"]
        for key, value in modified.items():
            if isinstance(value, str):
                modified[key] = ldap_payloads[0]
        return modified

    def _create_nosql_injection_payload(self, payload: Dict) -> Dict:
        """Create payload with NoSQL injection patterns"""
        modified = payload.copy()
        for key, value in modified.items():
            if isinstance(value, str):
                modified[key] = {"$ne": None}
            elif isinstance(value, (int, float)):
                modified[key] = {"$gt": ""}
        return modified

    def _create_xxe_payload(self, payload: Dict) -> Dict:
        """Create payload with XXE patterns"""
        modified = payload.copy()
        xxe_pattern = "<?xml version='1.0'?><!DOCTYPE root [<!ENTITY test SYSTEM 'file:///etc/passwd'>]><root>&test;</root>"
        for key, value in modified.items():
            if isinstance(value, str):
                modified[key] = xxe_pattern
        return modified

    def _create_ssti_payload(self, payload: Dict) -> Dict:
        """Create payload with Server-Side Template Injection patterns"""
        modified = payload.copy()
        ssti_patterns = ["{{7*7}}", "${7*7}", "<%=7*7%>", "#{7*7}"]
        for key, value in modified.items():
            if isinstance(value, str):
                modified[key] = ssti_patterns[0]
        return modified

    def _create_malicious_file_payload(self, payload: Dict) -> Dict:
        """Create payload with malicious file patterns"""
        modified = payload.copy()
        malicious_patterns = [
            "../../../etc/passwd",
            "test.php%00.jpg",
            "script.exe",
            "malware.bat"
        ]
        for key, value in modified.items():
            if 'file' in key.lower() or 'upload' in key.lower():
                modified[key] = malicious_patterns[0]
        return modified

    def _generate_get_tests(self, api_info: Dict[str, Any]) -> OrderedDict:
        """
        Generate comprehensive test cases for GET requests with proper ordering
        Order: Positive, Negative, Boundary, Semantic, Security
        """
        method = api_info.get('method', 'GET')
        url = api_info.get('url', '')
        headers = api_info.get('headers', {})
        query_params = api_info.get('query_params', {})
        response = api_info.get('response', {})

        result = OrderedDict()

        # 1. Positive tests (2)
        positive_tests = []

        # Positive test 1: Valid parameters
        positive_test_1 = self._create_ordered_test_case(
            description="Test fetching data with valid parameters",
            endpoint=url,
            method=method,
            headers=headers,
            query_params=query_params if query_params else None,
            expected_status=response.get('status_code', 200)
        )
        positive_tests.append(positive_test_1)

        # Positive test 2: Minimal valid request
        minimal_headers = {"accept": "application/json"}
        positive_test_2 = self._create_ordered_test_case(
            description="Test with minimal valid headers and no query parameters",
            endpoint=url,
            method=method,
            headers=minimal_headers,
            query_params=None,
            expected_status=response.get('status_code', 200)
        )
        positive_tests.append(positive_test_2)

        result['Positive'] = positive_tests

        # 2. Negative tests (8)
        negative_tests = []

        # Negative test 1: Invalid endpoint
        negative_test_1 = self._create_ordered_test_case(
            description="Test with invalid endpoint path",
            endpoint=url + "/invalid",
            method=method,
            headers=headers,
            query_params=query_params if query_params else None,
            expected_status=404,
            expected_schema={}
        )
        negative_tests.append(negative_test_1)

        # Negative test 2: Invalid query parameters
        invalid_query_params = {"invalid_param": "invalid_value"}
        negative_test_2 = self._create_ordered_test_case(
            description="Test with invalid query parameters",
            endpoint=url,
            method=method,
            headers=headers,
            query_params=invalid_query_params,
            expected_status=400,
            expected_schema={}
        )
        negative_tests.append(negative_test_2)

        # Negative test 3: Missing required headers
        minimal_headers = {"accept": "application/json"}
        negative_test_3 = self._create_ordered_test_case(
            description="Test with missing required headers",
            endpoint=url,
            method=method,
            headers=minimal_headers,
            query_params=query_params if query_params else None,
            expected_status=400,
            expected_schema={}
        )
        negative_tests.append(negative_test_3)

        # Negative test 4: Malformed request
        negative_test_4 = self._create_ordered_test_case(
            description="Test with malformed request structure",
            endpoint=url.replace("https://", "http://"),
            method=method,
            headers=headers,
            query_params=query_params if query_params else None,
            expected_status=400,
            expected_schema={}
        )
        negative_tests.append(negative_test_4)

        # Negative test 5: Non-existent resource ID
        nonexistent_query_params = {"id": "999999999"}
        negative_test_5 = self._create_ordered_test_case(
            description="Test with non-existent resource ID",
            endpoint=url,
            method=method,
            headers=headers,
            query_params=nonexistent_query_params,
            expected_status=404,
            expected_schema={}
        )
        negative_tests.append(negative_test_5)

        # Negative test 6: Invalid HTTP method
        negative_test_6 = self._create_ordered_test_case(
            description="Test with invalid HTTP method",
            endpoint=url,
            method="INVALID",
            headers=headers,
            query_params=query_params if query_params else None,
            expected_status=405,
            expected_schema={}
        )
        negative_tests.append(negative_test_6)

        # Negative test 7: Malformed query parameter values
        malformed_query_params = {"date": "invalid-date-format", "number": "not-a-number"}
        negative_test_7 = self._create_ordered_test_case(
            description="Test with malformed query parameter values",
            endpoint=url,
            method=method,
            headers=headers,
            query_params=malformed_query_params,
            expected_status=400,
            expected_schema={}
        )
        negative_tests.append(negative_test_7)

        # Negative test 8: Duplicate query parameters
        duplicate_url = url + "?param=value1&param=value2"
        negative_test_8 = self._create_ordered_test_case(
            description="Test with duplicate query parameter names",
            endpoint=duplicate_url,
            method=method,
            headers=headers,
            query_params=None,
            expected_status=400,
            expected_schema={}
        )
        negative_tests.append(negative_test_8)

        result['Negative'] = negative_tests

        # 3. Boundary tests (10)
        boundary_tests = []

        # Boundary test 1: Maximum query parameter length
        max_query_params = {k: "A" * 1000 for k, v in query_params.items()} if query_params else {"test": "A" * 1000}
        boundary_test_1 = self._create_ordered_test_case(
            description="Test with maximum length query parameters (boundary condition)",
            endpoint=url,
            method=method,
            headers=headers,
            query_params=max_query_params,
            expected_status=414
        )
        boundary_tests.append(boundary_test_1)

        # Boundary test 2: Empty query parameters
        boundary_test_2 = self._create_ordered_test_case(
            description="Test with empty query parameters (boundary condition)",
            endpoint=url,
            method=method,
            headers=headers,
            query_params={},
            expected_status=response.get('status_code', 200)
        )
        boundary_tests.append(boundary_test_2)

        # Boundary test 3: Zero values in numeric parameters
        zero_query_params = {"id": "0", "page": "0", "limit": "0"}
        boundary_test_3 = self._create_ordered_test_case(
            description="Test with zero values in numeric parameters (boundary condition)",
            endpoint=url,
            method=method,
            headers=headers,
            query_params=zero_query_params,
            expected_status=response.get('status_code', 200)
        )
        boundary_tests.append(boundary_test_3)

        # Boundary test 4: Negative values in numeric parameters
        negative_query_params = {"id": "-1", "page": "-5"}
        boundary_test_4 = self._create_ordered_test_case(
            description="Test with negative values in numeric parameters (boundary condition)",
            endpoint=url,
            method=method,
            headers=headers,
            query_params=negative_query_params,
            expected_status=400
        )
        boundary_tests.append(boundary_test_4)

        # Boundary test 5: Very large numeric values
        large_query_params = {"id": "999999999", "limit": "2147483647"}
        boundary_test_5 = self._create_ordered_test_case(
            description="Test with very large numeric values (boundary condition)",
            endpoint=url,
            method=method,
            headers=headers,
            query_params=large_query_params,
            expected_status=400
        )
        boundary_tests.append(boundary_test_5)

        # Boundary test 6: Maximum URL length
        very_long_url = url + "?" + "&".join([f"param{i}=value{i}" for i in range(100)])
        boundary_test_6 = self._create_ordered_test_case(
            description="Test with maximum URL length (boundary condition)",
            endpoint=very_long_url,
            method=method,
            headers=headers,
            query_params=None,
            expected_status=414
        )
        boundary_tests.append(boundary_test_6)

        # Boundary test 7: Single character query parameters
        single_char_params = {"q": "a", "s": "1"}
        boundary_test_7 = self._create_ordered_test_case(
            description="Test with single character query parameters (boundary condition)",
            endpoint=url,
            method=method,
            headers=headers,
            query_params=single_char_params,
            expected_status=response.get('status_code', 200)
        )
        boundary_tests.append(boundary_test_7)

        # Boundary test 8: Maximum integer boundary values
        max_int_params = {"int32": "2147483647", "int64": "9223372036854775807"}
        boundary_test_8 = self._create_ordered_test_case(
            description="Test with maximum integer boundary values (boundary condition)",
            endpoint=url,
            method=method,
            headers=headers,
            query_params=max_int_params,
            expected_status=response.get('status_code', 200)
        )
        boundary_tests.append(boundary_test_8)

        # Boundary test 9: Minimum integer boundary values
        min_int_params = {"int32": "-2147483648", "int64": "-9223372036854775808"}
        boundary_test_9 = self._create_ordered_test_case(
            description="Test with minimum integer boundary values (boundary condition)",
            endpoint=url,
            method=method,
            headers=headers,
            query_params=min_int_params,
            expected_status=response.get('status_code', 200)
        )
        boundary_tests.append(boundary_test_9)

        # Boundary test 10: Empty string query parameters
        empty_string_params = {"search": "", "filter": ""}
        boundary_test_10 = self._create_ordered_test_case(
            description="Test with empty string query parameters (boundary condition)",
            endpoint=url,
            method=method,
            headers=headers,
            query_params=empty_string_params,
            expected_status=response.get('status_code', 200)
        )
        boundary_tests.append(boundary_test_10)

        result['Boundary'] = boundary_tests

        # 4. Semantic tests (6)
        semantic_tests = []

        # Semantic test 1: Special characters in query parameters
        special_query_params = {"search": "test@#$%^&*()"}
        semantic_test_1 = self._create_ordered_test_case(
            description="Test with special characters in query parameters",
            endpoint=url,
            method=method,
            headers=headers,
            query_params=special_query_params,
            expected_status=response.get('status_code', 200)
        )
        semantic_tests.append(semantic_test_1)

        # Semantic test 2: Unicode characters in query parameters
        unicode_query_params = {"search": "测试数据🚀"}
        semantic_test_2 = self._create_ordered_test_case(
            description="Test with Unicode characters in query parameters",
            endpoint=url,
            method=method,
            headers=headers,
            query_params=unicode_query_params,
            expected_status=response.get('status_code', 200)
        )
        semantic_tests.append(semantic_test_2)

        # Semantic test 3: URL encoded characters
        encoded_query_params = {"search": "hello%20world"}
        semantic_test_3 = self._create_ordered_test_case(
            description="Test with URL encoded characters in query parameters",
            endpoint=url,
            method=method,
            headers=headers,
            query_params=encoded_query_params,
            expected_status=response.get('status_code', 200)
        )
        semantic_tests.append(semantic_test_3)

        # Semantic test 4: Case sensitivity in query parameters
        case_sensitive_params = {"Search": "test", "FILTER": "value", "search": "test2"}
        semantic_test_4 = self._create_ordered_test_case(
            description="Test with case-sensitive query parameter names",
            endpoint=url,
            method=method,
            headers=headers,
            query_params=case_sensitive_params,
            expected_status=response.get('status_code', 200)
        )
        semantic_tests.append(semantic_test_4)

        # Semantic test 5: Boolean-like string values
        boolean_params = {"active": "true", "enabled": "false", "visible": "1", "hidden": "0"}
        semantic_test_5 = self._create_ordered_test_case(
            description="Test with boolean-like string values in query parameters",
            endpoint=url,
            method=method,
            headers=headers,
            query_params=boolean_params,
            expected_status=response.get('status_code', 200)
        )
        semantic_tests.append(semantic_test_5)

        # Semantic test 6: Date and time formats
        datetime_params = {"start_date": "2024-01-01", "end_date": "2024-12-31T23:59:59Z", "timestamp": "1640995200"}
        semantic_test_6 = self._create_ordered_test_case(
            description="Test with various date and time formats in query parameters",
            endpoint=url,
            method=method,
            headers=headers,
            query_params=datetime_params,
            expected_status=response.get('status_code', 200)
        )
        semantic_tests.append(semantic_test_6)

        result['Semantic'] = semantic_tests

        # 5. Security tests (10)
        security_tests = []

        # Security test 1: SQL injection in query parameters
        sql_query_params = {"search": "'; DROP TABLE users; --"}
        security_test_1 = self._create_ordered_test_case(
            description="Test with SQL injection patterns in query parameters",
            endpoint=url,
            method=method,
            headers=headers,
            query_params=sql_query_params,
            expected_status=400
        )
        security_tests.append(security_test_1)

        # Security test 2: XSS in query parameters
        xss_query_params = {"search": "<script>alert('XSS')</script>"}
        security_test_2 = self._create_ordered_test_case(
            description="Test with XSS patterns in query parameters",
            endpoint=url,
            method=method,
            headers=headers,
            query_params=xss_query_params,
            expected_status=400
        )
        security_tests.append(security_test_2)

        # Security test 3: Path traversal in query parameters
        path_query_params = {"file": "../../../etc/passwd"}
        security_test_3 = self._create_ordered_test_case(
            description="Test with path traversal patterns in query parameters",
            endpoint=url,
            method=method,
            headers=headers,
            query_params=path_query_params,
            expected_status=400
        )
        security_tests.append(security_test_3)

        # Security test 4: Missing authentication headers
        no_auth_headers = {k: v for k, v in headers.items() if
                           'authorization' not in k.lower() and 'token' not in k.lower()}
        security_test_4 = self._create_ordered_test_case(
            description="Test without authentication headers (security validation)",
            endpoint=url,
            method=method,
            headers=no_auth_headers,
            query_params=query_params if query_params else None,
            expected_status=401
        )
        security_tests.append(security_test_4)

        # Security test 5: Invalid accept header
        invalid_headers = headers.copy()
        invalid_headers['accept'] = 'text/html'
        security_test_5 = self._create_ordered_test_case(
            description="Test with invalid accept header (security validation)",
            endpoint=url,
            method=method,
            headers=invalid_headers,
            query_params=query_params if query_params else None,
            expected_status=406
        )
        security_tests.append(security_test_5)

        # Security test 6: Command injection in query parameters
        command_injection_params = {"cmd": "; ls -la", "exec": "| cat /etc/passwd"}
        security_test_6 = self._create_ordered_test_case(
            description="Test with command injection patterns in query parameters",
            endpoint=url,
            method=method,
            headers=headers,
            query_params=command_injection_params,
            expected_status=400
        )
        security_tests.append(security_test_6)

        # Security test 7: LDAP injection in query parameters
        ldap_injection_params = {"user": "admin)(|(password=*))", "filter": "*)(uid=*))(|(uid=*"}
        security_test_7 = self._create_ordered_test_case(
            description="Test with LDAP injection patterns in query parameters",
            endpoint=url,
            method=method,
            headers=headers,
            query_params=ldap_injection_params,
            expected_status=400
        )
        security_tests.append(security_test_7)

        # Security test 8: NoSQL injection in query parameters
        nosql_injection_params = {"id": "1'; return true; //", "filter": "{$where: 'this.name == this.name'}"}
        security_test_8 = self._create_ordered_test_case(
            description="Test with NoSQL injection patterns in query parameters",
            endpoint=url,
            method=method,
            headers=headers,
            query_params=nosql_injection_params,
            expected_status=400
        )
        security_tests.append(security_test_8)

        # Security test 9: HTTP header injection
        header_injection_headers = headers.copy()
        header_injection_headers['X-Custom-Header'] = "value\r\nX-Injected: malicious"
        security_test_9 = self._create_ordered_test_case(
            description="Test with HTTP header injection patterns",
            endpoint=url,
            method=method,
            headers=header_injection_headers,
            query_params=query_params if query_params else None,
            expected_status=400
        )
        security_tests.append(security_test_9)

        # Security test 10: Server-side template injection
        template_injection_params = {"template": "{{7*7}}", "expr": "${7*7}", "code": "<%=7*7%>"}
        security_test_10 = self._create_ordered_test_case(
            description="Test with server-side template injection patterns in query parameters",
            endpoint=url,
            method=method,
            headers=headers,
            query_params=template_injection_params,
            expected_status=400
        )
        security_tests.append(security_test_10)

        result['Security'] = security_tests

        return result

    # Helper methods for payload modification
    def _modify_payload_for_semantic(self, payload: Dict) -> Dict:
        """Modify payload for semantic testing"""
        modified = payload.copy()
        for key, value in modified.items():
            if isinstance(value, str) and 'description' in key.lower():
                modified[key] = "This is line 1\\nThis is line 2\\nThis is line 3"
        return modified

    def _add_special_chars_to_payload(self, payload: Dict) -> Dict:
        """Add special characters to payload fields"""
        modified = payload.copy()
        for key, value in modified.items():
            if isinstance(value, str):
                modified[key] = f"{value} !@#$%^&*()_+-="
        return modified

    def _add_unicode_to_payload(self, payload: Dict) -> Dict:
        """Add Unicode characters to payload fields"""
        modified = payload.copy()
        for key, value in modified.items():
            if isinstance(value, str):
                modified[key] = f"{value} 测试 🚀 ñáéíóú"
        return modified

    def _remove_required_fields(self, payload: Dict) -> Dict:
        """Remove some fields to test missing required fields"""
        modified = payload.copy()
        keys_to_remove = list(modified.keys())[:1]
        for key in keys_to_remove:
            modified.pop(key, None)
        return modified

    def _invalidate_data_types(self, payload: Dict) -> Dict:
        """Change data types to invalid ones"""
        modified = payload.copy()
        for key, value in modified.items():
            if isinstance(value, str):
                modified[key] = 12345
            elif isinstance(value, (int, float)):
                modified[key] = "invalid_number"
        return modified

    def _nullify_fields(self, payload: Dict) -> Dict:
        """Set fields to null values"""
        modified = payload.copy()
        for key in modified.keys():
            modified[key] = None
        return modified

    # Boundary test helper methods
    def _create_max_length_payload(self, payload: Dict) -> Dict:
        """Create payload with maximum length strings"""
        modified = payload.copy()
        for key, value in modified.items():
            if isinstance(value, str):
                modified[key] = "A" * 1000
        return modified

    def _create_min_length_payload(self, payload: Dict) -> Dict:
        """Create payload with minimum length strings"""
        modified = payload.copy()
        for key, value in modified.items():
            if isinstance(value, str):
                modified[key] = "A"
        return modified

    def _create_max_numeric_payload(self, payload: Dict) -> Dict:
        """Create payload with maximum numeric values"""
        modified = payload.copy()
        for key, value in modified.items():
            if isinstance(value, int):
                modified[key] = 2147483647
            elif isinstance(value, float):
                modified[key] = 1.7976931348623157e+308
        return modified

    def _create_min_numeric_payload(self, payload: Dict) -> Dict:
        """Create payload with minimum numeric values"""
        modified = payload.copy()
        for key, value in modified.items():
            if isinstance(value, int):
                modified[key] = -2147483648
            elif isinstance(value, float):
                modified[key] = -1.7976931348623157e+308
        return modified

    def _create_zero_values_payload(self, payload: Dict) -> Dict:
        """Create payload with zero values"""
        modified = payload.copy()
        for key, value in modified.items():
            if isinstance(value, (int, float)):
                modified[key] = 0
        return modified

    def _create_empty_strings_payload(self, payload: Dict) -> Dict:
        """Create payload with empty strings"""
        modified = payload.copy()
        for key, value in modified.items():
            if isinstance(value, str):
                modified[key] = ""
        return modified

    def _create_large_payload(self, payload: Dict) -> Dict:
        """Create very large payload"""
        modified = payload.copy()
        for i in range(100):  # Reduced from 1000 to avoid too large payload
            modified[f"large_field_{i}"] = "A" * 100
        return modified

    # Security test helper methods
    def _create_sql_injection_payload(self, payload: Dict) -> Dict:
        """Create payload with SQL injection patterns"""
        modified = payload.copy()
        for key, value in modified.items():
            if isinstance(value, str):
                modified[key] = "'; DROP TABLE users; --"
        return modified

    def _create_xss_payload(self, payload: Dict) -> Dict:
        """Create payload with XSS patterns"""
        modified = payload.copy()
        for key, value in modified.items():
            if isinstance(value, str):
                modified[key] = "<script>alert('XSS')</script>"
        return modified

    def _create_command_injection_payload(self, payload: Dict) -> Dict:
        """Create payload with command injection patterns"""
        modified = payload.copy()
        for key, value in modified.items():
            if isinstance(value, str):
                modified[key] = "; ls -la"
        return modified

    def _create_path_traversal_payload(self, payload: Dict) -> Dict:
        """Create payload with path traversal patterns"""
        modified = payload.copy()
        for key, value in modified.items():
            if isinstance(value, str):
                modified[key] = "../../../etc/passwd"
        return modified

