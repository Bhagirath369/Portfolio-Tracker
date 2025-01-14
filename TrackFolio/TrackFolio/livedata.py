from bs4 import BeautifulSoup
import requests
import lxml

# site for live data
url = "https://merolagani.com/LatestMarket.aspx#0"

req = requests.get(url)  # making requests to  fetch the raw html data
soup = BeautifulSoup(req.text,'lxml')
table = soup.find('table', class_ ="table table-hover live-trading sortable")
headers = [i.text for i in table.find_all('th')] # data of the tag 'th'

data =[ j for j in table.find_all('tr',{"class":['decrease-row','increase-row', 'nochange-row']})]

result = [{headers[index]:cell.text for index,cell in enumerate(row.find_all('td'))} for row in data]
print(result)