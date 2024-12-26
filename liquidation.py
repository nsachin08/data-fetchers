import asyncio
import json 
import os 
from datetime import datetime 
import pytz 
from websockets import connect 
from termcolor import cprint 

websocket_url = 'wss://fstream.binance.com/ws/!forceOrder@arr'
filename = 'binance.csv'

async def binance_liquidation(uri, filename):
    async with connect(uri) as websocket:
        while True:
            try:
                msg = await websocket.recv()
                order_data = json.loads(msg)['o']
                symbol = order_data['s'].replace('USDT', '')
                side = order_data['S']
                timestamp = int(order_data['T'])
                filled_quantity = float(order_data['z'])
                price = float(order_data['p'])
                usd_size = filled_quantity * price
                est = pytz.timezone("US/Eastern")
                time_est = datetime.fromtimestamp(timestamp/ 1000, est).strftime('%H:%M:%S')
                if usd_size > 3000:
                    liquidation_type = 'L LIQ' if side == 'SELL' else 'S LIQ'
                    symbol = symbol[:4]
                    output = f"{liquidation_type} {symbol} {time_est} {usd_size:,.0f}"
                    color = 'green' if side == 'SELL' else 'red'
                    attrs = ['bold'] if usd_size > 10000 else []

                    if usd_size > 250000:
                        stars = '*' * 3 
                        attrs.append('blink')
                        output = f'{stars}{output}'
                        for _ in range(4):
                            cprint(output, 'white', f'on_{color}', attrs=attrs)
                    elif usd_size > 100000:
                        stars = '*' *1
                        attrs.append('blink')
                        output = f'{stars}{output}'
                        for _ in range(2):
                            cprint(output, 'white', f'on_{color}', attrs=attrs)

                    elif usd_size > 25000:
                        cprint(output, 'white', f'on_{color}', attrs=attrs)

                    else:
                        cprint(output, 'white', f'on_{color}')

                    print('')

            except Exception as e:
                await asyncio.sleep(5)

asyncio.run(binance_liquidation(websocket_url, filename))