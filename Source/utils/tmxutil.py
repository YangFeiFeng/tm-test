import os
import xml.etree.ElementTree as ET
import time
from .logutil import logger


def getdatabylang(filepath, filenamelist):
    data_temp = []

    enstringlist = []
    for file in filenamelist:
        filepath_t = os.path.join(filepath, file)
        if not os.path.isfile(filepath_t):
            continue
        f_temp = open(filepath_t, encoding='utf-8')
        xml_temp = ET.parse(f_temp)
        root = xml_temp.getroot()

        for child in root:
            rowtemp = ['']
            en_context = child.get('name')
            enstring = en_context.replace('&amp;', '&')
            translation = child.find('value').text

            if enstring in enstringlist:
                i = enstringlist.index(enstring)
                data_temp[i][1] = translation
            else:
                enstringlist.append(enstring)
                rowtemp = [enstring, translation]
                data_temp.append(rowtemp)
        f_temp.close()
    return data_temp


def getdatabylang(filepath, filenamelist):
    data_temp = []

    enstringlist = []
    for file in filenamelist:
        filepath_t = os.path.join(filepath, file)
        if not os.path.isfile(filepath_t):
            continue
        f_temp = open(filepath_t, encoding='utf-8')
        xml_temp = ET.parse(f_temp)
        root = xml_temp.getroot()

        for child in root:
            rowtemp = ['']
            en_context = child.get('name')
            enstring = en_context.replace('&amp;', '&')
            translation = child.find('value').text

            if enstring in enstringlist:
                i = enstringlist.index(enstring)
                data_temp[i][1] = translation
            else:
                enstringlist.append(enstring)
                rowtemp = [enstring, translation]
                data_temp.append(rowtemp)
        f_temp.close()
    return data_temp


def writetmx(language, datalist, filename, targetpath):
    root = ET.Element('tmx')
    header = ET.SubElement(root, 'header', {'srclang': 'en-US', 'creationdate': time.strftime('%Y%m%d%H%M%S')})
    body = ET.SubElement(root, 'body')
    for i in datalist:
        tu = ET.SubElement(body, 'tu')
        tuv = ET.SubElement(tu, 'tuv', {'xml:lang': 'EN-US'})
        seg_en = ET.SubElement(tuv, 'seg')
        seg_en.text = i[0]
        tuv_l10n = ET.SubElement(tu, 'tuv', {'xml:lang': language.upper()})
        seg_l10n = ET.SubElement(tuv_l10n, 'seg')
        seg_l10n.text = i[1]

    indent(root)
    path = os.path.join(targetpath, filename)
    tree = ET.ElementTree(root)
    tree.write(path, encoding='utf-8', xml_declaration=True)


def indent(elem, level=0):
    """美化写入文件的内容"""
    i = "\n" + level * "  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level + 1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i


def writetmxfiles(languagelist, filepath, commonfilelist, productfilelist, termfilepath, tmxpath, commonlist):
    for lang in languagelist:
        # generate common TM for each language
        data = getdatabylang(filepath, commonlist)
        writetmx(lang, data, 'common_' + lang + '.tmx', tmxpath)
        for prod in productfilelist:
            # generate product TM for each product
            prodterm = commonfilelist.copy()
            prodterm.append(prod)
            filepath = os.path.join(termfilepath, lang)
            proddata = getdatabylang(filepath, prodterm)
            writetmx(lang, proddata, prod.replace('.resx', '') + '_' + lang + '.tmx', tmxpath)


# 根据 生成csv文件过程中的datalist来针对每个语言生成列表
def get_signlelange_trans_fromlist(data, product, productpath):
    logger.info('start write tmx')
    for j in range(2, len(data[0])):
        list = []
        for i in range(1, len(data)):
            list_temp = []
            trans = data[i][j]

            if trans:
                list_temp.append(data[i][1])
                list_temp.append(trans)
                list.append(list_temp)

        filename = product + '_' + data[0][j] + '.tmx'
        targetpath = os.path.join(productpath, data[0][j])
        # shutil.rmtree(targetpath)
        if not os.path.isdir(targetpath):
            # print('mkdir language folder',data[0][j])
            os.mkdir(targetpath)
        writetmx(data[0][j], list, filename, targetpath)
        logger.info('write file: %s' % filename)
