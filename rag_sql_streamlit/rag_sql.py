import os
import os
import uuid
import sys
from protected import open_ai_key, grocq_api_key
from langchain_openai import ChatOpenAI

# Define the base directory
# Define the base directory
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, BASE_DIR)
os.environ["OPENAI_API_KEY"] = open_ai_key
os.environ["GROQ_API_KEY"] = grocq_api_key

from utils.db_interaction import execute_sql_file
import json
import re
import uuid
from protected import pwd_db
import psycopg2
from config import multi_context_prompt
from langchain.docstore.document import Document
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_ollama import OllamaLLM
from groq import Groq


def clean_sql_dump(sql_dump: str) -> str:
    """
    Removes SQL-style comments, flattens newlines, and condenses extra spaces.
    """
    # Remove line-based SQL comments (e.g. -- comment)
    sql_dump = re.sub(r"--.*?$", "", sql_dump, flags=re.MULTILINE)
    # Remove /* */ block comments if present
    sql_dump = re.sub(r"/\*.*?\*/", "", sql_dump, flags=re.DOTALL)
    # Replace newlines with spaces
    sql_dump = re.sub(r"\n", " ", sql_dump)
    # Replace multiple spaces with single space
    sql_dump = re.sub(r"\s{2,}", " ", sql_dump)
    # Trim leading/trailing whitespace
    sql_dump = sql_dump.strip()
    return sql_dump


def extract_schema_info(sql_dump: str):
    """
    Extracts table definitions, primary keys, foreign keys, and
    a simple 'joins' mapping from a cleaned SQL dump.
    """
    # Regex patterns
    # This pattern handles optional schema name (e.g. CREATE TABLE public.actor ...)
    # and captures everything inside the parentheses up to the matching semicolon.
    table_pattern = re.compile(
        r"CREATE TABLE\s+"
        r'(?:["]?(\w+)["]?\.)?'  # optional schema name (group 1)
        r'["]?(\w+)["]?'
        r"\s*\((.*?)\)\s*;",
        re.IGNORECASE | re.DOTALL,
    )

    pkey_pattern = re.compile(
        r"ALTER TABLE ONLY\s+"
        r'(?:["]?(\w+)["]?\.)?'  # optional schema name
        r'["]?(\w+)["]?'
        r"\s+ADD CONSTRAINT\s+(\w+)\s+PRIMARY KEY\s*\((.*?)\);",
        re.IGNORECASE | re.DOTALL,
    )

    fkey_pattern = re.compile(
        r"ALTER TABLE ONLY\s+"
        r'(?:["]?(\w+)["]?\.)?'  # optional schema name
        r'["]?(\w+)["]?'
        r"\s+ADD CONSTRAINT\s+(\w+)\s+FOREIGN KEY\s*\((.*?)\)\s+REFERENCES\s+"
        r'(?:["]?(\w+)["]?\.)?'  # optional ref schema
        r'["]?(\w+)["]?\s*\((.*?)\)'
        r"(?:\s+ON UPDATE \w+\s+ON DELETE \w+)?;",
        re.IGNORECASE | re.DOTALL,
    )

    # Data structures to fill
    tables = {}
    primary_keys = {}
    foreign_keys = {}
    joins = {}

    # Extract tables
    for match in table_pattern.finditer(sql_dump):
        schema_name = match.group(1)  # Might be None if no schema specified
        table_name = match.group(2)
        columns_str = match.group(3)

        # Key for referencing the table will just be table_name
        # but you could store "schema.table" if needed:
        full_table_name = (
            table_name if not schema_name else f"{schema_name}.{table_name}"
        )

        tables[full_table_name] = columns_str

    # Extract primary keys
    for match in pkey_pattern.finditer(sql_dump):
        schema_name = match.group(1)
        table_name = match.group(2)
        pkey_name = match.group(3)
        pkey_columns = match.group(4).strip()

        full_table_name = (
            table_name if not schema_name else f"{schema_name}.{table_name}"
        )
        primary_keys[full_table_name] = {
            "pkey_name": pkey_name,
            "pkey_columns": pkey_columns,
        }

    # Extract foreign keys
    for match in fkey_pattern.finditer(sql_dump):
        schema_name = match.group(1)
        table_name = match.group(2)
        fkey_name = match.group(3)
        fkey_columns = match.group(4).strip()
        ref_schema = match.group(5)
        ref_table_name = match.group(6)
        ref_columns = match.group(7).strip()

        full_table_name = (
            table_name if not schema_name else f"{schema_name}.{table_name}"
        )
        full_ref_table_name = (
            ref_table_name
            if not ref_schema
            else f"{ref_schema}.{ref_table_name}"
        )

        if full_table_name not in foreign_keys:
            foreign_keys[full_table_name] = []

        foreign_keys[full_table_name].append(
            {
                "fkey_name": fkey_name,
                "fkey_columns": fkey_columns,
                "ref_table": full_ref_table_name,
                "ref_columns": ref_columns,
            }
        )

    # For simplicity, let's say "joins" just replicate foreign_keys
    joins = foreign_keys

    return tables, primary_keys, foreign_keys, joins


def create_rag_documents(tables, primary_keys, foreign_keys, joins):
    """
    Converts the extracted schema info into a list of JSON-like documents
    suitable for RAG ingestion. Each document contains:
      - table_name
      - columns (list of columns)
      - primary_key
      - foreign_keys
      - joins
    """
    documents = []

    for table_name, columns_str in tables.items():
        # Split columns by commas that are not inside parentheses
        # (to avoid splitting on something like numeric(4,2)).
        # A simpler approach is to split by lines or semicolons, but let's do a naive approach:
        raw_cols = split_columns(columns_str)

        # Clean each column definition
        cleaned_cols = [
            clean_column_definition(c) for c in raw_cols if c.strip()
        ]

        doc = {
            "table_name": table_name,
            "columns": cleaned_cols,
            "primary_key": primary_keys.get(table_name, {}),
            "foreign_keys": foreign_keys.get(table_name, []),
            "joins": joins.get(table_name, []),
        }
        documents.append(doc)

    return documents


def split_columns(columns_block: str):
    """
    Split a CREATE TABLE column block into individual column/constraint lines,
    ignoring commas found inside parentheses (like numeric(4,2)).
    """
    # A very common approach is to do a manual parse counting parentheses.
    # For brevity, here’s a quick version:
    results = []
    current = []
    paren_depth = 0

    for char in columns_block:
        if char == "(":
            paren_depth += 1
            current.append(char)
        elif char == ")":
            paren_depth -= 1
            current.append(char)
        elif char == "," and paren_depth == 0:
            # We reached a top-level comma -> new column
            results.append("".join(current).strip())
            current = []
        else:
            current.append(char)

    # Add the last accumulated column
    if current:
        results.append("".join(current).strip())

    return results


def clean_column_definition(col_def: str) -> str:
    """
    Cleans up one column/constraint definition line by removing extra
    semicolons, repeating spaces, etc.
    """
    # Remove trailing semicolons if any
    col_def = col_def.rstrip(";")
    # Convert multiple spaces to single
    col_def = re.sub(r"\s{2,}", " ", col_def)
    # Trim
    col_def = col_def.strip()
    return col_def


def get_pagila_context(sql_dump_path: str = "./context/pagila-schema.sql"):
    sql_dump_path = os.path.join(BASE_DIR, "context", "pagila-schema.sql")
    with open(sql_dump_path, "r") as file:
        sql_dump = file.read()
    sql_dump = clean_sql_dump(sql_dump)

    tables, primary_keys, foreign_keys, joins = extract_schema_info(sql_dump)
    rag_docs = create_rag_documents(tables, primary_keys, foreign_keys, joins)
    documents = []
    for doc in rag_docs:
        # Convert dict to a JSON string or any text representation you prefer
        text_content = json.dumps(doc, ensure_ascii=False, indent=2)
        documents.append(Document(page_content=text_content))

    # ------------------------------------------------------
    # 2) Create embeddings with a Hugging Face model + FAISS vector store
    # ------------------------------------------------------
    # Example: Using the MiniLM model from SentenceTransformers
    embedding_model = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    vectorstore = FAISS.from_documents(documents, embedding=embedding_model)
    # Create a retriever
    retriever = vectorstore.as_retriever(search_kwargs={"k": 10})
    return retriever, vectorstore


def get_logging_context():
    """
    Connect to PostgreSQL and retrieve table structures and some rows
    from queries_log and generated_views for an LLM 'logging context'.
    """
    connection_params = {
        "dbname": "pagila",
        "user": "postgres",
        "password": pwd_db,
        "host": "localhost",
        "port": 5432,
    }
    # Connect to the database
    conn = psycopg2.connect(**connection_params)
    cursor = conn.cursor()

    # Helper: fetch columns from information_schema
    def fetch_table_structure(table_name):
        cursor.execute(
            """
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = %s
            ORDER BY ordinal_position
        """,
            (table_name,),
        )
        columns = cursor.fetchall()
        # Build a small text block describing each column
        lines = []
        for col_name, data_type, is_nullable in columns:
            lines.append(
                f"  - {col_name} {data_type} {'(nullable)' if is_nullable == 'YES' else '(not null)'}"
            )
        structure_str = "Columns:\n" + "\n".join(lines)
        return structure_str

    # Helper: fetch sample rows from each table
    def fetch_sample_rows(table_name):
        cursor.execute(f"SELECT * FROM {table_name} ORDER BY created_at")
        rows = cursor.fetchall()
        # If you want column names, re-fetch from cursor.description:
        col_names = [desc.name for desc in cursor.description]

        lines = []
        for row in rows:
            # Zip column names with the row values
            row_data = ", ".join(
                f"{col}: {val}" for col, val in zip(col_names, row)
            )
            lines.append("    " + row_data)
        if not lines:
            lines = ["    No rows found."]
        return "\n".join(lines)

    # Build the logging context
    logging_context_lines = ["-- LOGGING SCHEMA METADATA --"]

    for table_name in ["queries_log", "generated_views"]:
        logging_context_lines.append(f"Table: {table_name}")
        # structure
        table_structure = fetch_table_structure(table_name)
        logging_context_lines.append(table_structure)
        # sample rows
        sample_rows = fetch_sample_rows(table_name)
        logging_context_lines.append("Sample rows (up to 5):\n" + sample_rows)
        logging_context_lines.append("")  # blank line

    # Combine into a single text block
    logging_context = "\n".join(logging_context_lines)

    # Clean up
    cursor.close()
    conn.close()

    return logging_context


def run_prompt_template(question, llm_openai=False):

    retriever, _ = get_pagila_context()
    retrieved_docs = retriever.get_relevant_documents(question)
    # Combine them into a single string for the 'schema_context'
    schema_context_str = "\n".join(doc.page_content for doc in retrieved_docs)
    # 2) Retrieve logging context from Postgres
    logging_context_str = get_logging_context()

    print(schema_context_str)
    print("--------------------------------------------")
    print(logging_context_str)

    # 3) Format the final prompt
    final_prompt = multi_context_prompt.format(
        schema_context=schema_context_str,
        logging_context=logging_context_str,
        question=question,
    )
    if llm_openai:
        llm = ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0)
        response = llm(final_prompt)
    else:
        # llm = OllamaLLM(model="llama3")
        # response = llm(final_prompt)
        client = Groq(
            api_key=os.environ.get("GROQ_API_KEY"),
        )

        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": final_prompt,
                }
            ],
            model="llama3-8b-8192",
        )

        response = chat_completion.choices[0].message.content
    return response


def parse_llm_output_to_sql_files(
    llm_output: str, unique_id, output_dir: str = "sql_files"
) -> int:
    """
    Parse an LLM response containing up to four sections, each introduced by:
      1) -- Final Query
      2) -- Insert into queries_log
      3) -- Create or replace view
      4) -- Insert into generated_views

    Each section includes a triple-backtick '```sql' block with the actual SQL.

    Example chunk:
    1) -- Final Query
    ```sql
    SELECT f.title, c.name FROM ...
    ```

    We'll capture each code block and write it to a .sql file, placing them
    into 'logging/' or 'views/' subfolders, and appending a random UUID
    to the filename. This handles the new format where the lines aren't
    strictly 'markers' but a heading plus a triple-backtick code block.
    """

    # We'll define a list of regex patterns, each capturing the code between triple backticks
    # after the heading "1) -- Final Query", etc.
    #
    # - (?s) allows the dot to match newlines
    # - We then match something like: 1\)\s*--\s*Final\s*Query
    #   followed by any text (.*?) until we see ```sql
    # - Then capture (.*?) until the next ```
    #
    # Each tuple has the regex pattern + (base_filename, subfolder).
    patterns = [
        (
            r"(?s)1\)\s*--\s*Final\s*Query.*?```sql\s*(.*?)```",
            ("final_query", "views"),
        ),
        (
            r"(?s)2\)\s*--\s*Insert\s*into\s*queries_log.*?```sql\s*(.*?)```",
            ("insert_into_queries_log", "logging"),
        ),
        (
            r"(?s)3\)\s*--\s*Create\s*or\s*replace\s*view.*?```sql\s*(.*?)```",
            ("create_or_replace_view", "views"),
        ),
        (
            r"(?s)4\)\s*--\s*Insert\s*into\s*generated_views.*?```sql\s*(.*?)```",
            ("insert_into_generated_views", "logging"),
        ),
    ]

    # Ensure the base output directory exists
    output_dir = os.path.join(BASE_DIR, output_dir)
    os.makedirs(output_dir, exist_ok=True)

    nonempty_count = 0

    # Search the LLM output for each pattern in turn
    for pattern, (base_name, subfolder) in patterns:
        match = re.search(pattern, llm_output)
        if match:
            # Extract the code content from inside the triple backticks
            code_block = match.group(1).strip()

            # If there's something in the block, write it to a file
            if code_block:
                # Create the subfolder if needed
                subpath = os.path.join(output_dir, subfolder)
                os.makedirs(subpath, exist_ok=True)

                filename = f"{base_name}_{unique_id}.sql"
                file_path = os.path.join(subpath, filename)

                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(code_block + "\n")

                nonempty_count += 1

    print(
        f"Parsed {nonempty_count} section(s). Files written under '{output_dir}' with unique ID '{unique_id}'."
    )

    return nonempty_count


def generate_sql(question, llm_openai=False):
    # generating ID for the run
    unique_id = uuid.uuid4().hex

    # prompting
    llm_output = run_prompt_template(question, llm_openai)

    # output store
    llm_dump_path = os.path.join(
        BASE_DIR, "llm_output", f"llm_output_{unique_id}.txt"
    )
    with open(llm_dump_path, "w", encoding="utf-8") as f:
        f.write(llm_output)
    f.close()
    with open(llm_dump_path, "r") as file:
        llm_output = file.read()

    # Parsing the output
    nonempty_count = parse_llm_output_to_sql_files(llm_output, unique_id)
    if nonempty_count < 1:
        print(
            f"LLM output could not get parsed, please check file {llm_dump_path}"
        )
        return False, unique_id

    return True, unique_id


if __name__ == "__main__":
    # question = (
    #     "Quelle est la liste des films disponibles avec leur catégorie ?"
    # )

    question = "Create a list of all the actors’ first name and last name. Display the first and last name of each actor in a single column in upper case letters. Name the column Actor Name."
    boo, unique_id = generate_sql(question, llm_openai=False)

    # unique_id = "45c7dc3978c44dd6ab00ced663b7607b"
    # boo = True

    view_file_path = os.path.join(
        BASE_DIR,
        "sql_files",
        "views",
        f"create_or_replace_view_{unique_id}.sql",
    )

    log_view_file_path = os.path.join(
        BASE_DIR,
        "sql_files",
        "logging",
        f"insert_into_generated_views_{unique_id}.sql",
    )

    log_file_path = os.path.join(
        BASE_DIR,
        "sql_files",
        "logging",
        f"insert_into_queries_log_{unique_id}.sql",
    )

    execute_sql_file(
        filepath=view_file_path,
        host="localhost",
        port=5432,
        dbname="pagila",
        user="postgres",
        password=pwd_db,
    )

    # execute_sql_file(
    #     filepath=log_file_path,
    #     host="localhost",
    #     port=5432,
    #     dbname="pagila",
    #     user="postgres",
    #     password=pwd_db,
    # )

    # execute_sql_file(
    #     filepath=log_view_file_path,
    #     host="localhost",
    #     port=5432,
    #     dbname="pagila",
    #     user="postgres",
    #     password=pwd_db,
    # )
