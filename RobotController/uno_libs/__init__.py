import sys

import logging

import mysql.connector
from mysql.connector import errorcode

from ..teks_libs.loghandlers import *
from ..tms.teks_db import teks_db_api, teks_db_configure

if (teks_db_configure.LOG_TO_DB):

    log_conn = mysql.connector.connect(**teks_db_configure.MYSQL_CONFIG)
    log_conn.start_transaction(isolation_level='READ COMMITTED')

    # Make the connection to database for the logger
    # log_conn = pymssql.connect(db_server, db_user, db_password, db_dbname, 30)
    # log_cursor = log_conn.cursor()
    log_cursor = log_conn.cursor(buffered=False)
    logdb = LogDBHandler(log_conn, log_cursor, teks_db_configure.DB_TBL_LOG)

# Set logger
# logging.basicConfig(filename=teks_db_configure.LOG_FILE_PATH)

# Set db handler for root logger
if (teks_db_configure.LOG_TO_DB):
    logging.getLogger(__name__).addHandler(logdb)
# Register MY_LOGGER
# logger = logging.getLogger('UNO_LOGGER')
logger = logging.getLogger(__name__)
logger.setLevel(teks_db_configure.LOG_ERROR_LEVEL)
