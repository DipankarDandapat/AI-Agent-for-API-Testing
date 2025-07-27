# 🤖 AI Agent for API Testing

<div align="center">
  
  [![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
  [![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)](https://flask.palletsprojects.com/)
  [![OpenAI](https://img.shields.io/badge/OpenAI-GPT--3.5-orange.svg)](https://openai.com)


  **🚀 Transform API Testing with AI-Powered Test Case Generation**
  
  *Automatically generate comprehensive test suites for any REST API with just a few clicks*

</div>

---

## 🎯 Project Overview

Successfully built and deployed a comprehensive AI Agent for API Testing that allows users to input API information and automatically generates comprehensive Test cases (positive, negative, Boundary Values and Edge Cases, semantic and Security) with downloadable JSON format.


## ✅ **What Makes This Special?**

🧠 **AI-Powered Intelligence** - Leverages OpenAI GPT-3.5 to understand your API and generate intelligent test cases  
⚡ **Complete Test Coverage** - Generates 5 comprehensive test categories: Positive, Negative, Boundary, Semantic & Security  
🎮 **One-Click Execution** - Execute all generated test cases with real-time results and performance metrics  
📱 **Zero Dependencies Frontend** - Pure HTML/CSS/JS for maximum compatibility and performance  
📊 **Professional Reports** - Export test cases in structured JSON format for CI/CD integration  
🔄 **Smart Fallback** - Rule-based generator ensures reliability when AI services are unavailable  

---
## 🎬 **Demo**

 **📹 Watch the Full Demo Video**



https://github.com/user-attachments/assets/c545f08c-4af3-4788-946b-3a1eed0b2594


 
 *See how easy it is to generate comprehensive test suites in under 2 minutes!*

### 🖼️ **Screenshots**



|                   Main Interface                   |                 Execution Results                  |
|:--------------------------------------------------:|:--------------------------------------------------:|
|![Main Interface](src/static/Main%20Interface.png)    | ![Results](src/static/Execution%20Results.png) |



---

## ✨ **Key Features**

### 🎯 **Comprehensive Test Generation**
- **Positive Tests** - Valid scenarios with expected successful responses
- **Negative Tests** - Invalid inputs and error handling validation  
- **Boundary Tests** - Edge cases and limit testing
- **Semantic Tests** - Real-world data scenarios and special characters
- **Security Tests** - SQL injection, XSS, and authentication bypass attempts

### 🚀 **Advanced Capabilities**
- **Multi-Method Support** - GET, POST, PUT, PATCH, DELETE
- **File Upload Testing** - Automatic file upload test generation for applicable methods
- **Real-time Execution** - Execute all test cases with live status updates
- **Performance Metrics** - Response time tracking and analysis
- **cURL Generation** - Copy-paste ready cURL commands for each test
- **JSON Export** - Download test suites in structured JSON format

### 🎨 **User Experience**
- **Intuitive Interface** - Clean, professional design with tabbed navigation
- **Mobile Responsive** - Works perfectly on desktop, tablet, and mobile
- **Visual Feedback** - Color-coded results with success/failure indicators
- **Progress Tracking** - Real-time execution progress with detailed results

---

## 🏃‍♂️ **Quick Start**

### 📋 **Prerequisites**
- Python 3.11 or higher
- OpenAI API key (optional - has fallback generator)

### ⚡ **Installation**

```bash
# Clone the repository
git clone https://github.com/DipankarDandapat/AI-Agent-for-API-Testing.git
cd AI-Agent-for-API-Testing.git

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables (optional)
export OPENAI_API_KEY="your-openai-api-key-here"

# Run the application
python src/main.py
```

🌐 **Open your browser and navigate to `http://localhost:5000`**

---

## 📖 **How to Use**

### 1️⃣ **Configure Your API**
```javascript
// Example configuration
Method: POST
URL: https://api.example.com/v1/users
Headers: {"Content-Type": "application/json", "Authorization": "Bearer token"}
Payload: {"name": "John Doe", "email": "john@example.com"}
```

### 2️⃣ **Test Your API**
Click **"Test API"** to verify your endpoint is working correctly

### 3️⃣ **Generate Test Cases**
Click **"Generate Tests"** and watch AI create comprehensive test scenarios

### 4️⃣ **Execute & Analyze**
- Review generated tests across 5 categories
- Click **"Execute All Tests"** for real-time validation
- Analyze results with response times and status codes

### 5️⃣ **Export & Integrate**
Download JSON test suite for integration with your CI/CD pipeline

---

## 🏗️ **Architecture**

![Architecture](src\\static\\mindmap.png) 

### 🔧 **Tech Stack**

**Backend**
- **Flask** - Lightweight Python web framework
- **OpenAI API** - GPT-3.5 for intelligent test generation
- **Requests** - HTTP library for API testing
- **CORS** - Cross-origin resource sharing support

**Frontend**
- **Pure HTML5** - Semantic structure
- **Vanilla CSS** - Custom responsive styling
- **Plain JavaScript** - No frameworks, maximum compatibility

---

## 📁 **Project Structure**

```
AI-Agent-for-API-Testing/
├── src/
│   ├── static/
│   │   ├── index.html              # Main web interface
│   │   ├── style.css               # Responsive styling
│   │   └── script.js               # Frontend logic
│   ├── routes/
│   │   └── api_testing.py          # API endpoints
│   ├── services/
│   │   ├── test_generator.py       # OpenAI-powered generation
│   │   └── simple_test_generator.py # Rule-based fallback
│   └── main.py                     # Flask application
├── requirements.txt                # Python dependencies
├── README.md                       
└── .env                  # Environment variables template
```

---

## 🎯 **Test Case Examples**

<details>
<summary>📝 POST Request Test Cases</summary>

```json
{
  "Positive": [
    {
      "description": "Create user with valid data",
      "endpoint": "/api/v1/users",
      "method": "POST",
      "headers": {"Content-Type": "application/json"},
      "payload": {
        "name": "John Doe",
        "email": "john@example.com",
        "age": 30
      },
      "expected_status": 201
    }
  ],
  "Negative": [
    {
      "description": "Create user with invalid email format",
      "endpoint": "/api/v1/users",
      "method": "POST",
      "headers": {"Content-Type": "application/json"},
      "payload": {
        "name": "John Doe",
        "email": "invalid-email",
        "age": 30
      },
      "expected_status": 422
    }
  ],
  "Security": [
    {
      "description": "SQL injection attempt in name field",
      "endpoint": "/api/v1/users",
      "method": "POST",
      "headers": {"Content-Type": "application/json"},
      "payload": {
        "name": "'; DROP TABLE users; --",
        "email": "test@example.com",
        "age": 30
      },
      "expected_status": 400
    }
  ]
}
```

</details>

<details>
<summary>🔍 GET Request Test Cases</summary>

```json
{
  "Positive": [
    {
      "description": "Fetch user with valid ID",
      "endpoint": "/api/v1/users/{id}",
      "method": "GET",
      "path_params": {"id": "123"},
      "headers": {"Accept": "application/json"},
      "expected_status": 200
    }
  ],
  "Boundary": [
    {
      "description": "Fetch user with maximum valid ID",
      "endpoint": "/api/v1/users/{id}",
      "method": "GET",
      "path_params": {"id": "999999999"},
      "headers": {"Accept": "application/json"},
      "expected_status": 200
    }
  ]
}
```

</details>

---

## 🚀 **Advanced Features**

### 🤖 **AI-Powered Generation**
- **Context Understanding** - AI analyzes your API structure and generates relevant tests
- **Smart Fallback** - Seamlessly switches to rule-based generation if AI is unavailable
- **Custom Prompting** - Optimized prompts for comprehensive test coverage

### ⚡ **Real-time Execution**
- **Parallel Processing** - Execute multiple test cases simultaneously
- **Live Updates** - Real-time status updates during execution
- **Performance Metrics** - Response time tracking and analysis
- **Error Handling** - Comprehensive error reporting and debugging

### 📊 **Export & Integration**
- **JSON Format** - Structured export for CI/CD integration
- **Custom Schemas** - Generate expected response schemas
- **cURL Commands** - Copy-paste ready terminal commands

---

## 🛠️ **Configuration**

### Environment Variables

```bash
# .env file
OPENAI_API_KEY=your-openai-api-key-here
FLASK_ENV=development
FLASK_DEBUG=True
PORT=5000
```

### Advanced Settings

```python
# Custom configuration options
MAX_TEST_CASES_PER_CATEGORY = 10
API_TIMEOUT = 30
OPENAI_MODEL = "gpt-3.5-turbo"
FALLBACK_ENABLED = True
```

---

## 📈 **Performance & Reliability**

### ⚡ **Speed Metrics**
- **Test Generation**: < 20 seconds for comprehensive suite
- **Execution Time**: Parallel processing for faster results
- **UI Response**: < 100ms for all interactions

### 🛡️ **Reliability Features**
- **Error Handling**: Comprehensive error catching and user feedback
- **Fallback System**: Rule-based generator ensures 100% uptime
- **Input Validation**: Robust validation for all user inputs
- **Timeout Management**: Prevents hanging requests



## 📚 **Documentation**

### 🔗 **API Endpoints**

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/test-api` | POST | Execute API request and return response |
| `/api/generate-tests` | POST | Generate comprehensive test cases |
| `/api/execute-tests` | POST | Execute all generated test cases |
| `/api/health` | GET | Health check endpoint |



## 🏆 **Use Cases**

### 👨‍💻 **For Developers**
- **Rapid Prototyping** - Quickly validate new API endpoints
- **Regression Testing** - Ensure changes don't break existing functionality
- **Documentation** - Generate test examples for API documentation

### 🧪 **For QA Engineers**
- **Test Case Generation** - Comprehensive test suite creation
- **Edge Case Discovery** - Identify scenarios you might have missed
- **Performance Testing** - Monitor API response times

### 🏢 **For Teams**
- **CI/CD Integration** - Export JSON for automated testing pipelines
- **Onboarding** - Help new team members understand API behavior
- **Code Reviews** - Validate API changes with comprehensive testing

---


## 🙏 **Acknowledgments**

- **OpenAI** for providing the GPT-3.5 API
- **Flask Community** for the excellent web framework
- **Contributors** who helped make this project better
- **Beta Testers** for valuable feedback and bug reports

---

## 📞 **Support & Contact**


### 🌟 **Connect With me**
- 💼 [LinkedIn](https://www.linkedin.com/in/dipankardandapat/)
- 📧 [Email](d.dandapat96@gmail.com)

---
