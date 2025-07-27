from flask import Blueprint, jsonify, request, session
import requests
import json
import os
import curlify
import time
from urllib.parse import urljoin, urlparse
from werkzeug.utils import secure_filename
import traceback
try:
    from src.services.test_generator import TestCaseGenerator
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
from src.services.simple_test_generator import SimpleTestCaseGenerator

api_testing_bp = Blueprint('api_testing', __name__)

# Configure upload folder
UPLOAD_FOLDER = '/tmp/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf', 'pptx', 'mp3', 'txt', 'csv', 'json', 'xml'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_mime_type(file_extension):
    """Determine MIME type based on file extension"""
    mime_types = {
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.pdf': 'application/pdf',
        '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
        '.mp3': 'audio/mpeg',
        '.txt': 'text/plain',
        '.csv': 'text/csv',
        '.json': 'application/json',
        '.xml': 'application/xml'
    }
    return mime_types.get(file_extension.lower(), 'application/octet-stream')

def add_file(file_path, file_variable_name):
    """Create file tuple for requests"""
    file_name = os.path.basename(file_path)
    file_extension = os.path.splitext(file_name)[1].lower()
    mime_type = get_mime_type(file_extension)

    file_tuple = (file_name, open(file_path, 'rb'), mime_type)
    files = {file_variable_name: file_tuple}
    return files

def convert_response_to_curl(response):
    """Convert requests response object to cURL command"""
    try:
        curl_command = curlify.to_curl(response.request)
        return curl_command
    except Exception as e:
        return f"# Failed to generate cURL command: {str(e)}"

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@api_testing_bp.route('/execute-test-case', methods=['POST'])
def execute_test_case():
    """Execute a single test case and return the response"""
    try:
        test_case = request.json.get('test_case')
        if not test_case:
            return jsonify({'error': 'Test case is required'}), 400

        method = test_case.get('method', 'GET').upper()
        url = test_case.get('endpoint', '')
        headers = test_case.get('headers', {})
        payload = test_case.get('payload', {})
        query_params = test_case.get('query_params', {})
        file_path = test_case.get('file_path')

        if not url:
            return jsonify({'error': 'URL is required'}), 400

        request_kwargs = {
            'url': url,
            'headers': headers,
            'params': query_params,
            'timeout': 30
        }

        files_dict = None
        if file_path and os.path.exists(file_path) and method in ['POST', 'PUT', 'PATCH']:
            files_dict = add_file(file_path, 'file')
            request_kwargs['files'] = files_dict
            if payload:
                request_kwargs['data'] = payload
        elif method in ['POST', 'PUT', 'PATCH'] and payload:
            if headers.get('content-type', '').lower() == 'application/json':
                request_kwargs['json'] = payload
            else:
                request_kwargs['data'] = payload

        start_time = time.time()
        response = requests.request(method, **request_kwargs)
        response_time = time.time() - start_time

        response_data = {
            'status_code': response.status_code,
            'headers': dict(response.headers),
            'content': None,
            'content_type': response.headers.get('content-type', ''),
            'response_time': response_time
        }

        try:
            if 'application/json' in response_data['content_type']:
                response_data['content'] = response.json()
            else:
                response_data['content'] = response.text
        except:
            response_data['content'] = response.text

        if files_dict:
            for file_tuple in files_dict.values():
                if hasattr(file_tuple[1], 'close'):
                    file_tuple[1].close()

        return jsonify({
            'success': True,
            'response': response_data,
            # 'curl_command': convert_response_to_curl(response)
        })

    except requests.exceptions.RequestException as e:
        return jsonify({
            'success': False,
            'error': f'Request failed: {str(e)}'
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Unexpected error: {str(e)}'
        }),


@api_testing_bp.route('/test-api', methods=['POST'])
def test_api():
    """
    Test an API endpoint and capture the response for test case generation
    Supports both JSON and file uploads
    """
    try:
        # Handle both JSON and form data
        if request.is_json:
            data = request.json
            uploaded_file = None
        else:
            # Handle form data with potential file upload
            data = {
                'method': request.form.get('method', 'GET'),
                'url': request.form.get('url', ''),
                'headers': json.loads(request.form.get('headers', '{}')),
                'payload': json.loads(request.form.get('payload', '{}')),
                'query_params': json.loads(request.form.get('query_params', '{}'))
            }
            uploaded_file = request.files.get('file') if 'file' in request.files else None

        # Extract API details from request
        method = data.get('method', 'GET').upper()
        url = data.get('url', '')
        headers = data.get('headers', {})
        payload = data.get('payload', {})
        query_params = data.get('query_params', {})
        file_variable_name = data.get('file_variable_name', 'file')

        # Validate required fields
        if not url:
            return jsonify({'error': 'URL is required'}), 400

        # Prepare request parameters
        request_kwargs = {
            'url': url,
            'headers': headers,
            'params': query_params,
            'timeout': 30
        }

        # Handle file upload for POST/PUT/PATCH methods
        files_dict = None
        if uploaded_file and method in ['POST', 'PUT', 'PATCH']:
            if uploaded_file and allowed_file(uploaded_file.filename):
                filename = secure_filename(uploaded_file.filename)
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                uploaded_file.save(file_path)

                # Create files dictionary for requests
                files_dict = add_file(file_path, file_variable_name)
                request_kwargs['files'] = files_dict

                # If we have files, don't send JSON payload
                if payload:
                    request_kwargs['data'] = payload
            else:
                return jsonify({'error': 'Invalid file type'}), 400
        elif method in ['POST', 'PUT', 'PATCH'] and payload:
            # Handle JSON payload when no file is uploaded
            if headers.get('content-type', '').lower() == 'application/json':
                request_kwargs['json'] = payload
            else:
                request_kwargs['data'] = payload

        # Make the API request
        response = requests.request(method, **request_kwargs)

        # Generate cURL command
        curl_command = convert_response_to_curl(response)

        # Capture response details
        response_data = {
            'status_code': response.status_code,
            'headers': dict(response.headers),
            'content': None,
            'content_type': response.headers.get('content-type', ''),
            'curl_command': curl_command
        }

        # Try to parse response content
        try:
            if 'application/json' in response_data['content_type']:
                response_data['content'] = response.json()
            else:
                response_data['content'] = response.text
        except:
            response_data['content'] = response.text

        # Clean up uploaded file
        if files_dict:
            for file_tuple in files_dict.values():
                if hasattr(file_tuple[1], 'close'):
                    file_tuple[1].close()
            # Remove the temporary file
            if 'file_path' in locals():
                try:
                    os.remove(file_path)
                except:
                    pass

        # Prepare API information for test generation
        api_info = {
            'method': method,
            'url': url,
            'headers': headers,
            'payload': payload,
            'query_params': query_params,
            'response': response_data,
            'has_file_upload': uploaded_file is not None,
            'file_variable_name': file_variable_name if uploaded_file else None
        }

        return jsonify({
            'success': True,
            'api_info': api_info,
            'message': f'API request completed with status {response.status_code}'
        })

    except requests.exceptions.RequestException as e:
        return jsonify({
            'success': False,
            'error': f'Request failed: {str(e)}'
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Unexpected error: {str(e)}'
        }), 500


@api_testing_bp.route('/generate-tests', methods=['POST'])
def generate_tests():
    """Generate test cases and execute them immediately"""
    try:
        data = request.json
        api_info = data.get('api_info', {})
        use_ai = data.get('use_ai', True)

        if not api_info:
            return jsonify({'error': 'API information is required'}), 400

        # Determine which generator to use
        if use_ai and OPENAI_AVAILABLE:
            try:
                generator = TestCaseGenerator()
                test_cases = generator.generate_test_cases(api_info, include_curl=True)
            except Exception as e:
                print(f"OpenAI generation failed, falling back to simple generator: {str(e)}")
                generator = SimpleTestCaseGenerator()
                test_cases = generator.generate_tests(api_info)
        else:
            generator = SimpleTestCaseGenerator()
            test_cases = generator.generate_tests(api_info)

        # Execute all test cases and store responses
        executed_test_cases = {}
        for category, cases in test_cases.items():
            executed_test_cases[category] = []
            for case in cases:
                # Prepare test case for execution
                test_case_to_execute = {
                    'method': case.get('method', api_info.get('method', 'GET')),
                    'endpoint': case.get('endpoint', api_info.get('url', '')),
                    'headers': case.get('headers', api_info.get('headers', {})),
                    'payload': case.get('payload', api_info.get('payload', {})),
                    'query_params': case.get('query_params', api_info.get('query_params', {}))
                }

                # Execute the test case
                exec_response = requests.post(
                    urljoin(request.host_url, '/api/execute-test-case'),
                    json={'test_case': test_case_to_execute},
                    headers={'Content-Type': 'application/json'}
                )

                if exec_response.ok:
                    execution_result = exec_response.json()
                    # print(exec_response.json())

                    case['execution_result'] = execution_result
                else:
                    case['execution_result'] = {
                        'success': False,
                        'error': 'Failed to execute test case'
                    }

                executed_test_cases[category].append(case)

        # In your generate_tests route:
        minimized_test_cases = {}
        for category, cases in executed_test_cases.items():
            minimized_test_cases[category] = []
            for case in cases:
                minimized_case = {
                    'description': case.get('description'),
                    'method': case.get('method'),
                    'endpoint': case.get('endpoint'),
                    'headers': case.get('headers'),
                    'expected_status': case.get('expected_status'),
                }
                # Only add query_params if they exist and are not empty
                if case.get('query_params'):
                    minimized_case['query_params'] = case['query_params']

                # Only add payload if it exists and is not empty
                if case.get('payload'):
                    minimized_case['payload'] = case['payload']

                minimized_test_cases[category].append(minimized_case)

        print(minimized_test_cases)
        print("###############################################")
        # Store in session for download
        session['last_test_cases'] = minimized_test_cases

        return jsonify({
            'success': True,
            'test_cases': executed_test_cases,
            'message': 'Test cases generated and executed successfully',
            'used_ai': use_ai and OPENAI_AVAILABLE
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Test generation failed: {str(e)}'
        }), 500


@api_testing_bp.route('/download-tests', methods=['POST'])
def download_tests():
    try:
        test_cases = session.get('last_test_cases')
        if not test_cases:
            return jsonify({'error': 'No test cases available'}), 404

        # Define the desired order of test case categories
        ordered_categories = ['Positive', 'Negative', 'Boundary', 'Semantic', 'Security']

        # Build an ordered list of test cases (instead of a dict)
        ordered_test_cases = []
        for category in ordered_categories:
            if category in test_cases and test_cases[category]:
                ordered_test_cases.append({
                    "category": category,
                    "test_cases": [
                        {k: v for k, v in case.items() if k != 'curl_command'}
                        for case in test_cases[category]
                    ]
                })

        # Return as JSON with ensure_ascii=False for better readability
        response = jsonify(ordered_test_cases)
        response.headers['Content-Disposition'] = 'attachment; filename=test_cases.json'
        return response

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Download failed: {str(e)}'
        }), 500

@api_testing_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint
    """
    return jsonify({
        'status': 'healthy',
        'service': 'API Testing Service'
    })

