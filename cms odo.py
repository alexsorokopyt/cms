import getpass
import datetime
import imp
import logging
import os
import traceback
from unicodedata import numeric
import zipfile
from io import BytesIO

import odo
from odo import discover


# There are problem with pandas.py file inside odo package. 
# So in Ubuntu you need to go to Computer/usr/local/lib/python3.8/dist-packages/odo/backends/ and open pandas.py. 
# Than in line 94, change
# pd.tslib.NaTType
# to
# type(pd.NaT)

# pip install 'sqlalchemy=1.3'

# disable 'secure-file-priv' in MySQL 
# C:\ProgramData\MySQL\MySQL Server 8.0\my.ini
# then Windows + R >> services.msc >> MySQL >> Start\Restart

import openpyxl
import pandas as pd
import requests
from sqlalchemy import create_engine, exc, inspect
from numpy import nan
from plyer import notification


def downloadArchive(URL):
    '''
        Downloads archive from passed URL
        and extracts all its contents to download folder (specified in Parameters file)
    '''
    logging.info('Downloading started')
    filename = URL.split('/')[-1]
    req = requests.get(URL)
    logging.info(f'{filename} has been downloaded successfully')

    archive = zipfile.ZipFile(BytesIO(req.content))
    archive.extractall(result_directory)
    logging.info(f'All files from {filename} have been extracted to {DOWNLOAD_FOLDER}')


def getDataFromTable(wb, sheetName, tableName):
    '''
        Finds specified table in passed workbook
        and creates a dataframe from it
    '''
    ws = wb[sheetName]
    table = ws.tables[tableName]
    
    data = ws[table.ref]
    rows_list = []

    for row in data:
        cols = []
        for col in row:
            cols.append(col.value)
        rows_list.append(cols)

    return pd.DataFrame(data=rows_list[1:], index=None, columns=rows_list[0])


def getParameterValue(df, paramName):
    '''
        Filters Parameter table (as a dataframe) to find the value of a specific parameter
    '''
    return (df[df['Parameter'] == paramName].reset_index())['Value'][0]


current_filename = os.path.basename(__file__).rsplit('.', 1)[0]
log_file_name = current_filename + datetime.datetime.now().strftime(" %m.%d.%Y %H.%M.%S") + '.log'
logging.basicConfig(filename = log_file_name, level = logging.INFO, format = '%(asctime)s:%(levelname)s:%(message)s')

PARAMETERS_PATH = 'C:\\Users\\user\\Documents\\cms\\Parameters.xlsx'
ALPHA_TABLE = 'rpt_alpha'
RPT_TABLE = 'rpt'
NMRC_TABLE = 'rpt_nmrc'

wb = openpyxl.load_workbook(PARAMETERS_PATH)

parameters = getDataFromTable(wb, 'Parameters', 'Parameters')

HOST = getParameterValue(parameters, 'Host')
DB = getParameterValue(parameters, 'Database')
DOWNLOAD_FOLDER = getParameterValue(parameters, 'Download folder')
DOWNLOAD_FOLDER_TYPE = getParameterValue(parameters, 'Download folder path type')
SHOULD_CLEAR = getParameterValue(parameters, 'Clear download folder')
TABLES_BEHAVIOUR = getParameterValue(parameters, 'If tables exist')
DEFAULT_NUMERIC_FORMAT = getParameterValue(parameters, 'Default number format')
DEFAULT_DATE_FORMAT = getParameterValue(parameters, 'Default date format')

URLs = getDataFromTable(wb, 'Parameters', 'URLs')['URL']
mappings = getDataFromTable(wb, 'Parameters', 'Mappings')
mappings_tables = list(mappings['DB table'])
mappings_parts = list(mappings['Part of file name'])
mappings_defHeaders = list(mappings['Default headers'])
mappings_headers_settings = list(mappings['DB columns'])

wb.close()

logging.info(f'''
PASSED PARAMETERS:

Host: {HOST}
DB: {DB}
Downloads folder: {DOWNLOAD_FOLDER}
Clear download folder: {SHOULD_CLEAR}
Behaviour if tables exist: {TABLES_BEHAVIOUR}

URLS: 
{URLs}

MAPPINGS: 
{mappings}''')

current_directory = os.getcwd()
logging.info('Current working directory: ' + current_directory)

result_directory = ( current_directory + '\\' if DOWNLOAD_FOLDER_TYPE == 'relative' else '' ) + DOWNLOAD_FOLDER

# if SHOULD_CLEAR == 'yes':
#     if os.path.exists(result_directory):
#         for file in os.listdir(result_directory):
#             os.remove(result_directory + '\\' + file)
#             logging.info('File has been removed: ' + file)

#         os.rmdir(result_directory)
#         logging.info('Downloads folder has been removed')
#     else:
#         logging.info('Downloads folder doesn\'t exist')

# for url in URLs:
#     downloadArchive(url)

try:
    notification.notify(
        title = 'Credentials',
        message = 'Enter your credentials',
        app_icon = None,
        timeout = 10
    )

    DB_USER = 'admin' #input('Enter database username: ')
    DB_PASSWORD = 'admin' #getpass.getpass('Enter database password: ')

    db_engine = create_engine(f'mysql://{DB_USER}:{DB_PASSWORD}@{HOST}/{DB}')

    for file in os.listdir(DOWNLOAD_FOLDER):
        ds = odo.dshape("var * {RPT_REC_NUM: int64, WKSHT_CD: string, LINE_NUM: string, CLMN_NUM: string, ALPHNMRC_ITM_TXT: string}")
        csv_uri = f'{DOWNLOAD_FOLDER}/{os.path.splitext(file)[0] + os.path.splitext(file)[1].lower()}'
        mysql_uri = f'mysql://{DB_USER}:{DB_PASSWORD}@{HOST}/{DB}::rpt_alpha'
        odo.odo(csv_uri, mysql_uri, dshape=ds, escapechar='')
        print(file)


    # with db_engine.connect() as connection:
    #     logging.info('MySQL engine has been successfully created')

    #     if TABLES_BEHAVIOUR == 'replace':
    #         # Getting all schema tables names
    #         inspector = inspect(db_engine)
    #         table_names = inspector.get_table_names()

    #         trans = connection.begin()
    #         connection.execute('SET FOREIGN_KEY_CHECKS = 0;')
    #         for table in table_names:
    #             # Sequentially truncate each existing table
    #             connection.execute(f'TRUNCATE {table}')
    #             logging.info(f'Table {table} has been truncated')
    #         connection.execute('SET FOREIGN_KEY_CHECKS = 1;')
    #         trans.commit()

    #     # Iterrating over all files in Downloads folder
    #     for file in os.listdir(result_directory):
    #         logging.info('Started loading data from file ' + result_directory + '\\' + file)

    #         notification.notify(
    #             title = 'Loading data to DB',
    #             message = f'Started loading {file}',
    #             app_icon = None,
    #             timeout = 10
    #         )

    #         # Gettings current file extension
    #         file_extension = os.path.splitext(file)[-1]
            
    #         if file_extension.lower() != '.csv':
    #             logging.error(f'Unsupported file extension: {file}')
    #         else:
    #             # Iterrating over mappings table
    #             for index, path_part in enumerate(mappings_parts):
    #                 # If part of file name was found in current file name
    #                 # Then get 'table name' and 'headers' properties
    #                 if path_part.lower() in file.lower():

    #                     defHeaders = mappings_defHeaders[index]
    #                     headerSettings = mappings_headers_settings[index]
    #                     table_name = mappings_tables[index]

    #                     # If there are no headers in the file and no headers in the Parameters file, then skip this file
    #                     if defHeaders == 'no':
    #                         if headerSettings == None:
    #                             logging.critical(f'No specified headers for file {file}')
    #                             break
    #                         else:
    #                             headerSettings = mappings_headers_settings[index].split(';')
    #                             headerSettings = list(map(lambda x: x.split(':'), headerSettings))
    #                             header_names = list(map(lambda x: x[0], headerSettings))
    #                             df = pd.read_csv(result_directory + '\\' + file, 
    #                                             names=header_names)
    #                             for colSettings in headerSettings:
    #                                 if len(colSettings) > 1:
    #                                     colName = colSettings[0]
    #                                     if colSettings[1] == 'numeric':
    #                                         df[colName] = pd.to_numeric(df[colName], downcast=DEFAULT_NUMERIC_FORMAT)
    #                                     elif colSettings[1] == 'datetime':
    #                                         df[colName] = pd.to_datetime(df[colName], format=DEFAULT_DATE_FORMAT)
    #                     else:
    #                         header = [0]
    #                         df = pd.read_csv(result_directory + '\\' + file, 
    #                                         header=header)

    #                     df.fillna(value=nan)

    #                     # 'append' creates table if it doesn't exist
    #                     df.to_sql(con=db_engine, 
    #                               schema=DB, 
    #                               name=table_name, 
    #                               if_exists='append', 
    #                               index=False,
    #                               chunksize=1000)

    #                     logging.critical(f'{len(df.index)} new rows were successfully loaded to table {table_name} from {file}')
    #                     break

    #     connection.close()

except exc.SQLAlchemyError as e:
    logging.error(e)
    notification.notify(
        title = 'Error occurred',
        message = f'Check current log file: {log_file_name}',
        app_icon = None,
        timeout = 10
    )
except Exception as e:
    logging.error(traceback.format_exc())
    notification.notify(
        title = 'Error occurred',
        message = f'Check current log file: {log_file_name}',
        app_icon = None,
        timeout = 10
    )
finally:
    if 'db_engine' in globals():
        db_engine.dispose()
        logging.info(f'MySQL engine has been disposed')