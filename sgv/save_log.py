from qbuilder import QBuilder
from datetime import datetime

def save_log(type: str, database: QBuilder, content: str):
    date = datetime.now()
    
    logs = database["log"].all(where = {
        "type": {"eq": f"'{type}'"}
    })
    
    if len(logs) >= 100:
        database["log"].delete({
            "id": {"eq": logs[-1]["id"]}
        })
    
    database["log"].insert({
        "type": type,
        "date": f"{date.year}-{date.month}-{date.day}",
        "content": (
            f"[{date.day}/{date.month}/{date.year}] {content}"
        )
    })