document.addEventListener("DOMContentLoaded", () => {
    const methodSelect = document.getElementById("method");
    const urlInput = document.getElementById("url");
    const headersTextarea = document.getElementById("headers");
    const payloadTextarea = document.getElementById("payload");
    const queryParamsTextarea = document.getElementById("queryParams");
    const fileInput = document.getElementById("file");
    const fileVariableNameInput = document.getElementById("fileVariableName");
    const fileNameSpan = document.getElementById("file-name");
    const testApiBtn = document.getElementById("test-api-btn");
    const generateTestsBtn = document.getElementById("generate-tests-btn");
    const downloadJsonBtn = document.getElementById("download-json-btn");
    const errorDisplay = document.getElementById("error-display");
    const errorMessage = document.getElementById("error-message");
    const apiResponseSection = document.getElementById("api-response-section");
    const responseStatus = document.getElementById("response-status");
    const curlCommandSection = document.getElementById("curl-command-section");
    const curlCommandPre = document.getElementById("curl-command");
    const copyCurlBtn = document.getElementById("copy-curl-btn");
    const responseContentPre = document.getElementById("response-content");
    const generatedTestCasesSection = document.getElementById("generated-test-cases-section");
    const testCasesContent = document.getElementById("test-cases-content");
    const fileUploadSection = document.getElementById("file-upload-section");
    const payloadSection = document.getElementById("payload-section");

    const generateTestsSimpleBtn = document.getElementById("generate-tests-simple-btn");



    function validateJSONInput(textareaId, errorId) {
      const textarea = document.getElementById(textareaId);
      const errorElement = document.getElementById(errorId);

      textarea.addEventListener('input', () => {
        const value = textarea.value.trim();

        if (!value) {
          errorElement.style.display = 'none'; // Allow empty input
          textarea.classList.remove('invalid');
          return;
        }

        try {
          JSON.parse(value);
          errorElement.style.display = 'none';
          textarea.classList.remove('invalid');
        } catch (e) {
          errorElement.style.display = 'block';
          textarea.classList.add('invalid');
        }
      });
    }

// ✅ Call the function for each textarea
validateJSONInput('queryParams', 'queryParamsError');
validateJSONInput('headers', 'headersError');
validateJSONInput('payload', 'payloadError');



   const headers = {
  "content-type": "application/json",
  "accept": "application/json"
   };
    // Initialize default values
    headersTextarea.value = JSON.stringify(headers, null, 2);
    queryParamsTextarea.value = '{}';
    payloadTextarea.value = '{}';

    let currentApiInfo = null;
    let generatedTestCases = null;

    // Helper to show/hide elements
    const show = (element) => element.classList.remove("hidden");
    const hide = (element) => element.classList.add("hidden");

    // Helper to validate JSON
    const validateJSON = (jsonString) => {
        try {
            JSON.parse(jsonString);
            return true;
        } catch {
            return false;
        }
    };

    // Helper to display error
    const displayError = (message) => {
        errorMessage.textContent = message;
        show(errorDisplay);
    };

    // Helper to clear error
    const clearError = () => {
        hide(errorDisplay);
        errorMessage.textContent = "";
    };

    // Copy to clipboard
    const copyToClipboard = (text) => {
        navigator.clipboard.writeText(text).then(() => {
            alert("Copied to clipboard!");
        }).catch(err => {
            console.error("Failed to copy: ", err);
        });
    };

    // Handle method change to show/hide file upload and payload sections
    methodSelect.addEventListener("change", () => {
        const method = methodSelect.value;
        if (["POST", "PUT", "PATCH"].includes(method)) {
            show(fileUploadSection);
            show(payloadSection);
        } else {
            hide(fileUploadSection);
            hide(payloadSection);
        }
    });

    // Handle file input change
    fileInput.addEventListener("change", () => {
        if (fileInput.files.length > 0) {
            fileNameSpan.textContent = fileInput.files[0].name;
        } else {
            fileNameSpan.textContent = "";
        }
    });

    // Test API button click handler
    testApiBtn.addEventListener("click", async () => {
        clearError();
        hide(apiResponseSection);
        hide(generatedTestCasesSection);
        testApiBtn.disabled = true;
        generateTestsBtn.disabled = true;

        try {
            const method = methodSelect.value;
            const url = urlInput.value;
            const headers = headersTextarea.value;
            const payload = payloadTextarea.value;
            const queryParams = queryParamsTextarea.value;
            const selectedFile = fileInput.files[0];
            const fileVariableName = fileVariableNameInput.value;

            if (!url) {
                throw new Error("URL is required.");
            }
            if (!validateJSON(headers)) {
                throw new Error("Invalid JSON in headers.");
            }
            if (["POST", "PUT", "PATCH"].includes(method) && !validateJSON(payload)) {
                throw new Error("Invalid JSON in payload.");
            }
            if (!validateJSON(queryParams)) {
                throw new Error("Invalid JSON in query parameters.");
            }

            let requestBody;
            let requestHeaders = {};

            if (selectedFile && ["POST", "PUT", "PATCH"].includes(method)) {
                const formData = new FormData();
                formData.append("method", method);
                formData.append("url", url);
                formData.append("headers", headers);
                formData.append("payload", payload);
                formData.append("query_params", queryParams);
                formData.append("file_variable_name", fileVariableName);
                formData.append("file", selectedFile);
                requestBody = formData;
            } else {
                requestHeaders["Content-Type"] = "application/json";
                requestBody = JSON.stringify({
                    method: method,
                    url: url,
                    headers: JSON.parse(headers),
                    payload: JSON.parse(payload),
                    query_params: JSON.parse(queryParams)
                });
            }

            const response = await fetch("/api/test-api", {
                method: "POST",
                headers: requestHeaders,
                body: requestBody,
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || "API test failed.");
            }

            currentApiInfo = data.api_info;
            responseStatus.textContent = currentApiInfo.response.status_code;
            responseContentPre.textContent = typeof currentApiInfo.response.content === "object"
                ? JSON.stringify(currentApiInfo.response.content, null, 2)
                : currentApiInfo.response.content;

            if (currentApiInfo.response.curl_command) {
                curlCommandPre.textContent = currentApiInfo.response.curl_command;
                show(curlCommandSection);
            } else {
                hide(curlCommandSection);
            }
            show(apiResponseSection);
            generateTestsBtn.disabled = false;

        } catch (err) {
            displayError(err.message);
        } finally {
            testApiBtn.disabled = false;
        }
    });

    // Modify the generateTestsBtn click handler to include AI flag
    generateTestsBtn.addEventListener("click", async () => {
        await generateTests(true); // true = use AI
    });

    // Add new click handler for simple generation
    generateTestsSimpleBtn.addEventListener("click", async () => {
        await generateTests(false); // false = don't use AI
    });

    // Create a unified generateTests function
    const generateTests = async (useAI) => {
        if (!currentApiInfo) {
            displayError("Please test the API first.");
            return;
        }

        clearError();
        hide(generatedTestCasesSection);
        generateTestsBtn.disabled = true;
        generateTestsSimpleBtn.disabled = true;
        downloadJsonBtn.disabled = true;

        try {
            const response = await fetch("/api/generate-tests", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    api_info: currentApiInfo,
                    use_ai: useAI  // Add this flag
                }),
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || "Test generation failed.");
            }

            generatedTestCases = data.test_cases;
            renderTestCases(generatedTestCases);
            show(generatedTestCasesSection);
            downloadJsonBtn.disabled = false;

        } catch (err) {
            displayError(err.message);
        } finally {
            generateTestsBtn.disabled = false;
            generateTestsSimpleBtn.disabled = false;
        }
    };

    // Download JSON button click handler
    downloadJsonBtn.addEventListener("click", async () => {
        if (!currentApiInfo) {
            displayError("Please test the API first to get API information.");
            return;
        }

        clearError();
        downloadJsonBtn.disabled = true;

        try {
            const response = await fetch("/api/download-tests", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    api_info: currentApiInfo,
                }),
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || "Failed to fetch download data.");
            }

            const jsonString = JSON.stringify(data, null, 2);
            const blob = new Blob([jsonString], { type: "application/json" });
            const url = URL.createObjectURL(blob);
            const link = document.createElement("a");
            link.href = url;
            link.download = `api_test_cases_${new Date().toISOString().split("T")[0]}.json`;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            URL.revokeObjectURL(url);

        } catch (err) {
            displayError(`Failed to download JSON: ${err.message}. Please try again.`);
        } finally {
            downloadJsonBtn.disabled = false;
        }
    });

const renderTestCases = (testCasesData) => {
    console.log("Raw test cases data:", testCasesData); // Debug log

    const categories = ["Positive", "Negative", "Boundary", "Semantic", "Security"];

    // Update tab buttons with counts and set up click handlers
    categories.forEach(category => {
        const tabButton = document.querySelector(`[data-tab="${category.toLowerCase()}"]`);
        if (!tabButton) return;

        const tests = testCasesData[category] || [];
        const count = tests.length;
        tabButton.textContent = `${category} (${count})`;

        // Clear existing content
        const tabContentDiv = document.getElementById(`${category.toLowerCase()}-tests`);
        if (tabContentDiv) tabContentDiv.innerHTML = "";

        if (tests.length === 0) {
            tabContentDiv.innerHTML = `<p>No ${category} test cases generated.</p>`;
            return;
        }

        const testCasesContainer = document.createElement("div");
        testCasesContainer.className = "test-cases-container";

        tests.forEach((testCase, index) => {
            const testCaseDiv = document.createElement("div");
            testCaseDiv.className = "test-case-item";
            testCaseDiv.id = `${category.toLowerCase()}-test-${index}`;

            let content = `<h4>Test ${index + 1}: ${testCase.description || 'No description'}</h4>`;
            content += `<div><strong>Endpoint:</strong> ${testCase.endpoint || 'N/A'}</div>`;
            content += `<div><strong>Method:</strong> ${testCase.method || 'N/A'}</div>`;

            if (testCase.path_params && Object.keys(testCase.path_params).length > 0) {
                content += `<div><strong>Path Parameters:</strong> <pre>${JSON.stringify(testCase.path_params, null, 2)}</pre></div>`;
            }

            if (testCase.headers && Object.keys(testCase.headers).length > 0) {
                content += `<div><strong>Headers:</strong> <pre>${JSON.stringify(testCase.headers, null, 2)}</pre></div>`;
            }

            if (testCase.query_params && Object.keys(testCase.query_params).length > 0) {
                content += `<div><strong>Query Parameters:</strong> <pre>${JSON.stringify(testCase.query_params, null, 2)}</pre></div>`;
            }

            if (testCase.payload && Object.keys(testCase.payload).length > 0) {
                content += `<div><strong>Payload:</strong> <pre>${JSON.stringify(testCase.payload, null, 2)}</pre></div>`;
            }

            content += `<div><strong>Expected Status:</strong> ${testCase.expected_status || 'N/A'}</div>`;

            if (testCase.expected_schema && Object.keys(testCase.expected_schema).length > 0) {
                content += `<div><strong>Expected Schema:</strong> <pre>${JSON.stringify(testCase.expected_schema, null, 2)}</pre></div>`;
            }

            if (testCase.curl_command) {
                content += `<div><strong>cURL Command:</strong> <pre class="curl-command-pre">${testCase.curl_command}</pre><button class="copy-curl-btn-small" data-curl="${testCase.curl_command}">Copy</button></div>`;
            }

            // Add execution results if available
            if (testCase.execution_result && testCase.execution_result.response) {
                const response = testCase.execution_result.response;
                content += `<div class="execution-results"><strong>Execution Results:</strong>`;

                // Status Code
                if (response.status_code) {
                    content += `<div><strong>Status Code:</strong> ${response.status_code}</div>`;
                }

                // Response Time
                if (response.response_time) {
                    content += `<div><strong>Response Time:</strong> ${response.response_time} seconds</div>`;
                }

                // Response Content
                if (response.content) {
                    const contentStr = typeof response.content === 'object' ?
                        JSON.stringify(response.content, null, 2) :
                        response.content;
                    content += `<div><strong>Response Content:</strong> <pre>${contentStr}</pre></div>`;
                }

                content += `</div>`;
            }

            testCaseDiv.innerHTML = content;
            testCasesContainer.appendChild(testCaseDiv);
        });

        tabContentDiv.appendChild(testCasesContainer);
    });

   // Add event listeners for small copy buttons
    document.querySelectorAll(".copy-curl-btn-small").forEach(button => {
        button.addEventListener("click", (event) => {
            copyToClipboard(event.target.dataset.curl);
        });
    });

    // Initialize tab functionality
    setupTabs();
};

// Add this new function to handle tab switching
function setupTabs() {
    document.querySelectorAll(".tab-button").forEach(button => {
        button.addEventListener("click", (event) => {
            // Remove active class from all buttons
            document.querySelectorAll(".tab-button").forEach(btn => {
                btn.classList.remove("active");
            });

            // Add active class to clicked button
            event.target.classList.add("active");

            // Hide all tab contents
            document.querySelectorAll(".tab-content").forEach(content => {
                content.style.display = "none";
            });

            // Show the selected tab content
            const tabName = event.target.getAttribute("data-tab");
            const tabContent = document.getElementById(`${tabName}-tests`);
            if (tabContent) {
                tabContent.style.display = "block";
            }
        });
    });

    // Activate the first tab by default if there's no active tab
    if (!document.querySelector(".tab-button.active")) {
        const firstTab = document.querySelector(".tab-button");
        if (firstTab) {
            firstTab.click();
        }
    }
}

    // Tab switching logic
    document.querySelectorAll(".tab-button").forEach(button => {
        button.addEventListener("click", (event) => {
            document.querySelectorAll(".tab-button").forEach(btn => btn.classList.remove("active"));
            event.target.classList.add("active");

            document.querySelectorAll(".tab-content").forEach(content => hide(content));
            show(document.getElementById(`${event.target.dataset.tab}-tests`));
        });
    });

    // Initial call to set up method-based section visibility
    methodSelect.dispatchEvent(new Event("change"));

    // Copy cURL command from API Response section
    copyCurlBtn.addEventListener("click", () => {
        copyToClipboard(curlCommandPre.textContent);
    });
});







// Gradient color sets
const gradientColors = [
    ['#f9f5f1', '#f1f8f9'],  // Soft ivory to light teal
    ['#ffeaea', '#fff5f5'],  // Light blush pink
    ['#eaf3fd', '#f3f9fe'],  // Soft sky blue
    ['#e8fdf5', '#f0fcfa'],  // Minty green to aqua
    ['#f4efff', '#fae7fb'],  // Very light lavender to pink
    ['#fff8e7', '#fff0d9'],  // Cream to pale apricot
    ['#f6f0ff', '#eaf4ff'],  // Lavender haze to soft blue
    ['#f0ffe5', '#f6fff0'],  // Pale lime green
    ['#f0fffd', '#fff0f6'],  // Mint to very light rose
    ['#fafcff', '#f0f4fa']   // Cool fog gray to soft blue-gray
];

let currentIndex = 0;

function changeGradient() {
    currentIndex = (currentIndex + 1) % gradientColors.length;
    const [color1, color2] = gradientColors[currentIndex];
    document.body.style.background = `linear-gradient(to right, ${color1}, ${color2})`;
}

// Change gradient every 10 seconds
setInterval(changeGradient, 10000);

// Initialize with first gradient
changeGradient();


