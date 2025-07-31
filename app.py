import streamlit as st
import os
from docx_processor import extract_docx_to_xml, create_docx_from_xml
from llm_optimizer import optimize_resume_with_llm
from io import BytesIO
from dotenv import load_dotenv

load_dotenv()

# --- Streamlit Page Configuration ---
st.set_page_config(
    page_title="Resume Optimizer",
    page_icon="✨",
    layout="wide",
)

# --- Initialize Session State for Reset --- 
if 'reset_counter' not in st.session_state:
    st.session_state.reset_counter = 0
if 'job_role' not in st.session_state:
    st.session_state.job_role = ""
if 'job_description' not in st.session_state:
    st.session_state.job_description = ""

# --- Reset Callback --- 
def reset_fields():
    """Clears all input fields and session state by incrementing a counter for the file_uploader key."""
    st.session_state.reset_counter += 1
    st.session_state.job_role = ""
    st.session_state.job_description = ""
    for key in ['optimized_doc', 'images_data', 'job_role_for_download']:
        if key in st.session_state:
            del st.session_state[key]

# --- Main Application UI ---
st.title("📄✨ Resume Optimizer powered by Gemini")
st.markdown("Upload your resume, provide the job details, and let AI tailor your resume for the perfect fit!")

# --- Gemini API Key Check ---
if not os.getenv("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY") == "YOUR_API_KEY_HERE":
    st.warning("Please enter your Gemini API Key in the .env file to proceed.")
    st.stop()

# --- Core Application Flow ---
col1, col2 = st.columns(2)

# Create a dynamic key for the file uploader
file_uploader_key = f"file_uploader_{st.session_state.reset_counter}"

with col1:
    st.header("Your Resume")
    uploaded_file = st.file_uploader(
        "Upload your resume (.docx)", 
        type=["docx"], 
        key=file_uploader_key
    )

with col2:
    st.header("Job Details")
    job_role = st.text_input("Job Role", key="job_role")
    job_description = st.text_area("Job Description", height=200, key="job_description")

# --- Buttons ---
button_col1, button_col2, _ = st.columns([1, 1, 5])

with button_col1:
    optimize_button = st.button("Optimize Resume", type="primary", use_container_width=True)

with button_col2:
    st.button("Reset", on_click=reset_fields, use_container_width=True)


if optimize_button:
    # Get values from session state, using the dynamic key for the file uploader
    uploaded_file = st.session_state[file_uploader_key]
    job_role = st.session_state.job_role
    job_description = st.session_state.job_description

    if not all([uploaded_file, job_role, job_description]):
        st.error("Please upload a resume and fill in all job details.")
    else:
        try:
            st.session_state.job_role_for_download = job_role

            with st.spinner("Processing your resume..."):
                temp_dir = "temp"
                if not os.path.exists(temp_dir):
                    os.makedirs(temp_dir)
                
                file_path = os.path.join(temp_dir, uploaded_file.name)
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

                st.info("Extracting resume content and formatting...")
                resume_xml, images_data = extract_docx_to_xml(file_path)
                st.session_state.images_data = images_data

            with st.spinner("AI is optimizing your resume... This may take a moment."):
                st.info("Sending to AI for optimization...")
                optimized_xml = optimize_resume_with_llm(resume_xml, job_role, job_description)

            with st.spinner("Generating your new resume..."):
                st.info("Generating optimized DOCX...")
                if "<error>" in optimized_xml:
                    st.error(f"An error occurred during optimization: {optimized_xml}")
                else:
                    images_to_use = st.session_state.get('images_data', {})
                    optimized_doc = create_docx_from_xml(optimized_xml, images_to_use)
                    st.session_state.optimized_doc = optimized_doc
                    st.success("Resume optimization complete!")

        except FileNotFoundError as e:
            st.error(f"Error: {e}")
        except ValueError as e:
            st.error(f"An error occurred during processing: {e}")
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")

# --- Download Button --- 
if 'optimized_doc' in st.session_state:
    st.header("Download Your Optimized Resume")
    bio = BytesIO()
    st.session_state.optimized_doc.save(bio)
    
    download_job_role = st.session_state.get('job_role_for_download', 'Optimized')

    st.download_button(
        label="Download Optimized Resume",
        data=bio.getvalue(),
        file_name=f"Optimized_Resume_{download_job_role.replace(' ', '_')}.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )

# --- Assumptions and Limitations ---
st.sidebar.markdown("---")
st.sidebar.header("Assumptions & Limitations")
st.sidebar.info(
    "- The app works best with standard resume formats.\n"
    "- Complex formatting like custom headers/footers or intricate shapes might not be perfectly preserved.\n"
    "- The quality of the optimization depends heavily on the detail of the job description provided."
)
