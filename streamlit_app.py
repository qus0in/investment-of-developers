from datetime import datetime
import streamlit as st
import yfinance as yf
import plotly.graph_objects as go

# 주식 가격 데이터를 가져오는 함수입니다. 
# Streamlit의 캐싱 기능을 사용하여 10분 동안 데이터를 캐시합니다.
@st.cache_data(ttl=600)
def get_history(ticker):
    return yf.Ticker(ticker).history(period='max')

# 주식 가격 차트를 생성하는 함수입니다.
def get_chart():
    # 사용자가 입력한 주식 종목 코드와 시작일을 가져옵니다.
    ticker = st.session_state.ticker
    sd = datetime.strftime(st.session_state.sd, '%Y-%m-%d')
    # 주식 가격 데이터를 가져옵니다.
    df = get_history(ticker).loc[sd:]

    # Plotly를 사용하여 캔들스틱 차트를 생성합니다.
    fig = go.Figure(data=[go.Candlestick(x=df.index,
                    open=df['Open'], high=df['High'],
                    low=df['Low'], close=df['Close'])])

    # 차트 레이아웃을 설정합니다.
    fig.update_layout(
        width=1200, height=600,
        title=f'{ticker}, {sd} ~',
        xaxis_rangeslider_visible=False)
    return fig

# 웹 앱의 제목을 설정합니다.
st.title('📌 240215_note_01_가격분석')

# 사용자에게 주식 종목 코드와 시작일을 입력받습니다.
st.text_input('종목코드 입력', 'MSFT', key='ticker')
st.date_input('시작일 입력', datetime.strptime('2022-02-01', '%Y-%m-%d'), key='sd', format='YYYY-MM-DD')

# 차트를 생성하고 웹 앱에 표시합니다.
chart = get_chart()
st.plotly_chart(chart, use_container_width=True)