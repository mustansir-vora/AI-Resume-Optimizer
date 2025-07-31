import google.generativeai as genai
import os

def optimize_resume_with_llm(resume_xml, job_role, job_description):
    """
    Sends the resume XML to the Gemini API for optimization.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment variables.")

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')

    prompt = f"""
    You are an expert resume optimization AI. Your primary goal is to **optimize the provided resume content to perfectly align with the given job role and description**. Focus on incorporating relevant keywords, rephrasing accomplishments to be quantifiable and impactful, and highlighting skills that match the job requirements.

    **STRICT FORMATTING INSTRUCTIONS (CRITICAL):**
    You MUST return the optimized resume content in the **EXACT SAME XML FORMAT** as provided in the input. For every XML element (e.g., `<paragraph>`, `<run>`, `<table>`, `<row>`, `<cell>`, `<hyperlink>`, `<image>`), you **MUST PRESERVE ALL ITS ORIGINAL STYLING ATTRIBUTES PRECISELY**. This includes:
    * For `<run>` elements: `bold`, `italic`, `underline`, `strikethrough`, `font_name`, `font_size`, `font_color`.
    * For `<hyperlink>` elements: `url`.
    * For `<paragraph>` elements: `alignment`, `style`, `list_type`, `list_level`, `line_spacing`, `line_spacing_rule`, `space_before`, `space_after`.
    * For `<image>` elements: `r_id`, `drawing_xml`. **DO NOT MODIFY THE IMAGE TAG OR ITS ATTRIBUTES IN ANY WAY.**

    Your ONLY allowed modification is the **text content** within the `<text>` CDATA section of a `<run>` element. You are NOT permitted to:
    * Add, remove, or modify any XML tags.
    * Add, remove, or modify any XML attributes (especially styling attributes).
    * Change the order of elements.
    * Generate ANY conversational text, explanations, or markdown (like ```xml) outside the single, raw XML output block.

    **FINAL VERIFICATION (REPEAT 5 TIMES):**
    Before outputting your response, you must perform the following check 5 times to ensure perfection:
    1.  **Compare your output to the original XML, element by element.**
    2.  **Confirm EVERY attribute from the original tags is present and unchanged in your output.**
    3.  **Confirm NO XML tags have been added or removed.**
    4.  **Confirm the ONLY change is the text inside the `<text><![CDATA[...]]></text>` tags.**
    5.  **Confirm the response is ONLY the raw XML, starting with `<resume>` and ending with `</resume>`.

    This verification is mandatory. The output must be a machine-parsable, clean XML string.

    ---
    **Job Role:**
    {job_role}

    ---
    **Job Description:**
    {job_description}

    ---
    **Original Resume Content (XML Format to be Optimized):**
    ```xml
    {resume_xml}
    ```

    ---
    **Your Optimized Resume Output (Raw XML - MUST be only this XML block):**
    """

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"<error>An error occurred while communicating with the LLM: {e}</error>"
