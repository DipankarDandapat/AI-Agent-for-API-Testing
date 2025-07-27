import json
import os
from openai import OpenAI
from typing import Dict, Any

from src.services.simple_test_generator import SimpleTestCaseGenerator


class TestCaseGenerator:
    def __init__(self):
        # Initialize OpenAI client
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY', 'your-api-key-here'))
        self.fallback_generator = SimpleTestCaseGenerator()

    # def generate_test_cases(self, api_info: Dict[str, Any]) -> Dict[str, Any]:
    #     """
    #     Generate test cases based on API information
    #     """
    #     method = api_info.get('method', 'GET')
    #     url = api_info.get('url', '')
    #     headers = api_info.get('headers', {})
    #     payload = api_info.get('payload', {})
    #     query_params = api_info.get('query_params', {})
    #     response = api_info.get('response', {})
    #
    #     # Create prompt based on method type
    #     if method.upper() in ['POST', 'PUT', 'PATCH']:
    #         prompt = self._create_post_prompt(api_info)
    #     else:
    #         prompt = self._create_get_prompt(api_info)
    #
    #     try:
    #         # Call OpenAI API
    #         response = self.client.chat.completions.create(
    #             model="gpt-4",
    #             messages=[
    #                 {
    #                     "role": "system",
    #                     "content": "You are an expert API testing specialist. Generate comprehensive test cases in the exact JSON format specified. Include positive, negative, boundary value, and security test cases."
    #                 },
    #                 {
    #                     "role": "user",
    #                     "content": prompt
    #                 }
    #             ],
    #             temperature=0.7,
    #             max_tokens=4000
    #         )
    #
    #         # Parse the response
    #         test_cases_text = response.choices[0].message.content
    #         test_cases = json.loads(test_cases_text)
    #
    #         return test_cases
    #
    #     except Exception as e:
    #         print("OpenAI fail to generate test case")
    #         print(e)
    #         # Return fallback test cases if OpenAI fails
    #         print("call generate fallback tests")
    #         # return self._generate_fallback_tests(api_info)
    #         return self.fallback_generator.generate_tests(api_info)
    def generate_test_cases(self, api_info: Dict[str, Any], include_curl: bool = True) -> Dict[str, Any]:
        """
        Generate test cases based on API information
        """
        method = api_info.get('method', 'GET')
        url = api_info.get('url', '')
        headers = api_info.get('headers', {})
        payload = api_info.get('payload', {})
        query_params = api_info.get('query_params', {})

        # Create prompt based on method type
        if method.upper() in ['POST', 'PUT', 'PATCH']:
            prompt = self._create_post_prompt(api_info)
        else:
            prompt = self._create_get_prompt(api_info)

        try:
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert API testing specialist. Generate comprehensive test cases in the exact JSON format specified."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=4000
            )

            # Parse the response
            test_cases_text = response.choices[0].message.content
            test_cases = json.loads(test_cases_text)

            # Add curl commands if requested
            if include_curl:
                for category in test_cases.values():
                    for test_case in category:
                        curl_cmd = self._generate_curl_command(
                            test_case.get('endpoint', url),
                            test_case.get('method', method),
                            test_case.get('headers', headers),
                            test_case.get('payload', payload),
                            test_case.get('query_params', query_params)
                        )
                        test_case['curl_command'] = curl_cmd

            return test_cases

        except Exception as e:
            # Use the SimpleTestCaseGenerator as fallback
            print(f"OpenAI generation failed --falling back to simple generator: {str(e)}")
            return self.fallback_generator.generate_tests(api_info)

    def _generate_curl_command(self, endpoint, method, headers=None, payload=None, query_params=None):
        """Generate a curl command for the test case"""
        curl_parts = [f"curl -X {method}"]

        if headers:
            for key, value in headers.items():
                curl_parts.append(f"-H '{key}: {value}'")

        if payload and isinstance(payload, dict):
            curl_parts.append(f"-d '{json.dumps(payload)}'")

        # Add query params to URL
        url = endpoint
        if query_params:
            query_string = "&".join([f"{k}={v}" for k, v in query_params.items()])
            url = f"{endpoint}?{query_string}"

        curl_parts.append(f"'{url}'")
        return " ".join(curl_parts)
    def _create_post_prompt(self, api_info: Dict[str, Any]) -> str:
        """
        Create prompt for POST/PUT/PATCH requests
        """
        method = api_info.get('method', 'POST')
        url = api_info.get('url', '')
        headers = api_info.get('headers', {})
        payload = api_info.get('payload', {})
        response = api_info.get('response', {})

        prompt = f"""
        Generate comprehensive test cases for the following API endpoint. The test cases should cover all aspects of API testing including positive, negative, boundary value, and security testing.
        
        API Details:
        Method: {method}
        URL: {url}
        Headers: {json.dumps(headers, indent=2)}
        Payload Structure: {json.dumps(payload, indent=2)}
        Response Status: {response.get('status_code', 'Unknown')}
        Response Content: {json.dumps(response.get('content', {}), indent=2)}
        
        Generate test cases in the following exact JSON format:
        
        {{
          "Positive": [
            {{
              "description": "Test with all valid inputs as specified in API information",
              "endpoint": "{url}",
              "method": "{method}",
              "headers": {json.dumps(headers)},
              "payload": {json.dumps(payload)},
              "expected_status": {response.get('status_code', 201)},
              "expected_response_schema": {{
                // Detailed JSON schema for expected response
              }}
            }}
          ],
          "Semantic": [
            {{
              "description": "Test with special characters in all string fields",
              "endpoint": "{url}",
              "method": "{method}",
              "headers": {json.dumps(headers)},
              "payload": {{
                // Modified payload with special characters
              }},
              "expected_status": {response.get('status_code', 201)},
              "expected_response_schema": {{
                // JSON schema for expected response
              }}
            }},
            {{
              "description": "Test with maximum allowed length for string fields",
              "endpoint": "{url}",
              "method": "{method}",
              "headers": {json.dumps(headers)},
              "payload": {{
                // Modified payload with max length strings
              }},
              "expected_status": {response.get('status_code', 201)},
              "expected_response_schema": {{
                // JSON schema for expected response
              }}
            }}
            // Generate 3-5 more semantic test cases with meaningful variations
          ],
          "Boundary": [
            {{
              "description": "Test with minimum allowed value for numeric fields",
              "endpoint": "{url}",
              "method": "{method}",
              "headers": {json.dumps(headers)},
              "payload": {{
                // Modified payload with minimum values
              }},
              "expected_status": {response.get('status_code', 201)},
              "expected_response_schema": {{
                // JSON schema for expected response
              }}
            }},
            {{
              "description": "Test with maximum allowed value for numeric fields",
              "endpoint": "{url}",
              "method": "{method}",
              "headers": {json.dumps(headers)},
              "payload": {{
                // Modified payload with maximum values
              }},
              "expected_status": {response.get('status_code', 201)},
              "expected_response_schema": {{
                // JSON schema for expected response
              }}
            }}
            // Generate 3-4 more boundary test cases
          ],
          "Negative": [
            {{
              "description": "Test with empty string for required field: [FIELD_NAME]",
              "endpoint": "{url}",
              "method": "{method}",
              "headers": {json.dumps(headers)},
              "payload": {{
                // Modified payload with empty string for required field
              }},
              "expected_status": 422,
              "expected_error": {{
                "message": "Validation error: [FIELD_NAME] cannot be empty",
                "code": "VALIDATION_ERROR"
              }}
            }},
            {{
              "description": "Test with invalid data type for field: [FIELD_NAME]",
              "endpoint": "{url}",
              "method": "{method}",
              "headers": {json.dumps(headers)},
              "payload": {{
                // Modified payload with wrong data type
              }},
              "expected_status": 422,
              "expected_error": {{
                "message": "Invalid data type for field: [FIELD_NAME]",
                "code": "INVALID_DATA_TYPE"
              }}
            }}
            // Generate 6-8 more negative test cases covering various scenarios
          ],
          "Security": [
            {{
              "description": "Test with missing authorization header",
              "endpoint": "{url}",
              "method": "{method}",
              "headers": {{
                // Headers without authorization
              }},
              "payload": {json.dumps(payload)},
              "expected_status": 401,
              "expected_error": {{
                "message": "Unauthorized: Missing authentication",
                "code": "UNAUTHORIZED"
              }}
            }},
            {{
              "description": "Test with invalid authorization token",
              "endpoint": "{url}",
              "method": "{method}",
              "headers": {{
                // Headers with invalid token
              }},
              "payload": {json.dumps(payload)},
              "expected_status": 403,
              "expected_error": {{
                "message": "Forbidden: Invalid authentication",
                "code": "FORBIDDEN"
              }}
            }}
            // Generate 3-4 more security test cases
          ]
        }}
        
        Requirements:
        1. Positive: Exactly 1 test case with valid inputs
        2. Semantic: 1-2 test cases with meaningful variations (special chars, formats, edge cases)
        3. Boundary: 1-2 test cases covering all boundary conditions (min/max values, lengths)
        4. Negative: 1-2 test cases covering various error scenarios (invalid types, missing fields, etc.)
        5. Security: 1-2 test cases covering authentication, authorization, injection attempts
        6. For each test case:
           - Provide detailed description
           - Include complete request structure
           - Specify expected status code
           - For success cases, include expected response schema
           - For error cases, include expected error structure
        7. Use actual field names from the provided payload
        8. Ensure all JSON is valid and properly formatted
        9. Cover all important aspects of the API based on its functionality
        10. Include tests for all query/path parameters if applicable
        """
        return prompt

    def _create_get_prompt(self, api_info: Dict[str, Any]) -> str:
        """
        Create prompt for GET requests
        """
        method = api_info.get('method', 'GET')
        url = api_info.get('url', '')
        headers = api_info.get('headers', {})
        query_params = api_info.get('query_params', {})
        response = api_info.get('response', {})

        prompt = f"""
        Generate comprehensive test cases for the following API endpoint. The test cases should cover all aspects of API testing including positive, negative, boundary value, and security testing.
        
        API Details:
        Method: {method}
        URL: {url}
        Headers: {json.dumps(headers, indent=2)}
        Query Parameters: {json.dumps(query_params, indent=2)}
        Response Status: {response.get('status_code', 'Unknown')}
        Response Content: {json.dumps(response.get('content', {}), indent=2)}
        
        Generate test cases in the following exact JSON format:
        
        {{
          "Positive": [
            {{
              "description": "Test fetching data with valid parameters",
              "endpoint": "{url}",
              "method": "{method}",
              "headers": {json.dumps(headers)},
              "query_params": {json.dumps(query_params)},
              "expected_status": {response.get('status_code', 200)},
              "expected_response_schema": {{
                // Detailed JSON schema for expected response
              }}
            }}
          ],
          "Semantic": [
            {{
              "description": "Test with special characters in query parameters",
              "endpoint": "{url}",
              "method": "{method}",
              "headers": {json.dumps(headers)},
              "query_params": {{
                // Modified query params with special chars
              }},
              "expected_status": {response.get('status_code', 200)},
              "expected_response_schema": {{
                // JSON schema for expected response
              }}
            }}
            // Generate 5-6 more semantic test cases
          ],
          "Boundary": [
            {{
              "description": "Test with minimum allowed value for numeric query parameters",
              "endpoint": "{url}",
              "method": "{method}",
              "headers": {json.dumps(headers)},
              "query_params": {{
                // Query params with minimum values
              }},
              "expected_status": {response.get('status_code', 200)},
              "expected_response_schema": {{
                // JSON schema for expected response
              }}
            }}
            // Generate 5-6 more boundary test cases
          ],
          "Negative": [
            {{
              "description": "Test with invalid parameter value: [PARAM_NAME]",
              "endpoint": "{url}",
              "method": "{method}",
              "headers": {json.dumps(headers)},
              "query_params": {{
                // Query params with invalid value
              }},
              "expected_status": 422,
              "expected_error": {{
                "message": "Invalid value for parameter: [PARAM_NAME]",
                "code": "INVALID_PARAMETER"
              }}
            }}
            // Generate 8-10 more negative test cases
          ],
          "Security": [
            {{
              "description": "Test SQL injection attempt in query parameters",
              "endpoint": "{url}",
              "method": "{method}",
              "headers": {json.dumps(headers)},
              "query_params": {{
                // Query params with SQL injection attempt
              }},
              "expected_status": 400,
              "expected_error": {{
                "message": "Invalid request parameters",
                "code": "BAD_REQUEST"
              }}
            }}
            // Generate 4-5 more security test cases
          ]
        }}
        
        Requirements:
        1. Positive: Exactly 1 test case with valid inputs
        2. Semantic: 5-6 test cases with meaningful variations
        3. Boundary: 5-6 test cases covering all boundary conditions
        4. Negative: 8-10 test cases covering various error scenarios
        5. Security: 4-5 test cases covering security aspects
        6. For each test case:
           - Provide detailed descriptions
           - Include complete request structure
           - Specify expected status code
           - For success cases, include expected response schema
           - For error cases, include expected error structure
        7. Ensure all JSON is valid and properly formatted
        8. Cover all important aspects of the API based on its functionality
        """
        return prompt

    # def _generate_fallback_tests(self, api_info: Dict[str, Any]) -> Dict[str, Any]:
    #     """
    #     Generate basic fallback test cases if OpenAI fails
    #     """
    #     method = api_info.get('method', 'GET')
    #     url = api_info.get('url', '')
    #     headers = api_info.get('headers', {})
    #     payload = api_info.get('payload', {})
    #     query_params = api_info.get('query_params', {})
    #
    #     if method.upper() in ['POST', 'PUT', 'PATCH']:
    #         return {
    #             "Positive": [
    #                 {
    #                     "description": "Test with valid inputs",
    #                     "endpoint": url,
    #                     "method": method,
    #                     "headers": headers,
    #                     "payload": payload,
    #                     "expected_status": 201
    #                 }
    #             ],
    #             "Semantic": [
    #                 {
    #                     "description": "Test with special characters in string fields",
    #                     "endpoint": url,
    #                     "method": method,
    #                     "headers": headers,
    #                     "payload": {**payload, "text_field": "Special!@#$%^&*()"},
    #                     "expected_status": 201
    #                 },
    #                 {
    #                     "description": "Test with maximum length for string fields",
    #                     "endpoint": url,
    #                     "method": method,
    #                     "headers": headers,
    #                     "payload": {**payload, "text_field": "A" * 255},
    #                     "expected_status": 201
    #                 }
    #             ],
    #             "Boundary": [
    #                 {
    #                     "description": "Test with minimum value for numeric field",
    #                     "endpoint": url,
    #                     "method": method,
    #                     "headers": headers,
    #                     "payload": {**payload, "numeric_field": 0},
    #                     "expected_status": 201
    #                 },
    #                 {
    #                     "description": "Test with maximum value for numeric field",
    #                     "endpoint": url,
    #                     "method": method,
    #                     "headers": headers,
    #                     "payload": {**payload, "numeric_field": 999999},
    #                     "expected_status": 201
    #                 }
    #             ],
    #             "Negative": [
    #                 {
    #                     "description": "Test with empty required field",
    #                     "endpoint": url,
    #                     "method": method,
    #                     "headers": headers,
    #                     "payload": {**payload, "required_field": ""},
    #                     "expected_status": 422
    #                 },
    #                 {
    #                     "description": "Test with invalid data type",
    #                     "endpoint": url,
    #                     "method": method,
    #                     "headers": headers,
    #                     "payload": {**payload, "numeric_field": "string"},
    #                     "expected_status": 422
    #                 },
    #                 {
    #                     "description": "Test with missing required field",
    #                     "endpoint": url,
    #                     "method": method,
    #                     "headers": headers,
    #                     "payload": {k: v for k, v in payload.items() if k != "required_field"},
    #                     "expected_status": 422
    #                 }
    #             ],
    #             "Security": [
    #                 {
    #                     "description": "Test with missing authorization header",
    #                     "endpoint": url,
    #                     "method": method,
    #                     "headers": {k: v for k, v in headers.items() if k.lower() != "authorization"},
    #                     "payload": payload,
    #                     "expected_status": 401
    #                 },
    #                 {
    #                     "description": "Test with SQL injection attempt",
    #                     "endpoint": url,
    #                     "method": method,
    #                     "headers": headers,
    #                     "payload": {**payload, "text_field": "' OR 1=1 --"},
    #                     "expected_status": 400
    #                 }
    #             ]
    #         }
    #     else:
    #         return {
    #             "Positive": [
    #                 {
    #                     "description": "Test fetching data with valid parameters",
    #                     "endpoint": url,
    #                     "method": method,
    #                     "headers": headers,
    #                     "query_params": query_params,
    #                     "expected_status": 200
    #                 }
    #             ],
    #             "Semantic": [
    #                 {
    #                     "description": "Test with special characters in query params",
    #                     "endpoint": url,
    #                     "method": method,
    #                     "headers": headers,
    #                     "query_params": {**query_params, "search": "special!@#$"},
    #                     "expected_status": 200
    #                 }
    #             ],
    #             "Boundary": [
    #                 {
    #                     "description": "Test with pagination limit at minimum",
    #                     "endpoint": url,
    #                     "method": method,
    #                     "headers": headers,
    #                     "query_params": {**query_params, "limit": 1},
    #                     "expected_status": 200
    #                 },
    #                 {
    #                     "description": "Test with pagination limit at maximum",
    #                     "endpoint": url,
    #                     "method": method,
    #                     "headers": headers,
    #                     "query_params": {**query_params, "limit": 100},
    #                     "expected_status": 200
    #                 }
    #             ],
    #             "Negative": [
    #                 {
    #                     "description": "Test with invalid parameter value",
    #                     "endpoint": url,
    #                     "method": method,
    #                     "headers": headers,
    #                     "query_params": {**query_params, "id": "invalid"},
    #                     "expected_status": 404
    #                 },
    #                 {
    #                     "description": "Test with non-existent resource",
    #                     "endpoint": f"{url}/nonexistent",
    #                     "method": method,
    #                     "headers": headers,
    #                     "expected_status": 404
    #                 }
    #             ],
    #             "Security": [
    #                 {
    #                     "description": "Test SQL injection in query params",
    #                     "endpoint": url,
    #                     "method": method,
    #                     "headers": headers,
    #                     "query_params": {**query_params, "id": "1 OR 1=1"},
    #                     "expected_status": 400
    #                 },
    #                 {
    #                     "description": "Test with missing auth token",
    #                     "endpoint": url,
    #                     "method": method,
    #                     "headers": {k: v for k, v in headers.items() if k.lower() != "authorization"},
    #                     "expected_status": 401
    #                 }
    #             ]
    #         }