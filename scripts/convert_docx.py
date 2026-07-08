import zipfile
import xml.etree.ElementTree as ET
import os

def read_docx(file_path):
    try:
        with zipfile.ZipFile(file_path) as z:
            xml_content = z.read('word/document.xml')
            root = ET.fromstring(xml_content)
            
            # The namespace for Word XML elements
            ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
            
            # Find all paragraph elements and extract text from text runs
            paragraphs = []
            for paragraph in root.findall('.//w:p', ns):
                texts = []
                for run in paragraph.findall('.//w:t', ns):
                    if run.text:
                        texts.append(run.text)
                paragraphs.append("".join(texts))
            return "\n".join(paragraphs)
    except Exception as e:
        return f"Error reading docx: {e}"

# List of docx files
files = ["README.docx", "job_description.docx", "redrob_signals_doc.docx", "submission_spec.docx"]
base_path = r"c:\Users\Dell\Downloads\[PUB] India_runs_data_and_ai_challenge\[PUB] India_runs_data_and_ai_challenge\India_runs_data_and_ai_challenge"

for f in files:
    full_path = os.path.join(base_path, f)
    print("=" * 60)
    print(f"FILE: {f}")
    print("=" * 60)
    content = read_docx(full_path)
    # Write to a text file in the same directory for viewing
    txt_name = f.replace(".docx", ".txt")
    txt_path = os.path.join(base_path, txt_name)
    with open(txt_path, "w", encoding="utf-8") as out:
        out.write(content)
    print(f"Successfully converted and saved to {txt_name} ({len(content)} chars)")
