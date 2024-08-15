import datetime

import settings
import zipfile
import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
import os
import json

class uploadtmx():

    def __init__(self, logger):
        self.logger = logger
        self.languagemap = settings.languagemap
        self.get_project = settings.get_project
        self.projects = self.get_projects()

    def get_projects(self):
        data = requests.get(self.get_project).json()[0]['projects']
        return data

    #获取到project id 列表
    def getprojectid(self, project_name=''):
        plist = self.projects
        projectmap = {}
        for item in plist:
            projectname = item['version']
            projectid = item['id']
            projectmap[projectname] = projectid
        if project_name:
            project_id = projectmap[project_name]
        else:
            project_id = ''
        return project_id, projectmap

    def preparedata(self, file, targetlanguage_id, project_id, token):

        data_upload = {
                    'name': file,
                    'description': 'Upload glossary TM',
                    'sourcelanguage_id': '1',
                    'targetlanguage_id': targetlanguage_id,
                    'type': 'UI',
                    'project_id': project_id,
                    'token': token}
        return data_upload

    def httprequest(self, smartUploadURL, data, upload_files=None):
        try:
            res = requests.post(smartUploadURL, data=data, files=upload_files)
            if res.json()["level"] != 'success':
                error_message = res.json()["message"]
                print('TM Portal Error: %s' % error_message)
                return False
            else:
                return True
        except Exception as e:
            print(e)
            return False

    def zipfiles(self, tmpath_temp, productList, languageList):
        self.logger.info(f"Start to zip files for product: {productList}, language: {languageList}...")
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        zipname = os.path.join(tmpath_temp, f"{timestamp}.zip")

        with zipfile.ZipFile(zipname, 'w', zipfile.ZIP_DEFLATED) as z:
            for product in productList:
                for language in languageList:
                    tmx_dir = os.path.join(tmpath_temp, product, language)
                    if os.path.exists(tmx_dir):
                        for root, dirs, files in os.walk(tmx_dir):
                            for file in files:
                                if file.endswith('.tmx'):
                                    file_path = os.path.join(root, file)
                                    arcname = os.path.relpath(file_path, start=tmpath_temp)
                                    z.write(file_path, arcname)

        self.logger.info(f"Finished zipping files for product: {product}, language: {language}")
        return zipname
    # upload files
    def tmx_upload(self, tmxpath, token, smartUploadURL, productList, languageList):
        # locker = threading.BoundedSemaphore(10)
        self.logger.info("Start to upload files...")
        for product in productList:
            try:
                projectid, projectlist = self.getprojectid(product) #get the product id
                self.logger.info(projectid)
            except Exception as e:
                print('get project id failed: %s' % product)
                continue
            productpath = os.path.join(tmxpath, product)
            for lang in languageList:
                langid = self.languagemap[lang]
                filepath = os.path.join(productpath, lang)
                filename = os.listdir(filepath)
                for file in filename:
                    if os.path.splitext(file)[-1] == '.tmx':
                        with open(os.path.join(filepath, file), 'rb') as f:
                            upload_files = {'tm_file': f}
                            data = self.preparedata(upload_files, langid, projectid, token)
                            self.logger.info("data: %s", data)
                            if not self.httprequest(smartUploadURL, data, upload_files):
                                self.logger.error('Failed to upload file: %s', file)
                            else:
                                self.logger.info('Successfully uploaded file: %s', file)

    #delete tmx file
    def deleteTM(self, TMdeleteURL, token, product, language):
        projectid, projectList = self.getprojectid()
        try:
            if not token:
                print("Failed to get token")
                return False
            deletemap = self.format_tm_delete_data(projectList, product, language)
            self.logger.info("deletemap is: {}".format(deletemap))
            data = {"params": json.dumps(deletemap), "token": token}
            s = requests.Session()
            s.mount('https://', HTTPAdapter(
                max_retries=Retry(total=10, backoff_factor=1, status_forcelist=[500, 502, 503, 504, 521])))
            res = s.post(TMdeleteURL, data=data)
            self.logger.info(res.text)
            if res.json()['level'] == 'success' and res.json()['data']['Delete error count'] == 0:
                return True
            return False
        except Exception as e:
            self.logger.error(str(e))
            print(str(e))
            return False

    def format_tm_delete_data(self, projectList, product, language):
        """
        This function is used to format the data for deleting TM files
        :param projectList: all project list, including project id and project name
        :param product: product name
        :param language:
        :return:
        """
        deletemap = {}
        for item in product:
            project_id = projectList[item]
            filelistmap = {}
            for lang in language:
                filelistmap[lang] = [item + '_' + lang + '.tmx']
        deletemap[project_id] = filelistmap
        return deletemap
