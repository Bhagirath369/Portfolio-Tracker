


from bs4 import BeautifulSoup
import requests

def fetch_live_stock_data():
    url = "https://merolagani.com/LatestMarket.aspx#0" # getting data from merolagani
    req = requests.get(url)
    soup = BeautifulSoup(req.text, 'lxml')

    # Find the table that contains the stock data
    table = soup.find('table', class_="table table-hover live-trading sortable")
    
    # Extract headers and data
    headers = [i.text.strip() for i in table.find_all('th')]
    data = [j for j in table.find_all('tr', {"class": ['decrease-row', 'increase-row', 'nochange-row']})]
    
    # Create a list of stock symbols and names
    stocks = [
    {
        'stock_symbol': row.find_all('td')[0].find('a').text.strip(),  # Get stock symbol from <a> tag
        'stock_name': row.find_all('td')[0].find('a')['title'].strip()  # Get stock name from 'title' attribute of <a> tag
    }
    for row in data
    ]
    return stocks
