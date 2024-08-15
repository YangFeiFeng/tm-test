import sys
import os
import logging
from xml.etree.ElementTree import _escape_cdata
import xlwt
import xml.etree.ElementTree as ET
import requests
import settings
sys.path.append("..")
from utils.osutil import remove_file_or_folder

currentpath = ""
languagelist = []
languagelist_all = settings.languagelist_all
LOG_FILE = 'term_export.log'
handler = logging.FileHandler(LOG_FILE, 'a', encoding='utf-8')
fmt = '%(levelname)s:%(asctime)s:%(message)s'
formatter = logging.Formatter(fmt)
handler.setFormatter(formatter)
logger = logging.getLogger('term_export')
logger.addHandler(handler)
logger.setLevel(logging.INFO)

localpath = os.path.join(os.getcwd(), settings.localpath)
workstringpath = os.path.join(os.path.abspath(os.path.join(os.getcwd(), "../..")), settings.termfilepath)


class GetPrepare():
    def __init__(self, repo, mainlocalpath):
        self.repo = repo
        self.mainlocalpath = mainlocalpath

    def removetempfolder(self):
        path_temp = os.path.join(currentpath, 'output')
        if (os.path.exists(path_temp)):
            remove_file_or_folder(path_temp)

    def getproductnames(self):
        url = settings.get_product_smartlocalizer
        response = requests.get(url).json()
        list = []
        for item in response:
            list.append(item['name'])
        return list


def CDATA(text=None):
    element = ET.Element('![CDATA[')
    element.text = text
    return element


ET._original_serialize_xml = ET._serialize_xml


def _serialize_xml(write, elem, qnames, namespaces, short_empty_elements, **kwargs):
    if elem.tag == '![CDATA[':
        write("<{}{}]]>".format(elem.tag, elem.text))
        if elem.tail:
            write(_escape_cdata(elem.tail))
    else:
        return ET._original_serialize_xml(write, elem, qnames, namespaces, short_empty_elements, **kwargs)


ET._serialize_xml = ET._serialize['xml'] = _serialize_xml


def cur_path_dir():
    global currentpath
    if getattr(sys, 'frozen', False):
        currentpath = os.path.dirname(sys.executable)
    elif __file__:
        currentpath = os.path.dirname(__file__)


def writeexcelgit(workstringpath, filenamelist, excelpath):
    print("write excel")
    excelfile = xlwt.Workbook()
    sheet1 = excelfile.add_sheet('sheet1', cell_overwrite_ok=True)
    rowIndex = 0

    # 设置表头样式
    header_style = xlwt.XFStyle()
    font = xlwt.Font()
    font.bold = True
    header_style.font = font

    # 写入表头
    headers = ['en-US', 'Translation', 'Language', 'From File', 'Comments', 'Products']
    for colIndex, header in enumerate(headers):
        sheet1.write(rowIndex, colIndex, header, header_style)

    rowIndex += 1  # 移动到下一行

    enstringlist = []
    written_data = {}  # 用于跟踪已经写入的语言和字符串

    for language_t in languagelist_all:
        if language_t == 'en-US':
            continue
        for filename_t in filenamelist:
            filepath_t = os.path.join(workstringpath, language_t, filename_t)
            if not os.path.isfile(filepath_t):
                logger.info("Not found file: %s" % filepath_t)
                continue

            with open(filepath_t, encoding='utf-8') as f_temp:
                try:
                    json_temp = ET.parse(f_temp)
                    root_temp = json_temp.getroot()
                except ET.ParseError as e:
                    logger.error("Error parsing file %s: %s" % (filepath_t, str(e)))
                    continue

                if os.path.getsize(filepath_t) == 0:
                    logger.info("File content none: %s" % filepath_t)
                    continue

                for child in root_temp:
                    en_context = child.get('name')
                    enstring = en_context.replace('&amp;', '&')
                    translation = child.find('value').text if child.find('value') is not None else ''
                    comments = child.find('comment').text if child.find('comment') is not None else ''
                    products = child.find('products').text if child.find('products') is not None else ''

                    key = (enstring, language_t)
                    if key in written_data:
                        i = written_data[key]
                    else:
                        i = rowIndex
                        rowIndex += 1
                        enstringlist.append(enstring)
                        written_data[key] = i

                    sheet1.write(i, 0, enstring)
                    sheet1.write(i, 1, translation)
                    sheet1.write(i, 2, language_t)
                    sheet1.write(i, 3, filename_t)
                    sheet1.write(i, 4, comments)
                    sheet1.write(i, 5, products)

    excelfile.save(excelpath)
    return


def writetbxgit(workstringpath, filenamelist, tbxfilepath):
    print("write tbx")
    datalist_temp = []
    rowtemp = []

    rowtemp.append("en-US")
    for language_t in languagelist_all:
        rowtemp.append(language_t)
    datalist_temp.append(rowtemp)

    enstringlist = []
    # filenamelist.reverse()  # 指定的文件名称
    for j in range(0, len(languagelist_all)):
        language_t = languagelist_all[j]
        for filename_t in filenamelist:
            filepath_t = os.path.join(workstringpath, language_t, filename_t)

            if os.path.isfile(filepath_t) == False:
                logger.info("Not found file: %s" % filepath_t)
                continue

            f_temp = open(filepath_t, encoding='utf-8')
            json_temp = ET.parse(f_temp)
            root = json_temp.getroot()
            '''if os.path.getsize(json_temp) == 0:
                logger.info("File content none: %s" % filepath_t)
                continue'''
            for child in root:
                rowtemp = []
                en_context = child.get('name')
                enstring = en_context.replace('&amp;', '&')
                translation = child.find('value').text

                if enstring in enstringlist:
                    i = enstringlist.index(enstring)
                    datalist_temp[i + 1][j + 1] = translation
                else:
                    rowtemp.append(enstring)
                    for language_t in languagelist_all:
                        rowtemp.append('')
                    rowtemp[j + 1] = translation
                    datalist_temp.append(rowtemp)

                    enstringlist.append(enstring)
            f_temp.close()
    generatetbx(datalist_temp, tbxfilepath)
    return


def generatetbx(datalist_temp, tbxfilepath):
    termnumber = 0
    trannumber = 0

    fp = open(tbxfilepath, 'w', encoding='utf-8')
    fp.write("<?xml version='1.0' encoding='utf-8'?>\n<body>\n")

    for rownum in range(1, len(datalist_temp)):
        termnumber += 1
        fp.write("    <termEntry id=\"cid-%d\">\n" % termnumber)

        rowtemp = datalist_temp[rownum]
        for colnum in range(0, len(languagelist_all)):
            celltemp = rowtemp[colnum]

            if (celltemp == "" or celltemp == None):
                continue

            fp.write("        <langSet xml:lang=\"%s\">\n" % datalist_temp[0][colnum])
            trannumber += 1
            fp.write("            <tig id=\"tid-%d\">\n" % trannumber)
            fp.write("                <term>%s</term>\n" % celltemp)
            fp.write("                <termNote type=\"partOfSpeech\">Noun</termNote>\n")
            fp.write("                <termNote type=\"processStatus\">finalized</termNote>\n")
            fp.write("                <termNote type=\"administrativeStatus\">preferredTerm-admn-sts</termNote>\n")
            fp.write("            </tig>\n")
            fp.write("        </langSet>\n\n")

        fp.write("    </termEntry>\n")

    fp.write("</body>\n")
    fp.close()

    return


def termgetmain():
    list = prepare.getproductnames()
    list.append('common')

    print('argv: %s' % sys.argv)
    print(len(sys.argv))
    
    get_productname, get_common_file, get_apple_file, get_excel = sys.argv[1:]
    print('get_productname is: %s, get_common_file is %s, get_apple_file is %s, get_excel is: %s'
          % (get_productname, get_common_file, get_apple_file, get_excel))

    get_product_file = get_productname + '.resx'
    if get_productname not in list:
        logger.error("Product Name not exist in SmartLocalizer")
        return

    termexportpath = os.path.join(currentpath, 'output')
    os.makedirs(termexportpath)
    excelpath = os.path.join(termexportpath, 'termforuse_%s.xls' % get_productname)
    tbxpath = os.path.join(termexportpath, 'termforuse_%s.tbx' % get_productname)
    filenamelist = get_common_file.split(',')
    if get_apple_file == 'true':
        print('Include ios/macos terms')
        filenamelist.append('common_apple.resx')
    if get_productname != 'common':
        filenamelist.append(get_product_file)
    if get_excel == 'TBX':
        writetbxgit(workstringpath, filenamelist, tbxpath)
    else:
        writeexcelgit(workstringpath, filenamelist, excelpath)
    print("Get Finished.")
    logger.info("End Success.")


if __name__ == "__main__":
    cur_path_dir()
    repo = 'git@adc.github.trendmicro.com:Corp-L10N/TE-Tools-Terminology.git'
    print('currentpath: %s' % currentpath)
    mainlocalpath = os.path.join(os.getcwd(), settings.mainlocalpath)
    print('localpath: %s' % mainlocalpath)
    prepare = GetPrepare(repo, mainlocalpath)
    prepare.removetempfolder()
    termgetmain()
