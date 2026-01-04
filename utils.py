import os, re
from vercel_app.settings import BASE_DIR

# import docx
# def doc_replace(doc, findText, replaceText):
#     for p in doc.paragraphs:
#         if findText in p.text:
#             inline = p.runs
#             for i in range(len(inline)):
#                 if findText in inline[i].text:
#                     text = inline[i].text.replace(
#                         findText, replaceText)
#                     inline[i].text = text

from datetime import datetime
# Filter by datetime gte lte
def get_queryset__datetime_filter(_self,_object,_field='thoi_gian'):
    try:
        start = _self.request.query_params.get('thoi_gian__gte')
        end = _self.request.query_params.get('thoi_gian__lte')
        if (start == None or start == '') and (end == None or end == ''):
            return _object
        if (start == None or start == ''):
            return _object.filter(**{_field+'__lte':end})
            # start = '0001-01-01'
        if (end == None or end == ''):
            return _object.filter(**{_field+'__gte':start})
            # end = datetime.now().date()
        return _object.filter(**{_field+'__gte':start,_field+'__lte':end})
    except:
        return _object

def text_to_mp3(text):
    import pyttsx3
    bot = pyttsx3.init()
    bot.setProperty('rate', 125)
    bot.setProperty('volume', 1.0)
    voices = bot.getProperty('voices')
    # print(voices)
    bot.setProperty('voice', voices[1].id)
    import time
    ts = time.time()
    filename = "static/audio/"+str(ts)+".mp3"
    bot.save_to_file(text, filename)
    bot.runAndWait()
    return filename

def speak(text):
    import pyttsx3
    bot = pyttsx3.init()
    bot.setProperty('rate', 125)
    bot.setProperty('volume', 1.0)
    voices = bot.getProperty('voices')
    bot.setProperty('voice', voices[4].id)
    print(voices)
    for voice in voices:
        print(voice)
    bot.say(text)
    bot.save_to_file(text, 'E:/test.mp3')
    bot.runAndWait()

def fdf2images(file, page=None):
    import pdf2image
    images = pdf2image.convert_from_path(
        file, dpi=200, first_page=page, last_page=page, poppler_path=r"D:\Server\PCCC\poppler\Library\bin")
    return images
def image2text(image):
    import pytesseract
    path_to_tesseract = r"D:\Server\PCCC\Tesseract-OCR\tesseract.exe"
    pytesseract.pytesseract.tesseract_cmd = path_to_tesseract
    return tieng_viet_loai_bo_ky_tu_dac_biet(pytesseract.image_to_string(image, 'vie', '--psm 6'))

def fdf_orc(file, page=None):
    import pdf2image
    import pytesseract
    path_to_tesseract = r"D:\Server\PCCC\Tesseract-OCR\tesseract.exe"
    pytesseract.pytesseract.tesseract_cmd = path_to_tesseract
    images = pdf2image.convert_from_path(
        file, dpi=200, first_page=page, last_page=page, poppler_path=r"D:\Server\PCCC\poppler\Library\bin")
    text = ''
    for image in images:
        text += pytesseract.image_to_string(image, 'vie', '--psm 6')
    return text
    # return text.strip()

def tieng_viet_loai_bo_ky_tu_dac_biet(text):
    result = ''
    for char in text:
        if re.search('^[\n\s\t /()?.,\-\; 0-9A-ZÀÁẢÃẠĂẰẮẲẴẶÂẦẤẨẪẬĐÐÊỀẾỂỄỆÈÉẺẼẸÒÓỎÕỌÔỒỐỔỖỘƠỜỚỞỠỢÙÚỦŨỤƯỪỨỬỮỰÌÍỈĨỊỲÝỶỸỴa-zàáảãạăằắẳẵặâầấẩẫậđðêềếểễệèéẻẽẹòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựìíỉĩịỳýỷỹỵ]',char):
            result += char
    return result

def tieng_viet_khong_dau(text):
    text = text.upper()
    text = re.sub('[ÀÁẢÃẠĂẰẮẲẴẶÂẦẤẨẪẬ]','A',text)
    text = re.sub('[ĐÐ]','D',text)
    text = re.sub('[ÊỀẾỂỄỆÈÉẺẼẸ]','E',text)
    text = re.sub('[ÒÓỎÕỌÔỒỐỔỖỘƠỜỚỞỠỢ]','O',text)
    text = re.sub('[ÙÚỦŨỤƯỪỨỬỮỰ]','U',text)
    text = re.sub('[ÌÍỈĨỊ]','I',text)
    text = re.sub('[ỲÝỶỸỴ]','Y',text)
    text = re.sub('[àáảãạăằắẳẵặâầấẩẫậ]','a',text)
    text = re.sub('[đð]','d',text)
    text = re.sub('[êềếểễệèéẻẽẹ]','e',text)
    text = re.sub('[òóỏõọôồốổỗộơờớởỡợ]','o',text)
    text = re.sub('[ùúủũụưừứửữự]','u',text)
    text = re.sub('[ìíỉĩị]','i',text)
    text = re.sub('[ỳýỷỹỵ]','y',text)
    return text

from threading import Thread
import re