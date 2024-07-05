from django.shortcuts import render
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from deep_translator import GoogleTranslator
from nltk.tokenize import sent_tokenize
import os
import pytube
import math
from decimal import Decimal, getcontext
getcontext().prec = 9999
import roman
from fpdf import FPDF
from PyPDF2 import PdfReader  # Import PdfReader instead of PdfFileReader
from pytube.innertube import _default_clients
from django.views.decorators.csrf import csrf_exempt
_default_clients["ANDROID_MUSIC"] = _default_clients["ANDROID_CREATOR"]
from math import factorial
def youtube(request):
    resolutions = ['360p', '720p', '1080p', '1440p', '2160p', 'mp3']
    title = ""
    streams = []
    streams3 = []
    error_message = ""
    resolution = []

    if request.method == 'POST':
        youtube_link = request.POST.get('youtube_link')
        resolution = request.POST.get('resolution')

        if youtube_link and resolution:
            try:
                yt = pytube.YouTube(youtube_link)
                title = yt.title

                if resolution == 'mp3':
                    streams3 = yt.streams.filter(only_audio=True)
                else:
                    streams = yt.streams.filter(res=resolution)
            except pytube.exceptions.VideoUnavailable as e:
                error_message = f"Error: Video is unavailable ({str(e)})"
            except Exception as e:
                error_message = f"Error: {str(e)}"
        else:
            error_message = "Please enter a YouTube link and select a resolution."

    context = {
        'title': title,
        'streams': streams,
        'streams3': streams3,
        'resolutions': resolutions,
        'selected_resolution': resolution,
        'error_message': error_message,
    }

    return render(request, 'youtube.html', context)

def calculate_result(expression):
    
    try:
        
        expression = expression
        result = Decimal(eval(expression))
        return str(result)
    except Exception as e:
        return "Error"
@csrf_exempt
def kalkulator(request):
    result = ""

    if request.method == 'POST':
        expression = request.POST.get('expression', '')
        result = calculate_result(expression)
        if 'log' in request.POST :
            try:
                angka = expression.split()
                a = int(angka[0])
                b = int(angka[1])
                if b == '':
                    
                    result = math.log(a)
                elif b == '10':
                    result = math.log10(a)
                else :
                    result = math.log(a, b)
            except ValueError:
                result = "Gunakan 2 angka dipisah spasi"
        if 'to_roman' in request.POST:
            try:
                result = roman.toRoman(int(expression))
            except ValueError or IndexError:
                result = "Invalid number must be 0 - 4999"
            except Exception:
                result = "Invalid number must be 0 - 4999"
        elif 'from_roman' in request.POST:
            roman_number = expression
            try:
                result = roman.fromRoman(roman_number)
            except roman.InvalidRomanNumeralError:
                result = "Invalid Roman numeral"
        elif 'sin' in request.POST:
            sin = expression
            try:
                result = math.sin(float(sin))
            except ValueError:
                result = "error"
        elif 'cos' in request.POST:
            cos = expression
            try:
                result = math.cos(float(cos))
            except ValueError:
                result = "error"
        elif 'tan' in request.POST:
            tan = expression
            try:
                result = math.tan(float(tan))
            except ValueError:
                result = "error"
        elif 'asin' in request.POST:
            asin = expression
            try:
                result = math.asin(float(asin))
            except ValueError:
                result = "error"
        elif 'acos' in request.POST:
            acos = expression
            try:
                result = math.acos(float(acos))
            except ValueError:
                result = "error"
        elif 'atan' in request.POST:
            atan = expression
            try:
                result = math.atan(float(atan))
            except ValueError:
                result = "error"
        elif 'factorial' in request.POST:
            fact = expression
            try:
                result = math.factorial(int(fact))
            except ValueError:
                result = "Dont use comma"
        elif 'c_to_f' in request.POST:
            celcius = float(expression)
            try:
                result = ((celcius * 9/5) + 32)
            except ValueError:
                result = "error"
        elif 'f_to_c' in request.POST:
            fahrenheit = float(expression)
            try:
                result = ((fahrenheit - 32) * 5/9)
            except ValueError:
                result = "error"
        elif 'c_to_k' in request.POST:
            celcius = expression
            try:
                result = (float(celcius) + 273.15)
            except ValueError:
                result = "error"
        elif 'k_to_c' in request.POST:
            kelvin = float(expression)
            try:
                result = (kelvin - 273.15)
            except ValueError:
                result = "error"
        elif 'c_to_r' in request.POST:
            celcius = float(expression)
            try:
                result = (celcius * 4/5)
            except ValueError:
                result = "error"
        elif 'r_to_c' in request.POST:
            reamur = float(expression)
            try:
                result = (reamur * 5/4)
            except ValueError:
                result = "error"
        elif 'r_to_c' in request.POST:
            reamur = float(expression)
            try:
                result = (float(reamur) * 5/4)
            except ValueError:
                result = "error"
        elif 'f_to_r' in request.POST:
            fahrenheit = float(expression)
            try:
                result = ((fahrenheit - 32) * 4/9)
            except ValueError:
                result = "error"
        elif 'f_to_k' in request.POST:
            fahrenheit = float(expression)
            try:
                result = ((fahrenheit + 459.67)* 5/9)
            except ValueError:
                result = "error"
        elif 'r_to_f' in request.POST:
            reamur = float(expression)
            try:
                result = ((reamur * 9/4) + 32)
            except ValueError:
                result = "error"
        elif 'r_to_k' in request.POST:
            reamur = float(expression)
            try:
                result = ((reamur * 5/4) + 273.15)
            except ValueError:
                result = "error"
        elif 'k_to_r' in request.POST:
            kelvin = float(expression)
            try:
                result = ((kelvin - 273.15) * 4/5)
            except ValueError:
                result = "error"
        elif 'k_to_f' in request.POST:
            kelvin = float(expression)
            try:
                result = ((kelvin * 9/5) - 459.67)
            except ValueError:
                result = "error"
        elif 'binary' in request.POST:
            n = int(expression)
            try:
                result = format(n ,"b")
            except ValueError:
                result = "Don't use comma"
        elif 'num' in request.POST:
            n = expression
            try:
                result = int(n, 2)
            except ValueError:
                result = "Not Binary"
                
        elif 'sqrt' in request.POST:
            n = int(expression)
            try:
                result = math.sqrt(n)
            except ValueError:
                result = "Invalid Number"

            
    return render(request, 'kalkulator.html', {'result': result})


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
    """Extract text from a PDF file using PyPDF2."""
    text = ""
    with open(pdf_path, 'rb') as f:
        pdf_reader = PdfReader(f)
        num_pages = len(pdf_reader.pages)
        for page_num in range(num_pages):
            page = pdf_reader.pages[page_num]
            text += page.extract_text()
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

