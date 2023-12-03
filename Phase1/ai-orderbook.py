import time
import requests
import pandas as pd
from datetime import datetime

while True:
    response = requests.get('https://api.bithumb.com/public/orderbook/BTC_KRW/?count=5')
    
    if response.status_code == 200:
        book = response.json()
        data = book['data']

        bids = (pd.DataFrame(data['bids'])).apply(pd.to_numeric,errors='ignore')
        bids.sort_values('price', ascending=False, inplace=True)
        bids = bids.reset_index(); del bids['index']
        bids['type'] = 0
    
        asks = (pd.DataFrame(data['asks'])).apply(pd.to_numeric,errors='ignore')
        asks.sort_values('price', ascending=True, inplace=True)
        asks['type'] = 1 

        df = bids.append(asks)

        # Add a 'timestamp' column with the current timestamp
        df['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')

        # Define the file name based on the current date
        current_date = datetime.now().strftime('%Y-%m-%d')
        file_name = '%s-bithumb-BTC-orderbook.csv'% current_date 

        # Reorder the columns to match your desired format
        df = df[['price', 'quantity', 'type', 'timestamp']]

        print(df)

        # Save data to a CSV file with the specified file name
        df.to_csv(file_name, mode='a', header=False, index=False)

    time.sleep(5)
