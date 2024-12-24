import os
import sys
import streamlit as st

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, BASE_DIR)
from utils.db_interaction import execute_sql_file, fetch_data
from rag_sql import generate_sql
from protected import pwd_db


def main():
    st.title("RAG-based SQL Generation Demo")

    # 1. Initialize session state variables if not present
    if "generated_sql" not in st.session_state:
        st.session_state.generated_sql = None
    if "unique_id" not in st.session_state:
        st.session_state.unique_id = None
    if "boo" not in st.session_state:
        st.session_state.boo = False

    user_instruction = st.text_input("Enter your instruction", value="")

    # 2. Generate SQL from instruction
    if st.button("Generate SQL"):
        try:
            # Example: actually call your LLM or logic here
            st.session_state.boo, st.session_state.unique_id = generate_sql(
                user_instruction
            )

            # For demonstration, hard-code some values
            # st.session_state.boo = True
            # st.session_state.unique_id = "45c7dc3978c44dd6ab00ced663b7607b"

            if not st.session_state.boo:
                st.info("Output from the LLM could not be parsed")
            else:
                sql_path = os.path.join(
                    BASE_DIR,
                    "sql_files",
                    "views",
                    f"final_query_{st.session_state.unique_id}.sql",
                )
                with open(sql_path, "r", encoding="utf-8") as file:
                    st.session_state.generated_sql = file.read()

        except Exception as e:
            st.error(f"An error occurred: {e}")

    # 3. If we have generated SQL stored, show it and let user fetch data
    if st.session_state.generated_sql:
        st.write("**Generated SQL:**")
        st.code(st.session_state.generated_sql, language="sql")

        # Show table sample
        st.info("Table sample:")
        try:
            col_names, data = fetch_data(
                st.session_state.generated_sql,
                host="localhost",
                port=5432,
                dbname="pagila",
                user="postgres",
                password=pwd_db,
            )
            st.write(f"Number of rows: {len(data)}")
            if len(data) > 0:
                st.dataframe(data)
            else:
                st.write("No data returned from the view.")
        except Exception as e:
            st.error(f"Error fetching data: {e}")

        # 4. Optionally let user confirm they want to execute the statement
        if st.button("Upload to database"):
            try:
                view_file_path = os.path.join(
                    BASE_DIR,
                    "sql_files",
                    "views",
                    f"create_or_replace_view_{st.session_state.unique_id}.sql",
                )

                log_view_file_path = os.path.join(
                    BASE_DIR,
                    "sql_files",
                    "logging",
                    f"insert_into_generated_views_{st.session_state.unique_id}.sql",
                )

                log_file_path = os.path.join(
                    BASE_DIR,
                    "sql_files",
                    "logging",
                    f"insert_into_queries_log_{st.session_state.unique_id}.sql",
                )

                execute_sql_file(
                    filepath=view_file_path,
                    host="localhost",
                    port=5432,
                    dbname="pagila",
                    user="postgres",
                    password=pwd_db,
                )

                execute_sql_file(
                    filepath=log_file_path,
                    host="localhost",
                    port=5432,
                    dbname="pagila",
                    user="postgres",
                    password=pwd_db,
                )

                execute_sql_file(
                    filepath=log_view_file_path,
                    host="localhost",
                    port=5432,
                    dbname="pagila",
                    user="postgres",
                    password=pwd_db,
                )

                st.success("SQL executed successfully!")
            except Exception as e:
                st.error(f"Error executing SQL files: {e}")


if __name__ == "__main__":
    main()
