from django.shortcuts import render
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from deep_translator import GoogleTranslator
from nltk.tokenize import sent_tokenize
import os
from fpdf import FPDF
from PIL import Image
import fitz  # PyMuPDF
import fpdf
def index(request):
    output_path = ''
    if request.method == 'POST' and 'input' in request.FILES:
        input_pdf_file = request.FILES['input']
        target_language = request.POST.get('lang', '')
        
        # Validate file extension, size, or other criteria here if needed
        
        # Save the uploaded file temporarily
        fs = FileSystemStorage()
        input_pdf_path = fs.save(input_pdf_file.name, input_pdf_file)
        
        # Process the PDF
        try:
            translated_pdf_path = handle_pdf_translation(input_pdf_path, target_language)
            output_path = fs.url('static/translated_fpdf.pdf')
        except Exception as e:
            # Handle specific exceptions, log errors
            print(f"Error processing PDF: {e}")
            output_path = None
        
        return render(request, 'index.html', {'output_pdf': output_path})
    else:
        return render(request, 'index.html')

def handle_pdf_translation(input_pdf_path, target_language):
    # Example function to handle PDF translation
    extracted_text = extract_text_from_pdf(input_pdf_path)
    translated_text = translate_extracted(extracted_text, target_language=target_language)

    # Write translated text to PDF using FPDF
    translated_pdf_filename = 'translated_fpdf.pdf'
    translated_pdf_path = os.path.join(settings.BASE_DIR, translated_pdf_filename)
    pdf = FPDF()
    pdf.add_page()
    pdf.add_font("Arial1", "", os.path.join(settings.BASE_DIR, "timesnewarial.ttf"), uni=True)

    pdf.set_font("Arial1", size=12)

    # Manually split translated text into lines based on a maximum width
    max_width = 80  # Maximum width for text on a line
    lines = split_text_into_lines(translated_text, max_width)

    # Write lines to PDF
    for line in lines:
        pdf.multi_cell(0, 10, line)
    
    pdf.output(translated_pdf_path)
    
    return translated_pdf_filename

def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file using PyMuPDF."""
    text = ""
    doc = fitz.open(pdf_path)
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text += page.get_text()
    return text

def split_text_into_lines(text, max_width):
    """Split text into lines of maximum width."""
    words = text.split()
    lines = []
    current_line = words[0]
    
    for word in words[1:]:
        if len(current_line) + len(word) + 1 <= max_width:
            current_line += " " + word
        else:
            lines.append(current_line)
            current_line = word
    
    if current_line:
        lines.append(current_line)
    
    return lines

def translate_extracted(text, target_language):
    """Translate extracted text to the target language."""
    translate = GoogleTranslator(source='auto', target=target_language).translate
    sentences = sent_tokenize(text)  # Tokenize into sentences

    translated_text = ""
    chunk = ""
    for sentence in sentences:
        if len(chunk.encode('utf-8')) + len(sentence.encode('utf-8')) < 5000:
            chunk += " " + sentence
        else:
            translated_text += " " + translate(chunk.strip())
            chunk = sentence

    if chunk:
        translated_text += " " + translate(chunk.strip())

    return translated_text

