
import os
import re
from docx import Document
from docx.shared import Pt, RGBColor, Emu
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import qn
from lxml import etree
from io import BytesIO

# Namespace map for parsing DOCX XML
ns = {
    'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
    'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
    'wp': 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing',
    'a': 'http://schemas.openxmlformats.org/drawingml/2006/main'
}

def _get_run_properties_from_element(r_element):
    """Extracts properties directly from a w:r OxmlElement."""
    props = {
        "bold": "false", "italic": "false", "underline": "false",
        "strikethrough": "false", "font_name": "Unknown",
        "font_size": "0", "font_color": "#000000"
    }
    rPr = r_element.find('w:rPr', namespaces=ns)
    if rPr is None: return props

    if rPr.find('w:b', namespaces=ns) is not None: props['bold'] = "true"
    if rPr.find('w:i', namespaces=ns) is not None: props['italic'] = "true"
    if rPr.find('w:u', namespaces=ns) is not None: props['underline'] = "true"
    if rPr.find('w:strike', namespaces=ns) is not None: props['strikethrough'] = "true"
    rFonts = rPr.find('w:rFonts', namespaces=ns)
    if rFonts is not None and rFonts.get(qn('w:ascii')):
        props['font_name'] = rFonts.get(qn('w:ascii'))
    sz = rPr.find('w:sz', namespaces=ns)
    if sz is not None and sz.get(qn('w:val')):
        try:
            props['font_size'] = str(int(sz.get(qn('w:val'))) / 2)
        except (ValueError, TypeError): pass
    color = rPr.find('w:color', namespaces=ns)
    if color is not None and color.get(qn('w:val')):
        props['font_color'] = f"#{color.get(qn('w:val'))}"
    return props

def extract_docx_to_xml(docx_file_path):
    """
    Converts a DOCX file to a structured XML string, preserving content, styling, hyperlinks, and full image formatting.
    Returns the XML string and a dictionary containing image data.
    """
    if not os.path.exists(docx_file_path):
        raise FileNotFoundError(f"File not found: {docx_file_path}")

    doc = Document(docx_file_path)
    resume_xml = etree.Element("resume")
    images_data = {}

    for p_obj in doc.paragraphs:
        p_xml = etree.SubElement(resume_xml, "paragraph")
        pf = p_obj.paragraph_format
        p_xml.set("alignment", str(p_obj.alignment).split(' ')[0] if p_obj.alignment else "left")
        p_xml.set("style", p_obj.style.name)
        p_xml.set("line_spacing", str(pf.line_spacing or 0))
        p_xml.set("line_spacing_rule", str(pf.line_spacing_rule or ''))
        p_xml.set("space_before", str(pf.space_before.pt) if pf.space_before else "0")
        p_xml.set("space_after", str(pf.space_after.pt) if pf.space_after else "0")

        for child in p_obj._p:
            if child.tag == qn('w:r'):
                drawing = child.find('w:drawing', namespaces=ns)
                if drawing is not None:
                    blip = drawing.find('.//a:blip', namespaces=ns)
                    if blip is not None:
                        r_id = blip.get(qn('r:embed'))
                        if r_id and r_id in doc.part.rels:
                            image_part = doc.part.rels[r_id].target_part
                            images_data[r_id] = {
                                'bytes': image_part.blob,
                                'content_type': image_part.content_type
                            }
                            img_xml = etree.SubElement(p_xml, "image")
                            img_xml.set("r_id", r_id)
                            drawing_str = etree.tostring(drawing).decode()
                            img_xml.set("drawing_xml", drawing_str)
                        continue

                r_xml = etree.SubElement(p_xml, "run")
                run_props = _get_run_properties_from_element(child)
                for key, value in run_props.items(): r_xml.set(key, value)
                text = ''.join(t.text for t in child.findall('.//w:t', namespaces=ns) if t.text)
                text_element = etree.SubElement(r_xml, "text")
                text_element.text = etree.CDATA(text)

            elif child.tag == qn('w:hyperlink'):
                r_id = child.get(qn('r:id'))
                if not r_id or r_id not in p_obj.part.rels: continue
                url = p_obj.part.rels[r_id].target_ref
                hlink_xml = etree.SubElement(p_xml, "hyperlink")
                hlink_xml.set("url", url)
                for run_element in child.findall('.//w:r', namespaces=ns):
                    r_xml = etree.SubElement(hlink_xml, "run")
                    run_props = _get_run_properties_from_element(run_element)
                    for key, value in run_props.items(): r_xml.set(key, value)
                    text = ''.join(t.text for t in run_element.findall('.//w:t', namespaces=ns) if t.text)
                    text_element = etree.SubElement(r_xml, "text")
                    text_element.text = etree.CDATA(text)

    xml_string = etree.tostring(resume_xml, pretty_print=True, xml_declaration=True, encoding='UTF-8').decode('utf-8')
    return xml_string, images_data

def _apply_run_properties(run, run_attrs):
    run.bold = run_attrs.get("bold") == "true"
    run.italic = run_attrs.get("italic") == "true"
    run.underline = run_attrs.get("underline") == "true"
    run.font.strike = run_attrs.get("strikethrough") == "true"
    if "font_name" in run_attrs and run_attrs['font_name'] != "Unknown":
        run.font.name = run_attrs["font_name"]
    if "font_size" in run_attrs and float(run_attrs.get("font_size", 0)) > 0:
        run.font.size = Pt(float(run_attrs["font_size"]))
    if "font_color" in run_attrs and run_attrs['font_color'] != "#000000":
        try:
            color = run_attrs["font_color"].lstrip('#')
            if len(color) == 6: run.font.color.rgb = RGBColor.from_string(color)
        except ValueError: pass

def _add_hyperlink(paragraph, url, runs_data):
    part = paragraph.part
    r_id = part.relate_to(url, 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink', is_external=True)
    hyperlink = OxmlElement('w:hyperlink')
    hyperlink.set(qn('r:id'), r_id)
    for run_data in runs_data:
        run_element = OxmlElement('w:r')
        rPr = OxmlElement('w:rPr')
        if run_data['attrs'].get("bold") == "true": rPr.append(OxmlElement('w:b'))
        r_style = OxmlElement('w:rStyle')
        r_style.set(qn('w:val'), 'Hyperlink')
        rPr.append(r_style)
        run_element.append(rPr)
        t = OxmlElement('w:t')
        t.text = run_data['text']
        run_element.append(t)
        hyperlink.append(run_element)
    paragraph._p.append(hyperlink)

def create_docx_from_xml(optimized_xml_string, images_data):
    """
    Creates a DOCX file from a structured XML string, preserving styling, hyperlinks, and re-inserting images with full formatting.
    """
    try:
        xml_match = re.search(r'<resume>.*</resume>', optimized_xml_string, re.DOTALL)
        if not xml_match: raise ValueError("No <resume> tag found in the LLM output.")
        clean_xml = xml_match.group(0)
        root = etree.fromstring(clean_xml)
    except etree.XMLSyntaxError as e:
        raise ValueError(f"Failed to parse XML from LLM output: {e}")

    doc = Document()
    alignment_map = {"left": WD_ALIGN_PARAGRAPH.LEFT, "center": WD_ALIGN_PARAGRAPH.CENTER, "right": WD_ALIGN_PARAGRAPH.RIGHT, "justify": WD_ALIGN_PARAGRAPH.JUSTIFY}
    line_spacing_map = {'SINGLE': WD_LINE_SPACING.SINGLE, 'ONE_POINT_FIVE': WD_LINE_SPACING.ONE_POINT_FIVE, 'DOUBLE': WD_LINE_SPACING.DOUBLE, 'AT_LEAST': WD_LINE_SPACING.AT_LEAST, 'EXACTLY': WD_LINE_SPACING.EXACTLY, 'MULTIPLE': WD_LINE_SPACING.MULTIPLE}

    for element in root:
        if element.tag == 'paragraph':
            p = doc.add_paragraph()
            para_attrs = element.attrib
            p.alignment = alignment_map.get(para_attrs.get("alignment", "left").lower(), WD_ALIGN_PARAGRAPH.LEFT)
            try:
                p.style = para_attrs.get("style", "Normal")
            except Exception: p.style = "Normal"
            pf = p.paragraph_format
            if para_attrs.get("line_spacing_rule") in line_spacing_map: pf.line_spacing_rule = line_spacing_map[para_attrs["line_spacing_rule"]]
            if float(para_attrs.get("line_spacing", 0)) > 0: pf.line_spacing = float(para_attrs["line_spacing"])
            if float(para_attrs.get("space_before", 0)) > 0: pf.space_before = Pt(float(para_attrs["space_before"]))
            if float(para_attrs.get("space_after", 0)) > 0: pf.space_after = Pt(float(para_attrs["space_after"]))

            for child in element:
                if child.tag == 'run':
                    run = p.add_run()
                    text_content = child.find('text').text if child.find('text') is not None else ""
                    run.text = text_content
                    _apply_run_properties(run, child.attrib)
                elif child.tag == 'hyperlink':
                    url = child.get('url')
                    runs_data = []
                    for run_element in child.findall('run'):
                        text_content = run_element.find('text').text if run_element.find('text') is not None else ""
                        runs_data.append({'attrs': run_element.attrib, 'text': text_content})
                    if url and runs_data: _add_hyperlink(p, url, runs_data)
                elif child.tag == 'image':
                    original_r_id = child.get('r_id')
                    drawing_xml_str = child.get('drawing_xml')
                    if original_r_id in images_data and drawing_xml_str:
                        image_info = images_data[original_r_id]
                        image_stream = BytesIO(image_info['bytes'])
                        try:
                            # Parse the drawing XML to get dimensions
                            drawing_element = etree.fromstring(drawing_xml_str)
                            extent = drawing_element.find('.//wp:extent', namespaces=ns)
                            width = Emu(int(extent.get('cx')))
                            height = Emu(int(extent.get('cy')))
                            
                            run = p.add_run()
                            run.add_picture(image_stream, width=width, height=height)
                        except (etree.XMLSyntaxError, AttributeError, ValueError, KeyError):
                            pass # Failsafe
    return doc
