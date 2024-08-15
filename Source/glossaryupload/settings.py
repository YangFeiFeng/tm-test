import os

LOG_PATH = os.path.join(os.getcwd(), 'logs')
refresh_glossary_url = 'xxx'
get_product_smartlocalizer = 'xxx'
get_project = 'xxx'
google_project_id = 'xxx'
google_project_number = 'xxx'
google_bucket_id = 'xxx'
apple_product = ['aaa.resx', 'bbb.resx', 'ccc.resx', 'ddd.resx']
apple_termfile = ['aaa_apple.resx']
commonlist = ['aaa.resx'] #Same term in later file will overwrite translation in former file

languagelist_all = ['zh-TW',
                    'zh-CN',
                    'ja-JP',
                    'de-DE',
                    'fr-FR',
                    'es-ES',
                    'it-IT',
                    'pl-PL',
                    'ru-RU',
                    'id-ID',
                    'vi-VN',
                    'th-TH',
                    'ar-SA',
                    'da-DK',
                    'el-GR',
                    'ko-KR',
                    'pt-BR',
                    'tr-TR',
                    'nl-NL',
                    'nb-NO',
                    'sv-SE',
                    'cs-CZ',
                     'hu-HU',
                     'pt-PT',
                    'sq-AL',
                    'ro-RO']
languagemap = {'zh-CN': '2', 'zh-TW': '3', 'ja-JP': '4', 'de-DE': '5', 'fr-FR': '6', 'es-ES': '7', 'it-IT': '8', 'pl-PL': '9', 'ru-RU': '10', 'id-ID': '11', 'vi-VN': '12',
               'th-TH': '13', 'ar-SA': '14', 'da-DK': '15', 'el-GR': '16', 'he-HE': '17', 'ko-KR': '18', 'pt-BR': '19', 'tr-TR': '20',
               'nl-NL': '21', 'fr-CA': '22', 'no-NO': '23', 'nb-NO': '23', 'sv-SV': '24', 'sv-SE': '24', 'cs-CZ': '25', 'es-MX': '26', 'pt-PT': '27', 'fi-FI': '28', 'ca-ES': '29', 'sl-SL': '30', 'is-IS': '31',
               'bg-BG': '32', 'sr-Cyrl': '33', 'sr-Latn': '34', 'zh-HK': '35', 'en-AU': '36', 'zh-AS': '39', 'hu-HU': '40','sq-AL':'44', 'ro-RO':'45'}

import requests
import json
# generate glossary for all products on smartlocalizer except the ones in below exclude list:
exclude_product_list = ['test1', 'test2']
# get the products need to generate glossary
response = requests.get(get_product_smartlocalizer)
text = json.loads(response.text)
list = []
for item in text:
    list.append(item['name'])
productlist = [product + '.resx' for product in list if product not in exclude_product_list]
productlist = [product for product in productlist if product not in apple_product]
print(productlist)
# Term file upload to TM/delete from TM API
TMdeleteURL = 'xxx'
smartUploadURL = 'xxx'

