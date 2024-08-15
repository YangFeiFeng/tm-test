import csv
import os
import xml.etree.ElementTree as ET
import copy
from .logutil import logger

def writecsv(datalist, targetpath, filename):
    with open('{}/{}'.format(targetpath, filename), "w+", newline='', encoding='utf-8-sig') as c:
        writer = csv.writer(c)
        writer.writerows(datalist)
        c.close
    return


def getdatafromfilelist(filepath, filenamelist, languagelist_all):
    datalist_temp = []
    csv_title = ['', 'en-US'] + languagelist_all
    datalist_temp.append(csv_title)

    enstringlist = []
    for j in range(0, len(languagelist_all)):
        language_t = languagelist_all[j]
        for filename_t in filenamelist:
            filepath_t = os.path.join(filepath, language_t, filename_t)

            if os.path.isfile(filepath_t) == False:
                logger.warning("Not found file: %s" % filepath_t)
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
                    datalist_temp[i + 1][j + 2] = translation
                else:
                    rowtemp.append(enstring)
                    for language_t2 in languagelist_all:
                        rowtemp.append('')
                    rowtemp[j + 2] = translation
                    datalist_temp.append(rowtemp)
                    enstringlist.append(enstring)
            f_temp.close()
    return datalist_temp


def getdatafromfile(filepath, filename, commonlist, languagelist_all):
    datalist = copy.deepcopy(commonlist)
    for j in range(0, len(languagelist_all)):
        language_t = languagelist_all[j]
        filepath_t = os.path.join(filepath, language_t, filename)
        if os.path.isfile(filepath_t) == False:
            continue
        f_temp = open(filepath_t, encoding='utf-8')
        xml_temp = ET.parse(f_temp)
        root = xml_temp.getroot()

        for child in root:

            en_context = child.get('name')
            enstring = en_context.replace('&amp;', '&')
            translation = child.find('value').text

            flag = 0
            for i in range(1, len(datalist)):
                if enstring == datalist[i][1]:
                    datalist[i][j + 2] = translation
                    flag = 1
                    break
            if flag == 0:
                rowtemp = ['']
                rowtemp.append(enstring)
                for language_t2 in languagelist_all:
                    rowtemp.append('')
                rowtemp[j + 2] = translation
                datalist.append(rowtemp)

        f_temp.close()
    return datalist
