from uploadtogoogle import upload
import sys
sys.path.append("..")
from utils.logutil import Log
from utils.glossaryutil import glossary
from google.api_core.exceptions import NotFound
import os

logger = Log.get_logger("GoogleOperation")


class ToGoogle:

    def __init__(self, project_id, bucket_id, csv_path, languagelist_all):
        self.project_id = project_id
        self.bucket_id = bucket_id
        self.csv_path = csv_path
        self.languagelist_all = languagelist_all

    def handle_uploadfail(self, upload_fail_list: list, glosary_list: list, notdelete_glossary: list, glossary_dict: dict):
        if upload_fail_list:
            for file in upload_fail_list:
                f_id = file.replace('.resx.csv', '')
                g_id = f_id.replace(' ', '').replace('.', '').replace('&', '') + "_terminology"
                notdelete_glossary.append(g_id)
                if g_id not in glosary_list:  # 这个上传失败的文件以前没有create过glossary
                    del glossary_dict[f_id]

    def handle_uploadsuccess(self, upload_success_list: list):
        if upload_success_list:
            # delete existing glossary
            gl = glossary(logger, self.languagelist_all)
            for file in upload_success_list:
                f_id = file.replace('.resx.csv', '')
                glossary_id = f_id.replace(' ', '').replace('.', '') + "_terminology"
                try:
                    gl.delete_glossary(self.project_id, glossary_id)
                except NotFound:
                    print('Glossary not found: %s' % glossary_id)
                    logger.warning('Glossary not found: %s' % glossary_id)
                except Exception as e:
                    print('Failed to delete glossary: %s' % glossary_id)
                    print(e)
                    logger.warning(e)
                    continue

                input_uri = f"gs://{self.bucket_id}/{file}"
                gl.create_glossary(self.project_id, input_uri, glossary_id, timeout=180)

    def upload2google(self, productList, languageList):
        logger.info('Start to upload CSV file to Google...')
        res = True
        up = upload(logger)
        upload_fail_list = []
        upload_success_list = []
        glossary_dict = {}
        for product in productList:
            file_path = os.path.join(self.csv_path, product + '.resx.csv')
            if os.path.exists(file_path):
                file = product + '.resx.csv'
                f_id = file.replace('.resx.csv', '')
                g_id = f_id.replace(' ', '').replace('.', '') + '_terminology'
                glossary_dict.update({f_id: g_id})
                source_file_name = os.path.join(self.csv_path, file)
                destination_blob_name = file
                try:
                    up.upload_blob(self.bucket_id, source_file_name, destination_blob_name)
                except Exception as e:
                    logger.error('Failed to upload file {} to google'.format(file))
                    logger.error(e)
                    upload_fail_list.append(file)
                    res = False
                    continue
                else:
                    logger.info('Upload to google success: {}'.format(file))
                    upload_success_list.append(file)

        gl = glossary(logger, self.languagelist_all)
        glosary_list = gl.list_glossaries(self.project_id)
        notdelete_glossary = []

        self.handle_uploadfail(upload_fail_list, glosary_list, notdelete_glossary, glossary_dict)
        self.handle_uploadsuccess(upload_success_list)
        logger.info('Finished upload CSV file to Google...')
        return res
