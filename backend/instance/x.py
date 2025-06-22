import sqlite3
from datetime import datetime, timezone
DATABASE_FILE = 'chat_history.db'

def display_database():
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        # cursor.execute("Delete from chat")
        # conn.commit()
        # date= str(datetime.now(timezone.utc))
        # current_timestamp = datetime.now(timezone.utc).isoformat()  # Get current timestamp in ISO format

        cursor.execute(
            "INSERT INTO User ( id,user_id,password ) VALUES (?, ?, ?)",
            (1, 'ruthvik', '1234')
        )
        cursor.execute("SELECT * FROM chat")
        rows = cursor.fetchall()

        # Get column names
        cursor.execute("PRAGMA table_info(chat)")
        columns_info = cursor.fetchall()
        column_names = [info[1] for info in columns_info]

        if column_names:
            print("| " + " | ".join(column_names) + " |")
            print("|" + "---|" * len(column_names))
            for row in rows:
                print("| " + " | ".join(map(str, row)) + " |")
        else:
            print("The 'chat' table is empty or doesn't exist.")

    except sqlite3.Error as e:
        print(f"Error connecting to or querying the database: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    display_database()



# from datetime import datetime, timezone
# import sqlite3

# DATABASE_FILE = 'chat_history.db'

# def display_database():
#     try:
#         conn = sqlite3.connect(DATABASE_FILE)
#         cursor = conn.cursor()
#         date= str(datetime.now(timezone.utc))
#         cursor.execute("Delete from chat")
#         cursor.execute("INSERT INTO chat (id, user_id, user_message, bot_response, timestamp) VALUES (1, 'react_user', 'my name is sathvik', 'ok',"+date+" ;")
#         cursor.execute("SELECT * FROM chat")
