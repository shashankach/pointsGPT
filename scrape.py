import requests
from bs4 import BeautifulSoup
import json

def fetch_data():

    headers ={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    url = "https://frequentmiler.com/current-point-transfer-bonuses/"
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'lxml')
    
    # Assuming the data is stored in a table
    data_list = []
    table = soup.find('table', {'class': 'tablepress tablepress-id-33 tablepress-responsive'})
    rows = table.find_all('tr')
    
    for row in rows:
        cols = row.find_all('td')
        if len(cols) == 3:  # Ensuring each row has three columns
            data = {
                'Transfer From': cols[0].text.strip(),
                'Transfer Bonus Details': cols[1].text.strip(),
                'End Date': cols[2].text.strip()
            }
            data_list.append(data)
    
    with open('scrape_data.json', 'w') as scrape_data:
        json.dump(data_list, scrape_data, indent=4)
    
    print(data_list)

# def save_to_json(data_list, filename):
#     with open(filename, 'w') as file:
#         json.dump(data_list, file, indent=4)

fetch_data()
