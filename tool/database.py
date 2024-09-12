import json
import livejson

class DataBase:
    
    def __init__(self, data):
        self.database = livejson.File(data.database_path, 4)
        self.database_path = data.database_path
        self.text_path = data.text_path
    
    def saveText(self, text):
        with open(self.text_path, mode = "w", encoding = "utf-8") as file:
            file.write(text)
    
    def loadText(self):
        with open(self.text_path, encoding = "utf-8") as file:
            return file.read()
