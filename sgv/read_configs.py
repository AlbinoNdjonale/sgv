import json
import cript
from base_path import base_path

def read_configs() -> dict[str]:
    with open(base_path+"/files/configs.conf", encoding = "utf-8") as file:
        configs = {}
        
        for line in file.readlines():
            key, value = line.split("=")
            configs[key.strip()] = json.loads(value.strip())
            
    return cript.encriptar(configs)