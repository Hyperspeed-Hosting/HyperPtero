import sqlite3

class User:
    def __init__(self, discord_id=None, pterodactyl_id=None, pterodactyl_api_key=None, user_id=None, email=None):
        self.id = user_id #Represents the Unique ID on SQL
        self.discord_id:int = discord_id #Represent Discord User's ID
        self.pterodactyl_id = pterodactyl_id #Represent Pterodactyl User's ID
        self.pterodactyl_api_key = pterodactyl_api_key #Represent Pterodactyl API Key of User
        self.email = email #Represent User's Email

    def __repr__(self):
        return (f"User(id={self.id}, discord_id={self.discord_id}, "
                f"pterodactyl_id={self.pterodactyl_id}, pterodactyl_api_key='{self.pterodactyl_api_key}')")
    
    @staticmethod
    def __table__() -> str:  # return Table
        return '''CREATE TABLE IF NOT EXISTS users(
                    "id" INTEGER NOT NULL UNIQUE,
                    "discord_id" INTEGER NOT NULL,
                    "pterodactyl_id" INTEGER NOT NULL,
                    "pterodactyl_api_key" TEXT NOT NULL,
                    "email" TEXT NOT NULL,
                    PRIMARY KEY("id" AUTOINCREMENT)
                );'''



class Database:
    def __init__(self):
        """
        Initialize a DatabaseManager with the specified SQLite database file.

        Parameters:
        - dbfile (str): The path to the SQLite database file.
        """
        self.dbfile = "database.db"
        self.connection = sqlite3.connect(self.dbfile)
        self.cursor = self.connection.cursor()

        self.create_tables()

    def create_tables(self):
        self.cursor.executescript(User.__table__())

    def find_user_by_email(self, email: str) -> User:
        query = "SELECT id, discord_id, pterodactyl_id, pterodactyl_api_key, email FROM users WHERE email = ?"
        self.cursor.execute(query, (email,))
        result = self.cursor.fetchone()

        if result:
            return User(
                user_id=result[0],
                discord_id=result[1],
                pterodactyl_id=result[2],
                pterodactyl_api_key=result[3],
                email=result[4]
            )
        else:
            return None
        
    def find_user_by_discord_id(self, discordID: int) -> User:
        query = "SELECT id, discord_id, pterodactyl_id, pterodactyl_api_key, email FROM users WHERE discord_id = ?"
        self.cursor.execute(query, (discordID,))
        result = self.cursor.fetchone()

        if result:
            return User(
                user_id=result[0],
                discord_id=result[1],
                pterodactyl_id=result[2],
                pterodactyl_api_key=result[3],
                email=result[4]
            )
        else:
            return None
    
    def add_user(self, user: User) -> None:
        query = '''INSERT INTO users (discord_id, pterodactyl_id, pterodactyl_api_key, email)
                   VALUES (?, ?, ?, ?)'''
        self.cursor.execute(query, (user.discord_id, user.pterodactyl_id, user.pterodactyl_api_key, user.email))
        self.connection.commit()
