import yfinance as yf
import pandas as pd
import streamlit as st
import plotly.express as px
import pdfkit as pdf
from jinja2 import Environment, select_autoescape, FileSystemLoader

## Setting the page title and favicon
st.set_page_config(
   page_title="ticktick.boom",
   page_icon="💣",
)

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

## MAIN APP
st.title("ticktick.boom") # Title of app
c1 = st.container() # Main container
s = c1.text_input("Enter Stock Ticker", placeholder="Eg. AAPL") # Ticker Input
btn = c1.button("Enter") # Submit button

## SETTING THE FILE PATH FOR PDF TEMPLATE
env = Environment(loader=FileSystemLoader("."), autoescape=select_autoescape())
template = env.get_template("template.html")

## APP LOADING 
with st.spinner("Crunching the data..."):
    try:
        if btn:
            df = historic_data(s) 
            info = price_info(s)

            # Creating 3 columns (Details)
            col1, col2, col3 = c1.columns(3)
            
            # Adding metric components to each column 
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
            
            # Lower columns (Performance Indicators)
            col6, col7, col8 = c1.columns(3)

            # Adding metric components to each column 
            with col6:
                st.metric(
                    label="Revenue Growth (yoy)",
                    value="%.2f" % (info["revenueGrowth"]*100)+"%"
                )
            with col7:
                st.metric(label="PE Ratio", value="%.2f" % info["trailingPE"])
            with col8:
                st.metric(label="PB Ratio", value="%.2f" % info["priceToBook"])

            # Generating Chart
            close_px = df["Close"]
            mavg = close_px.rolling(window=100).mean() # Calculating Moving Average of Stock Close
            df["Mavg"] = mavg
            df["datetime"] = pd.to_datetime(df.index)

            fig = px.line(df, x="datetime",y=["Close","Mavg"]) # Using Plotly Express to create line chart
            c1.plotly_chart(fig,use_container_width=True)

            # Adding Company Business Details
            c1.markdown("### Company Info")
            c1.write(info["longBusinessSummary"])

            # Generating PDF using the template
            html = template.render(
                shortName=info["shortName"],
                currentPrice=info["currentPrice"],
                dayHigh=info["dayHigh"],
                dayLow=info["dayLow"],
                revenueGrowth=info["revenueGrowth"]*100,
                trailingPE=info["trailingPE"],
                priceToBook=info["priceToBook"],
                longBusinessSummary=info["longBusinessSummary"],
            )
            pdf = pdf.from_string(html, False)
            c1.download_button(label="Download",data=pdf,file_name="stock.pdf", mime="application/octet-stream")
            
    except Exception as e:
        c1.markdown(
            '<h3 style="color:red">Incorrect ticker.</h3>', unsafe_allow_html=True
        )
        print(e)


## HIDING THE FOOTER
hide_streamlit_style = """
            <style>
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

