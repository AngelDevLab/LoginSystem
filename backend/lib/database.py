import mysql.connector
from mysql.connector import Error
from fastapi import HTTPException
from config import settings
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def connection():
    try:
        connection = mysql.connector.connect(
            host=settings.mysql_host,
            port=settings.mysql_port,
            user=settings.mysql_username,
            password=settings.mysql_password,
            database=settings.mysql_database
        )
        if connection.is_connected():
            return connection
        else:
            raise HTTPException(status_code=500, detail="[ERROR] Failed to connect to the database")
    except Error as e:
        raise HTTPException(status_code=500, detail=f"[ERROR] Database mysql_connection: {e}")

def table_user_info_init():
    db = connection()
    try:
        cursor = db.cursor()

        # 檢查 user_info 表是否存在
        cursor.execute("SHOW TABLES LIKE 'user_info';")
        result = cursor.fetchone()

        if not result:
            create_table_query = """
            CREATE TABLE user_info (
                id INT AUTO_INCREMENT PRIMARY KEY,
                email VARCHAR(100) NOT NULL UNIQUE,
                hashed_password VARCHAR(64) NOT NULL,
                level INT,
                hashed_authenticate_code VARCHAR(64),
                authenticate_status BOOLEAN,
                today_api_use INT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            );
            """
            cursor.execute(create_table_query)
            db.commit()

    except Error as e:
        logging.error(f"[ERROR] db init {e}")
    finally:
        cursor.close()
        db.close()




def user_info_analysis(data):
    if data and len(data) >= 9:
        user_info_dict = {
            "id": data[0],
            "email": data[1],
            "hashed_password": data[2],
            "level": data[3],
            "hashed_authenticate_code": data[4],
            "authenticate_status": data[5],
            "today_api_use": data[6],
            "created_at": data[7],
            "updated_at": data[8]
        }

        return user_info_dict
    
    return None

def update_user_info_api_count(email):
    try:
        db = connection()
        cursor = db.cursor()

        query = """
        UPDATE user_info
        SET today_api_use = today_api_use + 1
        WHERE email = %s
        """
        cursor.execute(query, (email,))
        
        db.commit()

    except Error as e:
        print(f"Error updating API count: {e}")
    
    finally:
        cursor.close()
        db.close()

def fetch_one(db, table_name, title, data):
    cursor = db.cursor()
    cursor.execute(f"SELECT * FROM {table_name} WHERE {title} = %s", (data,))
    return cursor.fetchone()

def delete_one(db, table_name, title, data):
    cursor = db.cursor()
    cursor.execute(f"DELETE FROM {table_name} WHERE {title} = %s", (data,))
    db.commit()
    cursor.close()


def write(db, table_name: str, columns: tuple, data: tuple):
    cursor = db.cursor()

    # 創建佔位符，如 %s, %s, %s 來對應數據的長度
    placeholders = ', '.join(['%s'] * len(data))
    columns_str = ', '.join(columns)

    query = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"

    cursor.execute(query, data)
    db.commit()


def update_authenticate_status(db, email: str, status: bool):
    cursor = db.cursor()
    query = """
    UPDATE user_info
    SET authenticate_status = %s
    WHERE email = %s
    """
    cursor.execute(query, (status, email))
    db.commit()
    cursor.close()

def get_all_user_info():
    db = connection()
    try:
        cursor = db.cursor(dictionary=True)
        query = """
        SELECT id, email, level, authenticate_status, today_api_use, created_at, updated_at 
        FROM user_info;
        """
        cursor.execute(query)
        result = cursor.fetchall()  # 獲取所有資料
        return result

    except Error as e:
        logging.error(f"[ERROR] Failed to retrieve user info: {e}")
        return None

    finally:
        cursor.close()
        db.close()
