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

# --- Main Application UI ---
st.title("📄✨ Resume Optimizer powered by Gemini")
st.markdown("Upload your resume, provide the job details, and let AI tailor your resume for the perfect fit!")

# --- Gemini API Key Check ---
if not os.getenv("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY") == "YOUR_API_KEY_HERE":
    st.warning("Please enter your Gemini API Key in the .env file to proceed.")
    st.stop()

# --- Core Application Flow ---
col1, col2 = st.columns(2)

with col1:
    st.header("Your Resume")
    uploaded_file = st.file_uploader("Upload your resume (.docx)", type=["docx"])

with col2:
    st.header("Job Details")
    job_role = st.text_input("Job Role")
    job_description = st.text_area("Job Description", height=200)

optimize_button = st.button("Optimize Resume", type="primary")

if optimize_button:
    if not all([uploaded_file, job_role, job_description]):
        st.error("Please upload a resume and fill in all job details.")
    else:
        try:
            # 1. Save uploaded file temporarily
            with st.spinner("Processing your resume..."):
                temp_dir = "temp"
                if not os.path.exists(temp_dir):
                    os.makedirs(temp_dir)
                
                file_path = os.path.join(temp_dir, uploaded_file.name)
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

                # 2. Extract content to XML
                st.info("Extracting resume content and formatting...")
                resume_xml, images_data = extract_docx_to_xml(file_path)
                st.session_state.images_data = images_data # Store images for later

            # 3. Send to LLM for optimization
            with st.spinner("AI is optimizing your resume... This may take a moment."):
                st.info("Sending to AI for optimization...")
                optimized_xml = optimize_resume_with_llm(resume_xml, job_role, job_description)

            # 4. Reconstruct DOCX from optimized XML
            with st.spinner("Generating your new resume..."):
                st.info("Generating optimized DOCX...")
                if "<error>" in optimized_xml:
                    st.error(f"An error occurred during optimization: {optimized_xml}")
                else:
                    optimized_doc = create_docx_from_xml(optimized_xml, st.session_state.images_data)
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
    st.download_button(
        label="Download Optimized Resume",
        data=bio.getvalue(),
        file_name=f"Optimized_Resume_{job_role.replace(' ', '_')}.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )

# --- Assumptions and Limitations ---
st.sidebar.markdown("---")
st.sidebar.header("Assumptions & Limitations")
st.sidebar.info(
    "- The app works best with standard resume formats.\n"
    "- Complex formatting like custom headers/footers or intricate shapes might not be perfectly preserved.\n"
    "- Hyperlink reconstruction is a known limitation of the underlying library.\n"
    "- The quality of the optimization depends heavily on the detail of the job description provided."
)
