import json 
import os 

class JSON:
    def __init__(self, json_file):
        self.json_file = json_file 
        self.indent = 4
        self.verbose = True 

    def load_json(self):
        with open(self.json_file, 'r') as file:
            return json.load(file)
        
    def save_json(self, data):
        with open(self.json_file, 'w') as file:
            file.write(json.dumps(data, indent=4))
    
    