import os.path

from uploadtmx import uploadtmx
import sys
sys.path.append("..")
from utils.logutil import Log

logger = Log.get_logger("TMPortalOperation")


class ToPortal:

    def __init__(self, tm_delete_url, smart_upload_url, tmx_path, token):
        self.tm_delete_url = tm_delete_url
        self.smart_upload_url = smart_upload_url
        self.tmx_path = tmx_path
        self.token = token

    def upload2portal(self, productList, languageList):
        """
        Upload TM files to TM Portal, delete existing TM files first, then upload new TM files one by one
        :param productList: product name
        :param language:
        :return:
        """
        print("Start to delete existing TM files from TM Portal")
        uptmx = uploadtmx(logger)

        if not uptmx.deleteTM(self.tm_delete_url, self.token, productList, languageList):
            print("Failed to delete TM files from TM portal")
            logger.info("Failed to delete TM files from TM portal")
            return False

        # upload TM files to TMPortal
        print("Start to upload TM files to TM portal")
        uptmx.tmx_upload(self.tmx_path, self.token, self.smart_upload_url, productList, languageList)
        return True
