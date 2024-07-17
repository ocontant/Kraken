from krakenfx.core.database import Base

print("Tables known to declarative_base():")
for table_name in Base.metadata.tables.keys():
    print(table_name)
