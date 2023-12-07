# Feature: calculating features using orderbook
# -*- coding: utf-8 -*-

import pandas as pd

# features 계산
def cal_feature (gr_bid_level, gr_ask_level):
    
    level = 5 
    ratio = 0.2
    interval = 1
    
    if len(gr_bid_level) > 0 and len(gr_ask_level) > 0:
        bid_top_price = gr_bid_level.iloc[0].price
        bid_top_level_qty = gr_bid_level.iloc[0].quantity
        ask_top_price = gr_ask_level.iloc[0].price
        ask_top_level_qty = gr_ask_level.iloc[0].quantity

        # mid price
        mid_price = (bid_top_price + ask_top_price) * 0.5 

        # mid price wt
        mid_price_wt = ((gr_bid_level.head(level))['price'].mean() + (gr_ask_level.head(level))['price'].mean()) * 0.5

        # mid price mkt
        mid_price_mkt = ((bid_top_price*ask_top_level_qty) + (ask_top_price*bid_top_level_qty))/(bid_top_level_qty+ask_top_level_qty)

        # book imbalance
        quant_v_bid = gr_bid_level.quantity**ratio
        price_v_bid = gr_bid_level.price * quant_v_bid

        quant_v_ask = gr_ask_level.quantity**ratio
        price_v_ask = gr_ask_level.price * quant_v_ask

        askQty = quant_v_ask.values.sum()
        bidPx = price_v_bid.values.sum()
        bidQty = quant_v_bid.values.sum()
        askPx = price_v_ask.values.sum()
        bid_ask_spread = interval

        book_price = 0 #because of warning, divisible by 0
        if bidQty > 0 and askQty > 0:
            book_price = (((askQty*bidPx)/bidQty) + ((bidQty*askPx)/askQty)) / (bidQty+askQty)

        book_imbalance = (book_price - mid_price) / bid_ask_spread

        # order imbalance
        total_bid_Qty = (gr_bid_level.head(level))['quantity'].sum()
        total_ask_Qty = (gr_ask_level.head(level))['quantity'].sum()
        order_imbalance = total_bid_Qty - total_ask_Qty

        return (mid_price, mid_price_wt, mid_price_mkt, book_imbalance, order_imbalance)

    else:
        print ('Error: serious cal_price')
        return (-1, -1, -1, -1, -1)
    
# 오더북 데이터 파일 읽어오기
fn = '2023-11-08-bithumb-BTC-orderbook.csv' # orederbook csv 파일명
df = pd.read_csv(fn).apply(pd.to_numeric,errors='ignore')  
group_o = df.groupby(['timestamp']) # timestamp로 그룹 만들기
# 빈 데이타 프레임 생성
result_df = pd.DataFrame()

# 하나씩 (매초 데이터) 읽어오기
for timestamp, gr_df in group_o:
    gr_bid_level = gr_df[(gr_df.type == 0)]
    gr_ask_level = gr_df[(gr_df.type == 1)]
    mid_price, mid_price_wt, mid_price_mkt, book_imbalance, order_imbalance = cal_feature(gr_bid_level, gr_ask_level)
    # features 계산 후 빈 프레임에 append
    result_df = result_df.append({
        'mid_price': mid_price,
        'mid_price_wt': mid_price_wt,
        'mid_price_mkt': mid_price_mkt,
        'book_imbalance': book_imbalance,
        'order_imbalance': order_imbalance,
        'timestamp': timestamp},
        ignore_index=True
    )

# 열의 순서를 정의
result_df = result_df[['mid_price', 'mid_price_wt', 'mid_price_mkt', 'book_imbalance', 'order_imbalance', 'timestamp']]

file_name = '2023-11-08-bithumb-BTC-feature.csv' # 결과 csv 파일 이름
result_df.to_csv(file_name, mode='a', header=True, index=False)
