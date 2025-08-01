import zipfile
from lxml import etree
from io import BytesIO
import json

WORD_NAMESPACE = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
PARA = WORD_NAMESPACE + 'p'
RUN = WORD_NAMESPACE + 'r'
TEXT = WORD_NAMESPACE + 't'

def extract_text_with_context(docx_path):
    """
    Extracts text from a DOCX document along with its XPath context.
    """
    texts_with_xpaths = []
    try:
        with zipfile.ZipFile(docx_path, 'r') as docx_zip:
            with docx_zip.open('word/document.xml') as doc_xml_file:
                tree = etree.parse(doc_xml_file)
                root = tree.getroot()

                for text_element in root.xpath('//w:t', namespaces={'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}):
                    # Get the XPath of the text element
                    xpath = tree.getpath(text_element)
                    texts_with_xpaths.append({
                        'original_text': text_element.text if text_element.text is not None else '',
                        'xpath': xpath
                    })
    except Exception as e:
        raise RuntimeError(f"Error extracting text from DOCX: {e}")
    return texts_with_xpaths

def replace_text_in_document(original_docx_path, optimized_texts_with_xpaths):
    """
    Replaces text in the DOCX document based on provided XPath and optimized text.
    Returns a BytesIO object containing the modified DOCX.
    """
    new_docx_buffer = BytesIO()

    try:
        with zipfile.ZipFile(original_docx_path, 'r') as docx_zip:
            with zipfile.ZipFile(new_docx_buffer, 'w', compression=zipfile.ZIP_DEFLATED) as new_zip:
                # Copy all files from original to new zip, except document.xml
                for item in docx_zip.infolist():
                    if item.filename == 'word/document.xml':
                        continue
                    new_zip.writestr(item, docx_zip.read(item.filename))

                # Read and parse document.xml
                with docx_zip.open('word/document.xml') as doc_xml_file:
                    tree = etree.parse(doc_xml_file)
                    root = tree.getroot()

                    # Create a dictionary for faster lookup of optimized texts by XPath
                    optimized_map = {item['xpath']: item['optimized_text'] for item in optimized_texts_with_xpaths}

                    # Iterate through all text elements and replace their content
                    for text_element in root.xpath('//w:t', namespaces={'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}):
                        xpath = tree.getpath(text_element)
                        if xpath in optimized_map:
                            text_element.text = optimized_map[xpath]

                    # Write the modified document.xml back to the new zip
                    modified_xml_content = etree.tostring(root, pretty_print=True, encoding='UTF-8', xml_declaration=True)
                    new_zip.writestr('word/document.xml', modified_xml_content)

    except Exception as e:
        raise RuntimeError(f"Error replacing text in DOCX: {e}")

    new_docx_buffer.seek(0)
    return new_docx_buffer