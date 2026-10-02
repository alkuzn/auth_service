import os

class Config:
    db_asyncdriver="postgresql+asyncpg"
    db_syncdriver="postgresql+psycopg"
    
    def __init__(self):
        #self.db_host=os.getenv("DB_HOST")
        self.db_host="localhost"
        self.db_name = 'reg_service_db'
        self.db_user = 'reg_service'
        self.db_password = '123'
        self.db_port = 5432

    def __db_url_(self, driver):
        return f"{driver}://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
    
    @property
    def db_asyncurl(self):
        return self._Config__db_url_(self.db_asyncdriver)
    
    @property
    def db_syncurl(self):
        return self._Config__db_url_(self.db_syncdriver)