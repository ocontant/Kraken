from krakenfx.repository.models._base import Base

print("Tables known to declarative_base():\n")
for table_name in Base.metadata.tables.keys():
    print(table_name)
