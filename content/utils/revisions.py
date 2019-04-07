"""
Functions related to revising course funding requests
"""
import json
from enum import Enum, auto
from .sql_connection import Transaction
from . import db_utils

def create_revision(username):
    """
    Create new revision of a CFR
    """

    current_cfr = db_utils.current_cfr(username)
    revision_num = current_cfr[5] + 1
    
    create_rev = ("INSERT INTO cfr_department "
                  "VALUES (%s, %s, YEAR(NOW()), %s, NOW(), %s, %s)")

    data_rev = (current_cfr[0], current_cfr[1], current_cfr[3], revision_num, username)

    with Transaction() as cursor:
        cursor.execute(create_rev, data_rev)
        rows_inserted = cursor.rowcount
    return rows_inserted

    

