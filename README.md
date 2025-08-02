# AI-Powered Resume Optimizer

This Streamlit web application helps you tailor your resume for specific job applications using the power of Google's Gemini large language model. You can upload your resume in `.docx` format, provide the job role and description, and the application will rewrite your resume to better match the job requirements, while preserving the original formatting.

## Features

-   **Seamless `.docx` Processing:** Extracts content and styling from `.docx` files, ensuring that even complex layouts are preserved.
-   **AI-Powered Optimization:** Leverages the Gemini LLM to intelligently rewrite and tailor your resume content based on a provided job description.
-   **Format Preservation:** Reconstructs the `.docx` file with the optimized content while maintaining the original layout, fonts, and styling.
-   **User-Friendly Interface:** A simple and intuitive Streamlit interface for uploading your resume, entering job details, and downloading the optimized result.
-   **Detailed Analysis:** Provides a summary of the changes made, including strong points, weak points, and specific modifications.

## How It Works

1.  **Upload and Parse:** The application reads a `.docx` file and uses `lxml` to parse the underlying `document.xml`. It extracts every text element along with its unique XPath.
2.  **AI Optimization:** The extracted text and XPaths are sent to the Gemini LLM with a detailed prompt, including the job role and description. The LLM rewrites the content to align with the job requirements.
3.  **JSON-Formatted Response:** The LLM returns a structured JSON object containing the optimized text and the corresponding XPaths, along with an analysis of the changes.
4.  **Reconstruction:** The application creates a new `.docx` file in memory. It iterates through the original document's structure and replaces the text at each XPath with the optimized content.
5.  **Download:** The newly generated `.docx` file is made available for download, preserving the original formatting.

## Project Structure

```
.
├── .env
├── .gitignore
├── app.py
├── docx_processor.py
├── llm_optimizer.py
├── README.md
├── requirements.txt
├── __pycache__/
├── .devcontainer/
└── temp/
```

### Key Components

-   `app.py`: The main Streamlit application. It handles the user interface, file uploads, and orchestrates the optimization process.
-   `docx_processor.py`: Contains the core logic for processing `.docx` files. It uses `python-docx` and `lxml` to extract text with its XPath and to replace it in a new document.
-   `llm_optimizer.py`: Manages the interaction with the Google Gemini API. It constructs the prompt, sends the request, and processes the JSON response.
-   `requirements.txt`: A list of all the Python dependencies required to run the project.
-   `.env`: Used for storing the Gemini API key securely.
-   `temp/`: A temporary directory for storing uploaded resumes during processing.

## Technical Details

-   **XPath for Precision:** The application uses XPath to identify the exact location of each text element in the XML structure of the `.docx` file. This allows for precise replacement of content without disrupting the document's formatting.
-   **JSON for Structured Data:** The communication with the Gemini LLM is standardized using JSON. This ensures that the response is structured and can be reliably parsed by the application.
-   **Error Handling:** The application includes robust error handling to manage potential issues with file processing, API communication, and JSON parsing.

## Setup and Installation

To run this project locally, follow these steps:

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/AI-Resume-Optimizer.git
cd AI-Resume-Optimizer
```

### 2. Create a Virtual Environment

It's recommended to use a virtual environment to manage the project's dependencies.

```bash
# For Windows
python -m venv .venv
.venv\Scripts\activate

# For macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

Install all the required packages from the `requirements.txt` file.

```bash
pip install -r requirements.txt
```

### 4. Set Up Your API Key

You'll need a Gemini API key to use this application.

1.  Open the file named `.env` in the root of the project directory.
2.  Add the following line to the `.env` file, replacing `YOUR_API_KEY_HERE` with your actual Gemini API key:

```
GEMINI_API_KEY='Your_key_here'
```

## How to Run the Application

Once you've completed the setup, you can run the Streamlit application with the following command:

```bash
streamlit run app.py
```

This will start the application, and you can access it in your web browser at `http://localhost:8501`.

## How to Use the Application

1.  **Upload Your Resume:** Click the "Upload your resume (.docx)" button to upload your resume in `.docx` format.
2.  **Enter Job Details:**
    -   In the "Job Role" field, enter the title of the job you're applying for.
    -   In the "Job Description" field, paste the full job description.
3.  **Optimize Your Resume:** Click the "Optimize Resume" button to start the optimization process.
4.  **Download Your Optimized Resume:** Once the optimization is complete, a "Download Optimized Resume" button will appear. Click it to download your new, tailored resume.