import pyodbc
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import os

# Fetch the connection string from the environment variable
connection_string = "Driver={ODBC Driver 18 for SQL Server};Server=tcp:monotodo.database.windows.net,1433;Database=free-sql-db-7549392;Uid=monosql;Pwd=Dockervm@123;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"

# Check if the connection string is available
if connection_string:
    print(f"Connection String: {connection_string}")
else:
    print("Connection string not found in environment variables.")
    
app = FastAPI()

# Configure CORSMiddleware to allow all origins (disable CORS for development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # This allows all origins (use '*' for development only)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Define the Task model
class Task(BaseModel):
    title: str
    description: str

# Create a table for tasks (You can run this once outside of the app)
@app.get("/")
def create_tasks_table():
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Tasks' AND xtype='U')
        CREATE TABLE Tasks (
            ID INT IDENTITY(1,1) PRIMARY KEY,
            Title NVARCHAR(255),
            Description NVARCHAR(MAX)
        )
        """)
        conn.commit()  
        return "Add-Tasks API Ready."      
    except Exception as e:
        print(e)
        if "There is already an object named 'Tasks' in the database." in str(e):
            return "Add-Tasks API Ready."
        else:
            return "Error. Please check Logs."
    

# Create a new task
@app.post("/tasks")
def create_task(task: Task):
    try:
        with pyodbc.connect(connection_string) as conn:
            cursor = conn.cursor()

            cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Tasks')
            BEGIN
                CREATE TABLE Tasks (
                    ID INT IDENTITY(1,1) PRIMARY KEY,
                    Title NVARCHAR(255),
                    Description NVARCHAR(MAX)
                )
            END
            """)

            cursor.execute(
                "INSERT INTO Tasks (Title, Description) VALUES (?, ?)",
                task.title,
                task.description
            )

            conn.commit()

        return {"message": "Task created", "data": task}

    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    create_tasks_table()
