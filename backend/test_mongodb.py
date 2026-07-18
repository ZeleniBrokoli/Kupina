from config import db

# print(db.name)
# print("MongoDB connection successful!")

print("Database name:", db.name)
print("Collections:", db.list_collection_names())