import streamlit as st
import os
import json
import re
from docx_processor import extract_text_with_context, replace_text_in_document
from llm_optimizer import optimize_resume_with_llm
from io import BytesIO
from dotenv import load_dotenv

load_dotenv()

# --- Streamlit Page Configuration ---
st.set_page_config(
    page_title="AI Resume Optimizer",
    page_icon="✨",
    layout="wide",
)

# --- Custom CSS for a more polished look ---
st.markdown("""
<style>
    .stButton>button {
        border-radius: 20px;
        border: 1px solid #3A6DC2;
        background-color: #FFFFFF;
        color: black;
        transition: all 0.2s ease-in-out;
    }
    .stButton>button:hover {
        background-color: #ADD8E6;
        border: 1px solid #3A6DC2;
    }
    .stDownloadButton>button {
        border-radius: 20px;
        border: 1px solid #3A6DC2;
        background-color: #FFFFFF;
        color: white;
        transition: all 0.2s ease-in-out;
    }
    .stDownloadButton>button:hover {
        background-color: #ADD8E6;
        border: 1px solid #3A6DC2;
    }
    .st-emotion-cache-1y4p8pa {
        padding-top: 2rem;
    }
    .st-emotion-cache-1v0mbdj {
        gap: 1rem;
    }
    .st-emotion-cache-16txtl3 {
        padding: 2rem 1rem;
    }
    h1, h2, h3 {
        color: #2c3e50;
    }
</style>
""", unsafe_allow_html=True)


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
    # Clear all result-related keys from session state
    for key in ['optimized_doc', 'images_data', 'job_role_for_download', 'strong_points', 'weak_points', 'changes_made', 'llm_response']:
        if key in st.session_state:
            del st.session_state[key]

def clean_llm_json_response(response_text):
    """
    Extracts and cleans a JSON object from a string that may contain markdown code fences
    and other non-JSON text.
    """
    # Attempt to extract JSON from a markdown code block
    match = re.search(r"```json\n(.*?)\n```", response_text, re.DOTALL)
    if match:
        response_text = match.group(1)

    # Find the start of the first JSON object
    json_start = response_text.find('{')
    if json_start != -1:
        # Find the corresponding closing brace
        brace_count = 0
        json_end = -1
        for i, char in enumerate(response_text[json_start:]):
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
            if brace_count == 0:
                json_end = json_start + i + 1
                break
        if json_end != -1:
            response_text = response_text[json_start:json_end]

    # Final check for completeness
    if not response_text.startswith('{') or not response_text.endswith('}'):
        raise ValueError("Incomplete JSON response from LLM.")

    return response_text.strip()

st.title("📄✨ AI-Powered Resume Optimizer")
st.markdown("Transform your resume to perfectly match your dream job. Upload your resume, paste the job description, and let Gemini AI work its magic!")

st.markdown("---")

# --- Gemini API Key Check ---
if not os.getenv("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY") == "YOUR_API_KEY_HERE":
    st.warning("⚠️ Please enter your Gemini API Key in the `.env` file to proceed.")
    st.stop()

# --- Core Application Flow ---
col1, col2 = st.columns([2, 3])

# Create a dynamic key for the file uploader
file_uploader_key = f"file_uploader_{st.session_state.reset_counter}"

with col1:
    st.header("1. Your Information")
    uploaded_file = st.file_uploader(
        "📁 Upload your resume (.docx)", 
        type=["docx"], 
        key=file_uploader_key
    )

with col2:
    st.header("2. The Job You Want")
    job_role = st.text_input("🎯 Job Role", key="job_role", placeholder="e.g., Senior Python Developer")
    job_description = st.text_area("📋 Job Description", height=200, key="job_description", placeholder="Paste the full job description here...")

# --- Buttons ---
st.markdown("<br>", unsafe_allow_html=True)
button_col1, button_col2, _ = st.columns([1, 1, 3])

with button_col1:
    optimize_button = st.button("🚀 Optimize My Resume", type="primary", use_container_width=True)

with button_col2:
    st.button("🔄 Reset Fields", on_click=reset_fields, use_container_width=True)


if optimize_button:
    # Get values from session state
    job_role = st.session_state.job_role
    job_description = st.session_state.job_description

    # We need to get the uploaded file from the session state using the dynamic key
    uploaded_file = st.session_state.get(file_uploader_key)

    if not all([uploaded_file, job_role, job_description]):
        st.error("❗️ Please upload a resume and fill in all job details before optimizing.")
    else:
        try:
            st.session_state.job_role_for_download = job_role

            with st.spinner("Step 1/3: Processing your resume..."):
                temp_dir = "temp"
                if not os.path.exists(temp_dir):
                    os.makedirs(temp_dir)
                
                file_path = os.path.join(temp_dir, uploaded_file.name)
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

                st.info("✅ Resume content extracted.")
                texts_with_xpaths = extract_text_with_context(file_path)
                st.session_state.texts_with_xpaths = texts_with_xpaths # Store for later replacement

            with st.spinner("Step 2/3: AI is optimizing your resume... This may take a moment."):
                llm_response_text = optimize_resume_with_llm(st.session_state.texts_with_xpaths, job_role, job_description)
                st.session_state.llm_response = llm_response_text # Save for debugging
                st.info("✅ AI optimization complete.")

            with st.spinner("Step 3/3: Generating your new resume..."):
                try:
                    llm_response_text_cleaned = clean_llm_json_response(llm_response_text)
                    llm_response_json = json.loads(llm_response_text_cleaned)
                    
                    if "error" in llm_response_json:
                        st.error(f"An error occurred during optimization: {llm_response_json['error']}")
                    else:
                        analysis = llm_response_json.get("analysis", {})
                        
                        strong_points = analysis.get("strong_points", "N/A")
                        weak_points = analysis.get("weak_points", "N/A")
                        changes_made = analysis.get("changes_made", "N/A")

                        optimized_texts_with_xpaths = llm_response_json.get("optimized_texts_with_xpaths", [])

                        if not optimized_texts_with_xpaths:
                            st.error("LLM did not return optimized content with XPaths.")
                        else:
                            # Call the new function to replace content in the original document
                            optimized_doc_buffer = replace_text_in_document(file_path, optimized_texts_with_xpaths)
                            st.session_state.optimized_doc_buffer = optimized_doc_buffer
                            st.session_state.strong_points = strong_points
                            st.session_state.weak_points = weak_points
                            st.session_state.changes_made = changes_made
                            st.success("🎉 Your new resume is ready!")
                            st.balloons()

                except json.JSONDecodeError as e:
                    st.error(f"Failed to parse LLM response as JSON. Error: {e}. Raw response below.")
                    st.code(llm_response_text, language='text')
                except Exception as e:
                    st.error(f"An error occurred during response processing: {e}")

        except FileNotFoundError as e:
            st.error(f"Error: {e}")
        except ValueError as e:
            st.error(f"An error occurred during processing: {e}")
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")

# --- Download and Summary Section ---
if 'optimized_doc_buffer' in st.session_state:
    st.markdown("---")
    st.header("3. Your Optimized Results")

    download_job_role = st.session_state.get('job_role_for_download', 'Optimized')

    st.download_button(
        label=f"📥 Download Optimized Resume for {download_job_role}",
        data=st.session_state.optimized_doc_buffer.getvalue(),
        file_name=f"Optimized_Resume_{download_job_role.replace(' ', '_')}.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        use_container_width=True
    )

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("🔍 Optimization Summary")

    summary_col1, summary_col2, summary_col3 = st.columns(3)
    with summary_col1:
        with st.container(border=True):
            st.markdown("<h5>👍 Strong Points</h5>", unsafe_allow_html=True)
            st.markdown(st.session_state.get('strong_points', 'No strong points identified.'))

    with summary_col2:
        with st.container(border=True):
            st.markdown("<h5>👎 Weak Points</h5>", unsafe_allow_html=True)
            st.markdown(st.session_state.get('weak_points', 'No weak points identified.'))

    with summary_col3:
        with st.container(border=True):
            st.markdown("<h5>✨ Changes Made</h5>", unsafe_allow_html=True)
            st.markdown(st.session_state.get('changes_made', 'No changes described.'))

# --- Debugging Section ---
if 'llm_response' in st.session_state:
    with st.expander("Show Raw LLM Response (for Debugging)"):
        st.code(st.session_state.llm_response, language='json')

# --- Sidebar and Footer ---
st.sidebar.markdown("---")
st.sidebar.header("About this App")
st.sidebar.info(
    "This app uses Google's Gemini model to rewrite your resume, "
    "tailoring it to a specific job description while preserving the original formatting."
)
st.sidebar.header("Assumptions & Limitations")
st.sidebar.info(
    "- The app works best with standard resume formats.\n"
    "- Complex formatting like custom headers/footers or intricate shapes might not be perfectly preserved.\n"
    "- The quality of the optimization depends heavily on the detail of the job description provided."
)

st.markdown("<br><br><hr>", unsafe_allow_html=True)
st.markdown("<div style='text-align: center; color: grey;'>Made with ❤️ using Streamlit & Gemini</div>", unsafe_allow_html=True)