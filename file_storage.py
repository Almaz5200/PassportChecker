import os
import json
from typing import Dict, Any

class FileStorage:
    def __init__(self):
        if os.environ.get("RUNNING_IN_DOCKER") == "true":
            self.path = "/app/data"
        else:
            self.path = "data"
        
    def get(self, user_id: str):
        user_path = os.path.join(self.path, user_id + ".json")
        if not os.path.exists(user_path):
            return None
        with open(user_path, "r") as f:
            return json.load(f)
        
    def set(self, user_id: str, data: Dict[str, Any]):
        if not os.path.exists(self.path):
            os.makedirs(self.path)
         
        user_path = os.path.join(self.path, user_id + ".json")
        with open(user_path, "w") as f:
            json.dump(data, f)
        