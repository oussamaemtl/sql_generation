import psycopg2
import psycopg2.errors


import pandas as pd


def fetch_data(
    sql_query: str, host: str, port: int, dbname: str, user: str, password: str
):
    """
    Connects to a PostgreSQL database, executes the given SQL query,
    and returns a tuple of (list_of_column_names, dataframe_of_results).

    Parameters:
    -----------
    sql_query : str
        The SQL query statement to execute.

    Returns:
    --------
    (list, pandas.DataFrame)
        - A list of column names
        - A pandas DataFrame containing the rows returned by the query
    """

    # Update these with your actual connection details
    connection_params = {
        "dbname": dbname,
        "user": user,
        "password": password,
        "host": host,
        "port": port,
    }

    # Connect to PostgreSQL
    conn = psycopg2.connect(**connection_params)
    cursor = conn.cursor()

    try:
        # Execute the query
        cursor.execute(sql_query)
        rows = cursor.fetchall()  # All rows from the query

        # Extract column names from cursor.description
        col_names = [desc[0] for desc in cursor.description]

        # Create a pandas DataFrame from the fetched rows and column names
        df = pd.DataFrame(rows, columns=col_names)
    finally:
        # Always close the cursor and connection
        cursor.close()
        conn.close()

    return col_names, df


def execute_sql_file(
    filepath: str, host: str, port: int, dbname: str, user: str, password: str
) -> None:
    """
    Connect to a PostgreSQL database, read a .sql file, and execute its contents.
    If the SQL statements are invalid, an error is raised.

    :param filepath:  Path to the .sql file containing the statements
    :param host:      Hostname or IP address of the PostgreSQL server
    :param port:      Port number of the PostgreSQL server
    :param dbname:    Database name
    :param user:      Username for authentication
    :param password:  Password for authentication
    :raises psycopg2.Error: If the SQL statements are invalid or execution fails
    """
    # Read the SQL file
    with open(filepath, "r", encoding="utf-8") as f:
        sql_content = f.read()

    # Establish a connection
    connection_params = {
        "dbname": dbname,
        "user": user,
        "password": password,
        "host": host,
        "port": port,
    }
    conn = psycopg2.connect(**connection_params)

    # Create a cursor for executing statements
    cursor = conn.cursor()
    try:
        # Execute the SQL file content
        cursor.execute(sql_content)
        # Commit if everything is valid
        conn.commit()
    except psycopg2.Error as e:
        # Roll back any changes if there's an error
        conn.rollback()
        raise e  # re-raise the exception to inform the caller
    finally:
        cursor.close()
        conn.close()
