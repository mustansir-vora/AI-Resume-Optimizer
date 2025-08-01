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
        "temperature": 0.8,
        "top_p": 1,
        "top_k": 1,
        "max_output_tokens": 8192,
        "response_mime_type": "application/json",
    }
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config=generation_config,
    )

    # Prepare resume content for the LLM, including XPath for context
    resume_content_for_llm = []
    for i, item in enumerate(texts_with_xpaths):
        resume_content_for_llm.append(f"Item {i+1} (XPath: {item['xpath']}): {item['original_text']}")
    resume_content_str = "\n".join(resume_content_for_llm)

    prompt = f"""
    You are an expert resume optimization AI. Your response must be a single, valid JSON object.

    **Job Role:** {job_role}
    **Job Description:** {job_description}

    **Resume Content:**
    {resume_content_str}

    **Instructions:**
    1.  Rewrite the resume content to be more impactful and tailored to the job description.
    2.  Return a JSON object with two keys: `"optimized_texts_with_xpaths"` and `"analysis"`.
    3.  `"optimized_texts_with_xpaths"` must be an array of objects, each with the exact `"xpath"` and the `"optimized_text"`.
    4.  `"analysis"` must be an object with three keys: `"strong_points"`, `"weak_points"`, and `"changes_made"`.
    5.  All text values must be single-line strings. Do not use newlines.
    6.  Properly escape all special characters.
    """

    try:
        response = model.generate_content(prompt, stream=True)
        full_response = ""
        for chunk in response:
            full_response += chunk.text
        return full_response
    except StopIteration:
        # Handle cases where the stream ends unexpectedly
        return json.dumps({"error": "The model stopped generating a response unexpectedly."})
    except Exception as e:
        return json.dumps({"error": f"An error occurred while communicating with the LLM: {e}"})