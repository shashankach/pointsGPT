import requests
from bs4 import BeautifulSoup
import json

def fetch_data():

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
    
    with open('scrape_data.json', 'w') as scrape_data:
        json.dump(data_list, scrape_data, indent=4)
    
    print(data_list)

fetch_data()
