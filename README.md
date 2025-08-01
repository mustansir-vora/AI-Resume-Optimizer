# AI-Powered Resume Optimizer

This Streamlit web application helps you tailor your resume for specific job applications using the power of Google's Gemini large language model. You can upload your resume in `.docx` format, provide the job role and description, and the application will rewrite your resume to better match the job requirements, while preserving the original formatting.

## Features

-   **Resume Parsing:** Extracts content and styling from `.docx` files, including text, formatting, and images.
-   **AI-Powered Optimization:** Leverages the Gemini LLM to optimize your resume content based on a provided job description.
-   **Format Preservation:** Reconstructs the `.docx` file with the optimized content while maintaining the original layout and styling.
-   **User-Friendly Interface:** A simple Streamlit interface for uploading your resume and entering job details.

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
└── temp/
```

-   `app.py`: The main Streamlit application file.
-   `docx_processor.py`: Handles the extraction and reconstruction of `.docx` files.
-   `llm_optimizer.py`: Contains the logic for interacting with the Gemini LLM.
-   `requirements.txt`: A list of all the dependencies required to run the project.
-   `.env`: For storing your Gemini API key.
-   `README.md`: This file.
-   `.gitignore`: Specifies which files and directories to ignore in the Git repository.
-   `temp/`: A temporary directory for storing uploaded resumes.

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

## Assumptions and Limitations

-   The application works best with standard resume formats.
-   Complex formatting, such as custom headers, footers, or intricate shapes, may not be perfectly preserved.
-   The quality of the optimization depends heavily on the detail of the job description provided.
