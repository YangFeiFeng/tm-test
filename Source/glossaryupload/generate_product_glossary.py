import os
import sys

import git
import requests
import xlrd
import xlwt
from git import Repo

import xml.etree.ElementTree as ET
from generatecsv import GenerateCSV
sys.path.append("..")
from utils.logutil import logger
from utils.osutil import remove_file_or_folder
from termmanage import settings

workstringpath = os.path.join(os.path.abspath(os.path.join(os.getcwd(), "../..")), settings.termfilepath)
product_glossary_path = os.path.join(os.path.abspath(os.path.join(os.getcwd(), "../..")), settings.product_glossary)


class GetPrepare():
    def __init__(self, repo, mainlocalpath):
        self.repo = repo
        self.mainlocalpath = mainlocalpath

    def getgitfile(self, branch):
        try:
            if self.mainlocalpath.is_dir():
                gitfile = Repo(self.mainlocalpath)
                remote = gitfile.remote()
                remote.pull(branch)
                logger.info("gittemp exist,pull: %s" % self.mainlocalpath)
                print("gittemp exist,pull: %s" % self.mainlocalpath)
            else:
                git.Repo.clone_from(self.repo, self.mainlocalpath)
                logger.info(f'gittemp not exist, git clone: {self.mainlocalpath}')
                print(f'gittemp not exist, git clone: {self.mainlocalpath}')
        except git.GitCommandError as e:
            print(f"Fail to download term files from git: {e}")
            exit(1)

    def removetempfolder(self):
        path_temp = os.path.join(currentpath, "tempforimport")
        if os.path.exists(path_temp):
            remove_file_or_folder(path_temp)

    def getproductnames(self):
        url = settings.get_product_smartlocalizer
        response = requests.get(url).json()
        list = []
        for item in response:
            list.append(item['name'])
        print(list)
        return list


def cur_path_dir():
    global currentpath

    if getattr(sys, 'frozen', False):
        currentpath = os.path.dirname(sys.executable)
    elif __file__:
        currentpath = os.path.dirname(__file__)

def optimizeexcel(excelpath):
    old_excel = xlrd.open_workbook(excelpath)
    table = old_excel.sheet_by_name(u'sheet1')
    nrows = table.nrows
    ncols = table.ncols

    datalist_t = []
    for colnum in range(0, ncols):
        col = table.col_values(colnum)  # col为整列的值
        flag = 0
        for i in range(1, len(col)):
            if col[i] != '':
                flag = 1
                break  # 一直循环到找到该列有内容的单元格为止，flag=1
        if flag == 0:  # flag表示该列为空列
            continue
        datalist_t.append(col)
    # 非空列的时候，整列赋值给datalist_t。 去除空语言列
    new_excel = xlwt.Workbook()
    sheet1 = new_excel.add_sheet('sheet1')

    for colIndex in range(0, len(datalist_t)):
        for rowIndex in range(0, len(datalist_t[colIndex])):
            sheet1.write(rowIndex, colIndex, datalist_t[colIndex][rowIndex]);
    new_excel.save(excelpath)
    return


def writeexcelgit(workstringpath, filenamelist, excelpath, languages):
    print("write excel")
    excelfile = xlwt.Workbook()
    sheet1 = excelfile.add_sheet('sheet1', cell_overwrite_ok=True)

    # 写入第一行的语言列
    sheet1.write(0, 0, 'en-US')
    for colIndex, language_t in enumerate(languages, start=1):
        sheet1.write(0, colIndex, language_t)

    # 初始化enstringlist和行索引
    enstringlist = []
    rowIndex = 0

    for j, language_t in enumerate(languages):
        for filename_t in filenamelist:
            filepath_t = os.path.join(workstringpath, language_t, filename_t)
            if not os.path.isfile(filepath_t):
                logger.info("Not found file: %s", filepath_t)
                continue

            if os.path.getsize(filepath_t) == 0:
                logger.info("File content none: %s", filepath_t)
                continue

            # 使用上下文管理器打开文件
            with open(filepath_t, encoding='utf-8') as f_temp:
                try:
                    json_temp = ET.parse(f_temp)
                    root_temp = json_temp.getroot()
                except ET.ParseError as e:
                    logger.error("Failed to parse XML file: %s, error: %s", filepath_t, e)
                    continue

                for child in root_temp:
                    en_context = child.get('name')
                    enstring = en_context.replace('&amp;', '&')
                    translation = child.find('value').text

                    if enstring in enstringlist:
                        i = enstringlist.index(enstring) + 1
                    else:
                        rowIndex += 1
                        i = rowIndex
                        enstringlist.append(enstring)

                    sheet1.write(i, 0, enstring)
                    sheet1.write(i, j + 1, translation)

    # 确保目录存在
    os.makedirs(os.path.dirname(excelpath), exist_ok=True)

    # 保存文件
    excelfile.save(excelpath)
    optimizeexcel(excelpath)
    return


def writetbxgit(workstringpath, filenamelist, tbxfilepath, languages):
    print("write tbx")
    datalist_temp = []
    rowtemp = []

    rowtemp.append("en-US")
    for language_t in languages:
        rowtemp.append(language_t)
    datalist_temp.append(rowtemp)

    enstringlist = []
    # filenamelist.reverse()  # 指定的文件名称
    for j in range(0, len(languages)):
        language_t = languages[j]
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
                    for language_t in languages:
                        rowtemp.append('')
                    rowtemp[j + 1] = translation
                    datalist_temp.append(rowtemp)

                    enstringlist.append(enstring)
            f_temp.close()
    generatetbx(datalist_temp, tbxfilepath, languages)
    return

def generatetbx(datalist_temp, tbxfilepath, languages):
    termnumber = 0
    trannumber = 0

    fp = open(tbxfilepath, 'w', encoding='utf-8')
    fp.write("<?xml version='1.0' encoding='utf-8'?>\n<body>\n")

    for rownum in range(1, len(datalist_temp)):
        termnumber += 1
        fp.write("    <termEntry id=\"cid-%d\">\n" % termnumber)

        rowtemp = datalist_temp[rownum]
        for colnum in range(0, len(languages)):
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

def commitgitfile2(repopath, branch, comment):
    repo = git.Git(repopath)
    repo.checkout(branch)
    repo.add('.')
    try:
        repo.commit('-m  %s' % comment)
    except Exception as e:
        print(e)
        exit(1)
    repo.push()
    logger.info("git files uploaded：%s " % repopath)
    print("git files uploaded：%s " % repopath)

def export_full_term(branch):
    print('Start to export full term...')
    list = prepare.getproductnames()
    list.append('common')
    glossary_path = os.path.join(os.path.abspath(os.path.join(os.getcwd(), "../..")), '05.ProductGlossary')
    if not os.path.exists(glossary_path):
        os.makedirs(glossary_path)
    tm_path = os.path.join(os.path.abspath(os.path.join(os.getcwd(), "../..")), '01.Terminology')
    #
    generate_csv = GenerateCSV(tm_path=tm_path, tmx_path=glossary_path, languagelist_all=settings.languagelist_all)

    # generate common data
    data_list = generate_csv.generate_common_data(settings.commonlist)

    # generate apple data
    data_list_apple = generate_csv.generate_apple_data(data_list, settings.apple_termfile)

    # generate common tmx
    generate_csv.generate_common_tmx(settings.commonlist)

    # generate apple tmx
    generate_csv.generate_product_tmx(data_list_apple, settings.apple_product, True, 'apple product')

    # generate none-apple tmx
    generate_csv.generate_product_tmx(data_list, settings.productlist, False, 'none-apple product')

    for product in list:
        product_path = os.path.join(glossary_path, product)
        if not os.path.exists(product_path):
            os.makedirs(product_path)
        glossary_xls_path = os.path.join(product_path, 'termforuse_%s.xls' % product)
        glossary_tbx_path = os.path.join(product_path, 'termforuse_%s.tbx' % product)
        filenamelist = settings.export_commonlist
        if product != 'common':
            filenamelist.append(product + '.resx')
        if product + '.resx' in settings.apple_product:
            filenamelist.extend(settings.apple_termfile)
        writeexcelgit(workstringpath, filenamelist, glossary_xls_path, settings.languagelist_all)
        writetbxgit(workstringpath, filenamelist, glossary_tbx_path, settings.languagelist_all)

    try:
        print('Start to commit glossary files...')
        commitgitfile2(product_glossary_path, branch, 'Update product glossary')
        print('Finished to commit glossary files...')
    except Exception as e:
        print(str(e))
        exit(1)
