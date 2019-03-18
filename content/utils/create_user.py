"""
Functions related to creating a new user
"""
from . import sql_connection as sql


def create_user(username, usr_password, banner_id, usr_role):
    """
    Insert a new user into the user table
    """
    cursor = sql.new_cursor()
    add_user = ("INSERT INTO user "
                "VALUES (%s, %s, %s, %s)")
    data_user = (username, usr_password, banner_id, usr_role)

    #insert new user
    cursor.execute(add_user, data_user)

    #commit data to database
    sql.get_connection().commit()
    rows_inserted = (cursor.rowcount)
    cursor.close()
    sql.disconnect()
    return rows_inserted





