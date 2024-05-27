import requests
from bs4 import BeautifulSoup
import json

def convert_data(data):
    new_format = []
    for item in data:
        transfer_details = item["Transfer Bonus Details"]
        bonus, from_to = transfer_details.split(" transfer bonus from ")
        transfer_from, transfer_to = from_to.split(" to ")
        end_date = item["End Date"][5:]
        new_format.append({
            "Transfer From": transfer_from.strip(),
            "Transfer To": transfer_to.strip(),
            "Bonus": bonus.strip(),
            "End Date": end_date
        })
    return new_format

def fetch_data(file_name):

    headers ={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    url = "https://frequentmiler.com/current-point-transfer-bonuses/"
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'lxml')
    

    data_list = []
    table = soup.find('table', {'class': 'tablepress tablepress-id-33 tablepress-responsive'})
    rows = table.find_all('tr')
    
    for row in rows:
        cols = row.find_all('td')
        if len(cols) == 3: 
            data = {
                'Transfer From': cols[0].text.strip(),
                'Transfer Bonus Details': cols[1].text.strip(),
                'End Date': cols[2].text.strip()
            }
            data_list.append(data)

    new_data = convert_data(data_list)
 
    with open(file_name, 'w') as scrape_data:
        json.dump(new_data, scrape_data, indent=4)
    
    return(data_list)

fetch_data('scrape_data.json')