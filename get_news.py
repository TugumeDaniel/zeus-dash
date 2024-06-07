import requests

def get_news():
    query = "SELECT * FROM power_news"
    r = requests.post("https://zeus.ttobbi.com/api/sql.php", data={'query': query})
    json_data = r.text
    return json_data
def get_history():
    query = "SELECT * FROM historical_data"
    r = requests.post("https://zeus.ttobbi.com/api/sql.php", data={'query': query})
    json_data = r.text
    return json_data
def calculate_adjusted_status(row):
    confidence = row['confidence']
    status = row['status']
    
    if status == 1:
        return (confidence / 2) + 0.5
    else:
        return 0.5 - (confidence / 2)