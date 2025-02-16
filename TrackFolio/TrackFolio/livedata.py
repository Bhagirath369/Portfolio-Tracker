
from bs4 import BeautifulSoup
import requests
import psycopg2

# Fetch the live stock data from Merolagani
def fetch_live_stock_data():
    url = "https://merolagani.com/LatestMarket.aspx#0"
    req = requests.get(url)
    soup = BeautifulSoup(req.text, 'lxml')

    # Find the table that contains the stock data
    table = soup.find('table', class_="table table-hover live-trading sortable")
    
    # Extract data rows
    data = [j for j in table.find_all('tr', {"class": ['decrease-row', 'increase-row', 'nochange-row']})]
    
    # Create a list of stock symbols and other information
    stocks = []
    for row in data:
        columns = row.find_all('td')
        stock = {
            'stock_symbol': columns[0].find('a').text.strip(),  # Stock symbol
            'stock_name': columns[0].find('a')['title'].strip(),  # Stock name
            'ltp': float(columns[1].text.strip().replace(',', '')),  # LTP (Last Traded Price)
            'percent_change': float(columns[2].text.strip().replace('%', '').replace(',', '')),  # % Change
            'open_price': float(columns[4].text.strip().replace(',', '')),  # Open price
            'high_price': float(columns[5].text.strip().replace(',', '')),  # High price
            'low_price': float(columns[6].text.strip().replace(',', ''))  # Low price
        }
        stocks.append(stock)
    # print(stocks)
    return stocks

# Insert data into PostgreSQL
def insert_data_into_db(stocks):
    try:
        connection = psycopg2.connect(
            host="localhost",    
            database="trackfolio_db",  
            user="postgres",   
            password="Devendra@123"
        )
        cursor = connection.cursor()

        for stock in stocks:
            print(f"Inserting data: {stock}")  # Debugging line to print data

            cursor.execute(
                """
                INSERT INTO live_stocks (stock_symbol, stock_name, ltp, percent_change, open_price, high_price, low_price)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (stock_symbol) DO UPDATE
                SET ltp = EXCLUDED.ltp,
                    percent_change = EXCLUDED.percent_change,
                    open_price = EXCLUDED.open_price,
                    high_price = EXCLUDED.high_price,
                    low_price = EXCLUDED.low_price;
                """,
                (stock['stock_symbol'], stock['stock_name'], stock['ltp'], stock['percent_change'], stock['open_price'], stock['high_price'], stock['low_price'])
            )
            print(f"Inserted/Updated: {stock['stock_symbol']}")

        connection.commit()
        print("Data committed successfully.")
        
    except Exception as e:
        print(f"Error inserting data: {e}")
    finally:
        if connection:
            cursor.close()
            connection.close()

# Fetch the live stock data
stocks = fetch_live_stock_data()

# Insert the fetched data into the PostgreSQL database
insert_data_into_db(stocks)

