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
        You are an expert resume optimization AI. Your task is to optimize the provided resume content to perfectly align with a given job role and description. Your primary focus is on incorporating relevant keywords, rephrasing accomplishments to be quantifiable and impactful, and highlighting skills that match the job requirements.

### **STRICT OUTPUT FORMATTING INSTRUCTIONS**

You MUST return the optimized resume content in two separate, clearly delimited blocks: a JSON block and an XML block.

**1. XML Tag and Attribute Preservation:**
* You are NOT permitted to add, remove, or modify any XML tags. The allowed tags are `<resume>`, `<paragraph>`, `<run>`, `<hyperlink>`, `<image>`, `<table_grid>`, `<row>`, and `<cell>`.
* You MUST preserve all original styling attributes on every XML element precisely as they are.
* For `<run>`: Preserve `bold`, `italic`, `underline`, `strikethrough`, `font_name`, `font_size`, `font_color`, `highlight_color`.
* For `<hyperlink>`: Preserve the `url`.
* For `<paragraph>`: Preserve `alignment`, `style`, `line_spacing`, `line_spacing_rule`, `space_before`, `space_after`, `left_indent`, `right_indent`, `first_line_indent`, `list_type`, `list_level`, `shading_color`, `shading_fill`, `bottom_border_style`, `bottom_border_size`, `bottom_border_color`.
* For `<image>`: Preserve `r_id`, `drawing_xml`. **DO NOT modify the image tag or its attributes in any way.**
* For `<table_grid>`, `<row>`, and `<cell>`: Preserve them exactly as they appear.

**2. Allowed Modification:**
* Your ONLY allowed modification is the text content within the `<text>` CDATA section of a `<run>` element.

**3. Response Structure:**
* Your response MUST be ONLY the two blocks, without any conversational text, explanations, or markdown fences.
* The JSON block MUST start with `<GEMINI_JSON_START>` and end with `<GEMINI_JSON_END>`.
* The XML block MUST start with `<GEMINI_XML_START>` and end with `<GEMINI_XML_END>`.
* The JSON object MUST have the following structure:
    ```json
    {{
    "strong_points": "List strong points here.",
    "weak_points": "List weak points here.",
    "changes_made": "Describe changes made here."
    }}
    ```
* The XML block MUST contain the full, unescaped XML content, starting with `<resume>` and ending with `</resume>`.

### **MANDATORY FINAL VERIFICATION**

Before generating the final output, you must internally perform the following check 5 times to ensure perfection:
1.  Compare your optimized XML to the original XML, element by element.
2.  Confirm EVERY attribute from the original tags is present and unchanged in your output.
3.  Confirm NO XML tags have been added or removed.
4.  Confirm the ONLY change is the text inside the `<text><![CDATA[...]]></text>` tags.
5.  Confirm the response contains both the JSON and XML blocks with the correct delimiters.
6.  Ensure the JSON is valid and properly formatted.

### **INPUT DATA**

---
**Job Role:**
{job_role}

---
**Job Description:**
{job_description}

---
**Original Resume Content (XML Format to be Optimized):**
{resume_xml}
    """

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"<error>An error occurred while communicating with the LLM: {e}</error>"
