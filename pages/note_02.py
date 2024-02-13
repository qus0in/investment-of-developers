import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go

@st.cache_data(ttl=600)
def get_history(ticker):
    df = yf.Ticker(ticker).history(period='max')
    df.index = pd.to_datetime(df.index.date)
    return df

def backtest(history, sd=None):
    df = history.copy()
    if sd:
        df = df.loc[sd:]
    tmp = pd.DataFrame()
    tmp['Price'] = df.resample('MS').Close.last()
    tmp['Dividends'] = df.resample('MS').Dividends.sum()
    tmp['Change'] = tmp.Price.pct_change()
    tmp['Yearly'] = 0
    tmp['Monthly'] = 0
    tmp['Lump'] = len(tmp) * 100
    tmp.iloc[0, 3] = 1200
    tmp.iloc[0, 4] = 100
    for i in range(1, len(tmp)):
        for j in range(3, 6):
            tmp.iloc[i, j] = tmp.iloc[i-1, j] * (1 + tmp.iloc[i, 2])
        if i % 12 == 0:
            tmp.iloc[i, 3] += 1200
        tmp.iloc[i, 3] += tmp.iloc[i, 1] / tmp.iloc[i, 0] * tmp.iloc[i, 3]
        tmp.iloc[i, 4] += tmp.iloc[i, 1] / tmp.iloc[i, 0] * tmp.iloc[i, 4]
        tmp.iloc[i, 5] += tmp.iloc[i, 1] / tmp.iloc[i, 0] * tmp.iloc[i, 5]
        tmp.iloc[i, 4] += 100
    tmp['Yearly_DD'] = 1 - tmp['Yearly'] / tmp['Yearly'].cummax()
    tmp['Monthly_DD'] = 1 - tmp['Monthly'] / tmp['Monthly'].cummax()
    tmp['Lump_DD'] = 1 - tmp['Lump'] / tmp['Lump'].cummax()
    return tmp

def draw_dd(df, ticker, col1, col2, sd=None):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df[f'{col1}_DD'], name=col1))
    fig.add_trace(go.Scatter(x=df.index, y=df[f'{col2}_DD'], name=col2))
    fig.update_layout(
        width=1200, height=600,
        title= ticker + (f' ({sd} ~ )' if sd else '(Total)') + f' : {col1} vs {col2}')
    # fig.show()
    return fig

def draw_chart(ticker, sd=None):
    history = get_history(ticker)
    tested = backtest(history, sd)
    # draw_dd(tested, ticker, 'Lump', 'Yearly', sd)
    return draw_dd(tested, ticker, 'Lump', 'Monthly', sd)

st.title('📌 240215_note_02')
st.text_input('종목코드 입력', 'SPY', key='ticker')
st.date_input('시작일 입력', pd.to_datetime('2019-01-01'), key='sd', format='YYYY-MM-DD')
chart = draw_chart(st.session_state.ticker, st.session_state.sd)
st.plotly_chart(chart, use_container_width=True)
chart = draw_chart(st.session_state.ticker)
st.plotly_chart(chart, use_container_width=True)