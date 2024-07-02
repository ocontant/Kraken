# utils/database_inspection.py
from sqlalchemy import inspect

def output_db_structure_and_data(engine):
    inspector = inspect(engine)

    print("Database Structure:")
    for table_name in inspector.get_table_names():
        print(f"Table: {table_name}")
        
        columns = inspector.get_columns(table_name)
        for column in columns:
            print(f"  Column: {column['name']} - {column['type']}")

        # Query and print data for each table
        with engine.connect() as connection:
            result = connection.execute(f"SELECT * FROM {table_name}")
            rows = result.fetchall()
            if rows:
                print(f"\nData in {table_name}:")
                for row in rows:
                    print(dict(row))
            else:
                print(f"\nNo data found in {table_name}")
        print("\n")
