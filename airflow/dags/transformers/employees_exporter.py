from typing import List, Dict

def transform(source_data:List[Dict]):
    dest_json = {}
    """begin custom transform logic"""

    dest_json = {emp['id'] : {'name' : emp['employee_name'], 'age' : emp['employee_age']} for emp in source_data['data']}

    """end custom transform logic"""
    return dest_json
