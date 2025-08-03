import google.generativeai as genai
import os
import json

def optimize_resume_with_llm(texts_with_xpaths, job_role, job_description):
    """
    Sends the resume content (as a list of dictionaries with text and XPath) to the Gemini API for optimization.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment variables.")

    genai.configure(api_key=api_key)
    generation_config = {
        "temperature": 0.7,
        "top_p": 1,
        "top_k": 1,
        "max_output_tokens": 65535,
        "response_mime_type": "application/json",
    }
    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        generation_config=generation_config,
    )

    # Prepare resume content for the LLM, including XPath for context
    resume_content_for_llm = []
    for i, item in enumerate(texts_with_xpaths):
        resume_content_for_llm.append(f"Item {i+1} (XPath: {item['xpath']}): {item['original_text']}")
    resume_content_str = "\n".join(resume_content_for_llm)

    prompt = f"""
    You are an expert resume optimization AI. Your response must be a single, valid JSON object.

    **Job Role:** 
    {job_role}

    **Job Description:** 
    {job_description}

    **Resume Content:**
    {resume_content_str}

    *Instructions:**
    1. Rewrite the resume content to be more impactful and tailored to the job description.
    2. Return a JSON object with two keys: `"optimized_texts_with_xpaths"` and `"analysis"`.
    3. `"optimized_texts_with_xpaths"` must be an array of objects, each with the exact `"xpath"` and the `"optimized_text"`.
    4. `"analysis"` must be an object with three keys: `"strong_points"`, `"weak_points"`, and `"changes_made"`.
    5. All text values must be single-line strings. Do not use newlines.
    6. Properly escape all special characters.

    **Pre-computation Checklists:**
    * [ ] **Resume Content Analysis:** Extract and identify key skills, experiences, and achievements from the provided `resume_content_str`. Map these points to the requirements and keywords in the `job_description`. Note any gaps where the resume content doesn't align with the job description.
    * [ ] **Optimization Strategy:** Draft a new, more impactful version for each relevant resume section, focusing on action verbs and quantifying achievements. Incorporate keywords from the `job_description` and ensure the rewritten text is concise and results-oriented.

    **Final Output Validation Checklists:**
    * [ ] **JSON Validity Check:** Confirm the final output is a single, valid JSON object. Ensure proper nesting and correct use of braces `{{}}` and brackets `[]`. Verify all keys and string values are enclosed in double quotes `""` and there are no trailing commas.
    * [ ] **Key and Structure Compliance Check:** The root object must contain exactly two keys: `"optimized_texts_with_xpaths"` and `"analysis"`. `"optimized_texts_with_xpaths"` must be an array of objects, each with `"xpath"` and `"optimized_text"`. `"analysis"` must be an object with `"strong_points"`, `"weak_points"`, and `"changes_made"`.
    * [ ] **Content and Formatting Check:** All string values must be single-line and properly escaped. The optimized text should be more impactful and tailored to the job description, and the xpaths should be accurate.
    * [ ] **Final Review:** Reread the entire generated JSON object to confirm all instructions have been met and the output is coherent, professional, and accurate before sending the final response.
    """

    try:
        response = model.generate_content(prompt)
        # The response is already a complete JSON object because of `response_mime_type="application/json"`
        # We can directly access the text part, which should be a valid JSON string.
        return response.text
    except Exception as e:
        # Log the error for debugging purposes
        print(f"An error occurred while communicating with the LLM: {e}")
        # Return a JSON object with an error message
        return json.dumps({"error": f"An error occurred while communicating with the LLM: {e}"})