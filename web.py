import yfinance as yf
import pandas as pd
import streamlit as st
import altair as alt
import plotly.express as px

@st.experimental_memo
## FETCHING HISTORIC DATA
def historic_data(stock):
    ticker = yf.Ticker(stock)
    hist = ticker.history(period="max")
    return hist

@st.experimental_memo
## FETCHING COMPANY INFO
def price_info(stock):
    ticker = yf.Ticker(stock)
    return ticker.info


st.header("ticktick.boom")
c1 = st.container()
s = c1.text_input("Enter Stock Ticker", placeholder="Eg. AAPL")
btn = c1.button("Enter")


with st.spinner("Crunching the data..."):
    try:
        if btn:
            df = historic_data(s)
            info = price_info(s)
            col1, col2, col3 = c1.columns(3)
            with col1:
                st.metric(
                    label=info["shortName"],
                    value="%.2f" % info["currentPrice"],
                    delta="%.2f" % (info["currentPrice"] - info["previousClose"]),
                )

            with col2:
                st.metric(label="Today's High", value="%.2f" % info["dayHigh"])

            with col3:
                st.metric(label="Today's Low", value="%.2f" % info["dayLow"])
            
            col6, col7, col8 = c1.columns(3)
            with col6:
                st.metric(
                    label="Revenue Growth (yoy)",
                    value="%.2f" % (info["revenueGrowth"]*100)+"%"
                )

            with col7:
                st.metric(label="PE Ratio", value="%.2f" % info["trailingPE"])

            with col8:
                st.metric(label="PB Ratio", value="%.2f" % info["priceToBook"])

            close_px = df["Close"]
            mavg = close_px.rolling(window=100).mean()
            df["Mavg"] = mavg
            df["datetime"] = pd.to_datetime(df.index)
            df["year"]=df["datetime"].dt.year
            print(df["year"])
            fig = px.line(df, x="datetime",y=["Close","Mavg"])
            c1.plotly_chart(fig,use_container_width=True)
            c1.markdown("### Company Info")
            c1.write(info["longBusinessSummary"])
            

    except:
        c1.markdown(
            '<h3 style="color:red">Incorrect ticker.</h3>', unsafe_allow_html=True
        )


## HIDING THE FOOTER
hide_streamlit_style = """
            <style>
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

