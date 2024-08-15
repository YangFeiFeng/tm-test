import sys
sys.path.append("..")
from utils.logutil import logger
from utils.osutil import remove_file_or_folder
from utils.csvutil import getdatafromfilelist, writecsv, getdatafromfile
from utils.tmxutil import get_signlelange_trans_fromlist

import os


class GenerateCSV:

    def __init__(self, tm_path, csv_path='', tmx_path='', languagelist_all=[]):
        self.tm_path = tm_path
        self.csv_path = csv_path
        self.tmx_path = tmx_path
        self.languagelist_all = languagelist_all

        remove_file_or_folder(self.csv_path)
        remove_file_or_folder(self.tmx_path)

        if self.csv_path:
            os.makedirs(self.csv_path)
        if self.tmx_path:
            os.makedirs(self.tmx_path)

    def generate_common_data(self, common_list):
        logger.info('Start to write common.resx.csv...')
        datalist = getdatafromfilelist(self.tm_path, common_list, self.languagelist_all)
        return datalist

    def generate_common_csv(self, common_list: list):
        data_list = self.generate_common_data(common_list)
        logger.debug('Start to write common.csv file')
        writecsv(data_list, self.csv_path, '%s.csv' % common_list[0])
        logger.info('finished write file: common.resx.csv')

    def generate_common_tmx(self, common_list: list):
        logger.info('Start to write common.tmx file')
        data_list = self.generate_common_data(common_list)
        productpath = os.path.join(self.tmx_path, 'common')
        os.makedirs(productpath)
        get_signlelange_trans_fromlist(data_list, 'common', productpath)
        logger.debug('Finished to write common.tmx file')


    def generate_apple_data(self, data_list: list, apple_file: list):
        data_list_apple = data_list.copy()
        logger.info('Start to get apple datalist...')
        for file in apple_file:
            data_list_apple = getdatafromfile(self.tm_path, file, data_list_apple, self.languagelist_all)
        logger.info('Finished to get apple datalist.')
        return data_list_apple

    def generate_product_data(self, data_list: list, product_list: list, is_apple: bool):
        product_type = 'apple product' if is_apple else 'product'
        self.process_products(data_list, product_list, is_apple, product_type, self.generate_product_csv)
        self.process_products(data_list, product_list, is_apple, product_type, self.generate_product_tmx)

    def process_products(self, data_list: list, product_list: list, is_apple: bool, product_type: str,
                         process_function):
        if product_list:
            for product in product_list:
                datalist_product = getdatafromfile(self.tm_path, product, data_list, self.languagelist_all)
                if not is_apple and not datalist_product:
                    logger.warning(f'{product} is not exist on String Portal.')
                    continue
                logger.info(f'Start to write {product_type} file: {product}')
                process_function(datalist_product, product, is_apple, product_type)
                logger.info(f'Finished to write {product_type} file: {product}')
        else:
            logger.warning(f'{product_type} list is not specified in settings file')

    def generate_product_csv(self, data_list: list, product_list: list, is_apple: bool, product_type: str):
        self.process_products(data_list, product_list, is_apple, product_type, self._write_csv)

    def _write_csv(self, datalist_product: list, product: str, is_apple: bool, product_type: str):
        writecsv(datalist_product, self.csv_path, f'{product}.csv')

    def generate_product_tmx(self, data_list: list, product_list: list, is_apple: bool, product_type: str):
        self.process_products(data_list, product_list, is_apple, product_type, self._write_tmx)

    def _write_tmx(self, datalist_product: list, product: str, is_apple: bool, product_type: str):
        product_name = product.replace('.resx', '')
        product_path = os.path.join(self.tmx_path, product_name)
        try:
            os.makedirs(product_path, exist_ok=True)
        except OSError as e:
            logger.error(f"Error creating directory {product_path}: {e}")
            return
        get_signlelange_trans_fromlist(datalist_product, product_name, product_path)

