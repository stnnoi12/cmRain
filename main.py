import streamlit as st
import plotly.express as px
import pandas as pd
from PIL import Image
from  st_aggrid import AgGrid,GridOptionsBuilder
import datetime
import os 
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(page_title='ศูนย์อุทกวิทยาภาคเหนือตอนบน',page_icon=':umbrella_with_rain_drops:',layout='wide')

st.title(':umbrella_with_rain_drops: :blue[ศูนย์อุทกวิทยาภาคเหนือตอนบน]')
# Custom CSS to style the title
#custom_css = """
##<style>
#    .custom-title {
#        color: blue; /* Change to the desired color */
#    }
#    .custom-title::before {
#        content: "\2614"; /* Unicode character for umbrella (replace with the FontAwesome code if using FontAwesome) */
#        margin-right: 10px; /* Adjust as needed for spacing */
#</style>
#"""

# Display the custom CSS
#st.markdown(custom_css, unsafe_allow_html=True)

# Use st.markdown to create a title with a specific class
#st.markdown('<h1 class="custom-title"> ศูนย์อุทกวิทยาภาคเหนือตอนบน</h1>', unsafe_allow_html=True)
st.markdown('<style>div.block-container{padding-top:2rem;}</style>',unsafe_allow_html=True)

col1, col2 = st.sidebar.columns(2)
with col1:
    rd_logo = Image.open('./samplefile/rid-logo.jpeg')
    st.image(rd_logo)
with col2:
    st.header("กรมชลประทาน")

#prepare data
#df = pd.read_csv("C:\Steamlit Dev\samplefile\cmRain.csv")
gsheetid = "1w-QMEvL1FGL2jYx-33rPFKtEetjmk3BgPRbEHoPQEmI"
sheet_name = "Data"
#https://docs.google.com/spreadsheets/d/1w-QMEvL1FGL2jYx-33rPFKtEetjmk3BgPRbEHoPQEmI/edit?usp=sharing
#googleSheetId = '<Google Sheets Id>'
#worksheetName = '<Sheet Name>'
#URL = 'https://docs.google.com/spreadsheets/d/{0}/gviz/tq?tqx=out:csv&sheet={1}'.format(
URL = 'https://docs.google.com/spreadsheets/d/{}/gviz/tq?tqx=out:csv&sheet={}'.format(
	gsheetid,
	sheet_name
)

df = pd.read_csv(URL)

df['Timestamp'] = pd.to_datetime(df['Timestamp'], format='%d/%m/%Y %H:%M:%S')


timeSelect = st.sidebar.radio("เลือกช่วงเวลาที่ต้องการ : ",options=('ตามเวลาจริง','3 วันย้อนหลัง','7 วันย้อนหลัง',
                '15 วันย้อนหลัง','1 เดือน','3 เดือน','6 เดือน','12 เดือน','รายปี'))



if timeSelect == "ตามเวลาจริง":
    #Show Graph 
    st.header(':green[ปริมาณน้ำฝนราย 15 นาที]')
    df.set_index('Timestamp', inplace=True)
    df = df.sort_index()
    eddate = df.index[-1]
    stdate = df.index[-96]
    df1 = df.loc[stdate:eddate]
    df1.reset_index(inplace=True)
    fig = px.bar(df1,x='Timestamp',y='Volume')
    st.plotly_chart(fig,use_container_width=True,height = 200)
    
    #Show Table
    st.header('ตารางแสดงปริมาณน้ำฝน 24 ชม.ที่ผ่านมา ความละเอียด 15 นาที')
    gd=GridOptionsBuilder.from_dataframe(df1)
    gd.configure_pagination(paginationAutoPageSize=False)
    #gd.configure_default_column()
    gridoptions = gd.build()
    AgGrid(df1,gridOptions=gridoptions)
    cmRaincsv=df1.to_csv(index=False)
    st.download_button('ดาวน์โหลดข้อมูล',data=cmRaincsv,file_name='cmRainCSV.csv',mime='text/scv',
        help='กดปุ่มตรงนี้เพื่อดาวน์โหลดข้อมูลในรูปแบบ CSV')

elif timeSelect == '3 วันย้อนหลัง':
    #Show Graph
    st.header('ปริมาณน้ำฝนทุกๆ 1 ชม. ย้อนหลัง 3 วัน')
    df.set_index('Timestamp', inplace=True)
    df = df.sort_index()
    df1 = df.resample('H').sum()
    eddate = df1.index[-1]
    stdate = df1.index[-72]
    df1=df1.loc[stdate:eddate]
    df1.reset_index(inplace=True)
    fig = px.bar(df1,x='Timestamp',y='Volume',
        text=['{:,.2f}'.format(x) for x in df1['Volume']])
    st.plotly_chart(fig,use_container_width=True,height = 200)

    #Show Table
    st.header('ตารางแสดงปริมาณน้ำฝนทุกๆ 1 ชม.ย้อนหลัง 3 วัน')
    gd=GridOptionsBuilder.from_dataframe(df1)
    gd.configure_pagination(paginationAutoPageSize=False)
    #gd.configure_default_column()
    gridoptions = gd.build()
    AgGrid(df1,gridOptions=gridoptions)    
    cmRaincsv=df1.to_csv(index=False)
    st.download_button('ดาวน์โหลดข้อมูล',data=cmRaincsv,file_name='cmRainCSV.csv',mime='text/scv',
        help='กดปุ่มตรงนี้เพื่อดาวน์โหลดข้อมูลในรูปแบบ CSV')

elif timeSelect == '7 วันย้อนหลัง':
    st.header('ปริมาณน้ำฝนรวม 24 ชม. ย้อนหลัง 7 วัน')
    df.set_index('Timestamp', inplace=True)
    df = df.sort_index()
    daily_sum = df.between_time('00:00', '06:59:59').resample('24H').sum()
    daily_sum['night_sum'] = df.between_time('07:00', '23:59:59').resample('24H').sum()['Volume']
    daily_sum['sum'] = daily_sum['night_sum'].add(daily_sum['Volume'].shift(-1))
    eddate = daily_sum.index[-1]
    stdate = daily_sum.index[-7]
    daily_sum=daily_sum.loc[stdate:eddate]
    daily_sum.reset_index(inplace=True)
    fig = px.bar(daily_sum,x='Timestamp',y='sum',
        text=['{:,.2f}'.format(x) for x in daily_sum['sum']])
    st.plotly_chart(fig,use_container_width=True,height = 200)

        #Show Table
    st.header('ตารางแสดงปริมาณน้ำฝนทุกๆ 1 ชม.ย้อนหลัง 3 วัน')
    daily_sum = daily_sum[['Timestamp', 'sum','Volume','night_sum']]
    daily_sum.rename(columns={'sum': 'Total_Volume'}, inplace=True)
    gd=GridOptionsBuilder.from_dataframe(daily_sum)
    gd.configure_pagination(paginationAutoPageSize=False)
    gd.configure_columns(column_names=['Volume','night_sum'],hide='True')
    gridoptions = gd.build()
    AgGrid(daily_sum,gridOptions=gridoptions)    
    cmRaincsv=daily_sum.to_csv(index=False)
    st.download_button('ดาวน์โหลดข้อมูล',data=cmRaincsv,file_name='cmRainCSV.csv',mime='text/scv',
        help='กดปุ่มตรงนี้เพื่อดาวน์โหลดข้อมูลในรูปแบบ CSV')

elif timeSelect == '15 วันย้อนหลัง':
    st.header('ปริมาณน้ำฝนรวม 24 ชม. ย้อนหลัง 15 วัน')
    df.set_index('Timestamp', inplace=True)
    df = df.sort_index()
    daily_sum = df.between_time('00:00', '06:59:59').resample('24H').sum()
    daily_sum['night_sum'] = df.between_time('07:00', '23:59:59').resample('24H').sum()['Volume']
    daily_sum['sum'] = daily_sum['night_sum'].add(daily_sum['Volume'].shift(-1))
    eddate = daily_sum.index[-1]
    stdate = daily_sum.index[-15]
    daily_sum=daily_sum.loc[stdate:eddate]
    daily_sum.reset_index(inplace=True)
    fig = px.bar(daily_sum,x='Timestamp',y='sum',
        text=['{:,.2f}'.format(x) for x in daily_sum['sum']])
    st.plotly_chart(fig,use_container_width=True,height = 200)

    #Show Table
    st.header('ตารางแสดงปริมาณน้ำฝนทุกๆ 1 ชม.ย้อนหลัง 3 วัน')
    daily_sum = daily_sum[['Timestamp', 'sum','Volume','night_sum']]
    daily_sum.rename(columns={'sum': 'Total_Volume'}, inplace=True)
    gd=GridOptionsBuilder.from_dataframe(daily_sum)
    gd.configure_pagination(paginationAutoPageSize=False)
    gd.configure_columns(column_names=['Volume','night_sum'],hide='True')
    gridoptions = gd.build()
    AgGrid(daily_sum,gridOptions=gridoptions)    
    cmRaincsv=daily_sum.to_csv(index=False)
    st.download_button('ดาวน์โหลดข้อมูล',data=cmRaincsv,file_name='cmRainCSV.csv',mime='text/scv',
        help='กดปุ่มตรงนี้เพื่อดาวน์โหลดข้อมูลในรูปแบบ CSV')

elif timeSelect == '1 เดือน':
    st.header('ปริมาณน้ำฝนรวม 24 ชม. ย้อนหลัง 1 เดือน')
    df.set_index('Timestamp', inplace=True)
    df = df.sort_index()
    daily_sum = df.between_time('00:00', '06:59:59').resample('24H').sum()
    daily_sum['night_sum'] = df.between_time('07:00', '23:59:59').resample('24H').sum()['Volume']
    daily_sum['sum'] = daily_sum['night_sum'].add(daily_sum['Volume'].shift(-1))
    eddate = daily_sum.index[-1]
    stdate = daily_sum.index[-30]
    daily_sum=daily_sum.loc[stdate:eddate]
    daily_sum.reset_index(inplace=True)
    fig = px.bar(daily_sum,x='Timestamp',y='sum',
        text=['{:,.2f}'.format(x) for x in daily_sum['sum']])
    st.plotly_chart(fig,use_container_width=True,height = 200)

    #Show Table
    st.header('ตารางแสดงปริมาณน้ำฝนทุกๆ 1 ชม.ย้อนหลัง 3 วัน')
    daily_sum = daily_sum[['Timestamp', 'sum','Volume','night_sum']]
    daily_sum.rename(columns={'sum': 'Total_Volume'}, inplace=True)
    gd=GridOptionsBuilder.from_dataframe(daily_sum)
    gd.configure_pagination(paginationAutoPageSize=False)
    gd.configure_columns(column_names=['Volume','night_sum'],hide='True')
    gridoptions = gd.build()
    AgGrid(daily_sum,gridOptions=gridoptions)    
    cmRaincsv=daily_sum.to_csv(index=False)
    st.download_button('ดาวน์โหลดข้อมูล',data=cmRaincsv,file_name='cmRainCSV.csv',mime='text/scv',
        help='กดปุ่มตรงนี้เพื่อดาวน์โหลดข้อมูลในรูปแบบ CSV')

elif timeSelect == '3 เดือน':
    st.header('ปริมาณน้ำฝนรายเดือน ย้อนหลัง 3 เดือน')
    df.set_index('Timestamp', inplace=True)
    df = df.sort_index()
    daily_sum = df.between_time('00:00', '06:59:59').resample('24H').sum()
    daily_sum['night_sum'] = df.between_time('07:00', '23:59:59').resample('24H').sum()['Volume']
    daily_sum['sum'] = daily_sum['night_sum'].add(daily_sum['Volume'].shift(-1))
    daily_sum.tail()
    daily_sum = daily_sum.resample('M').sum()
    eddate = daily_sum.index[-1]
    stdate = daily_sum.index[-3]
    daily_sum=daily_sum.loc[stdate:eddate]
    daily_sum.reset_index(inplace=True)
    daily_sum['Monthly']=daily_sum['Timestamp'].dt.to_period('M')
    daily_sum['Monthly']=daily_sum['Monthly'].astype(str)
    fig = px.bar(daily_sum,x='Monthly',y='sum',
        text=['{:,.2f}'.format(x) for x in daily_sum['sum']])
    fig.update_xaxes(tickformat='%B-%Y',dtick="M1")
    st.plotly_chart(fig,use_container_width=True,height = 200)

    #Show Table
    st.header('ตารางแสดงปริมาณน้ำฝนทุกๆ 1 ชม.ย้อนหลัง 3 วัน')
    daily_sum = daily_sum[['Monthly', 'sum', 'Timestamp','Volume','night_sum']]
    daily_sum.rename(columns={'sum': 'Total_Volume'}, inplace=True)
    gd=GridOptionsBuilder.from_dataframe(daily_sum)
    gd.configure_pagination(paginationAutoPageSize=False)
    gd.configure_columns(column_names=['Timestamp','Volume','night_sum'],hide='True')
    gridoptions = gd.build()
    AgGrid(daily_sum,gridOptions=gridoptions)    
    cmRaincsv=daily_sum.to_csv(index=False)
    st.download_button('ดาวน์โหลดข้อมูล',data=cmRaincsv,file_name='cmRainCSV.csv',mime='text/scv',
        help='กดปุ่มตรงนี้เพื่อดาวน์โหลดข้อมูลในรูปแบบ CSV')

elif timeSelect == '6 เดือน':
    st.header('ปริมาณน้ำฝนรายเดือน ย้อนหลัง 6 เดือน')
    df.set_index('Timestamp', inplace=True)
    df = df.sort_index()
    daily_sum = df.between_time('00:00', '06:59:59').resample('24H').sum()
    daily_sum['night_sum'] = df.between_time('07:00', '23:59:59').resample('24H').sum()['Volume']
    daily_sum['sum'] = daily_sum['night_sum'].add(daily_sum['Volume'].shift(-1))
    daily_sum.tail()
    daily_sum = daily_sum.resample('M').sum()
    eddate = daily_sum.index[-1]
    stdate = daily_sum.index[-4]  #ไว้เปลี่ยนช่วงเวลาตรงนี้
    daily_sum=daily_sum.loc[stdate:eddate]
    daily_sum.reset_index(inplace=True)
    daily_sum['Monthly']=daily_sum['Timestamp'].dt.to_period('M')
    daily_sum['Monthly']=daily_sum['Monthly'].astype(str)
    fig = px.bar(daily_sum,x='Monthly',y='sum',
        text=['{:,.2f}'.format(x) for x in daily_sum['sum']])
    fig.update_xaxes(tickformat='%B-%Y',dtick="M1")
    st.plotly_chart(fig,use_container_width=True,height = 200)

    #Show Table
    st.header('ตารางแสดงปริมาณน้ำฝนรายเดือน ย้อนหลัง 6 เดือน')
    daily_sum = daily_sum[['Monthly', 'sum', 'Timestamp','Volume','night_sum']]
    daily_sum.rename(columns={'sum': 'Total_Volume'}, inplace=True)
    gd=GridOptionsBuilder.from_dataframe(daily_sum)
    gd.configure_pagination(paginationAutoPageSize=False)
    gd.configure_columns(column_names=['Timestamp','Volume','night_sum'],hide='True')
    gridoptions = gd.build()
    AgGrid(daily_sum,gridOptions=gridoptions)    
    cmRaincsv=daily_sum.to_csv(index=False)
    st.download_button('ดาวน์โหลดข้อมูล',data=cmRaincsv,file_name='cmRainCSV.csv',mime='text/scv',
        help='กดปุ่มตรงนี้เพื่อดาวน์โหลดข้อมูลในรูปแบบ CSV')

elif timeSelect == '12 เดือน':
    st.header('ปริมาณน้ำฝนรายเดือน ย้อนหลัง 12 เดือน')
    df.set_index('Timestamp', inplace=True)
    df = df.sort_index()
    daily_sum = df.between_time('00:00', '06:59:59').resample('24H').sum()
    daily_sum['night_sum'] = df.between_time('07:00', '23:59:59').resample('24H').sum()['Volume']
    daily_sum['sum'] = daily_sum['night_sum'].add(daily_sum['Volume'].shift(-1))
    daily_sum.tail()
    daily_sum = daily_sum.resample('M').sum()
#    eddate = daily_sum.index[-1]
#    stdate = daily_sum.index[-12]  #ไว้เปลี่ยนช่วงเวลาตรงนี้เป็น 12
#    daily_sum=daily_sum.loc[stdate:eddate]
    daily_sum.reset_index(inplace=True)
    daily_sum['Monthly']=daily_sum['Timestamp'].dt.to_period('M')
    daily_sum['Monthly']=daily_sum['Monthly'].astype(str)
    fig = px.bar(daily_sum,x='Monthly',y='sum',
        text=['{:,.2f}'.format(x) for x in daily_sum['sum']])
    fig.update_xaxes(tickformat='%B-%Y',dtick="M1")
    st.plotly_chart(fig,use_container_width=True,height = 200)

    #Show Table
    st.header('ตารางแสดงปริมาณน้ำฝนรายเดือน ย้อนหลัง 12 เดือน')
    daily_sum = daily_sum[['Monthly', 'sum', 'Timestamp','Volume','night_sum']]
    daily_sum.rename(columns={'sum': 'Total_Volume'}, inplace=True)
    gd=GridOptionsBuilder.from_dataframe(daily_sum)
    gd.configure_pagination(paginationAutoPageSize=False)
    gd.configure_columns(column_names=['Timestamp','Volume','night_sum'],hide='True')
    gridoptions = gd.build()
    AgGrid(daily_sum,gridOptions=gridoptions)    
    cmRaincsv=daily_sum.to_csv(index=False)
    st.download_button('ดาวน์โหลดข้อมูล',data=cmRaincsv,file_name='cmRainCSV.csv',mime='text/scv',
        help='กดปุ่มตรงนี้เพื่อดาวน์โหลดข้อมูลในรูปแบบ CSV')

else:
    st.header('ปริมาณน้ำฝนรายปี')
    df.set_index('Timestamp', inplace=True)
    df = df.sort_index()
    daily_sum = df.between_time('00:00', '06:59:59').resample('24H').sum()
    daily_sum['night_sum'] = df.between_time('07:00', '23:59:59').resample('24H').sum()['Volume']
    daily_sum['sum'] = daily_sum['night_sum'].add(daily_sum['Volume'].shift(-1))
    daily_sum.tail()
    daily_sum = daily_sum.resample('Y').sum()
    daily_sum.reset_index(inplace=True)
    daily_sum['Year']=daily_sum['Timestamp'].dt.to_period('Y')
    daily_sum['Year']=daily_sum['Year'].astype(str)
    fig = px.bar(daily_sum,x='Year',y='sum',
        text=['{:,.2f}'.format(x) for x in daily_sum['sum']])
    fig.update_xaxes(tickformat='%Y',dtick="M1")
    st.plotly_chart(fig,use_container_width=True,height = 200)
    
    #Show Table
    st.header('ตารางแสดงปริมาณน้ำฝนทุกๆ 1 ชม.ย้อนหลัง 3 วัน')
    daily_sum = daily_sum[['Year', 'sum', 'Timestamp','Volume','night_sum']]
    daily_sum.rename(columns={'sum': 'Total_Volume'}, inplace=True)
    gd=GridOptionsBuilder.from_dataframe(daily_sum)
    gd.configure_pagination(paginationAutoPageSize=False)
    gd.configure_columns(column_names=['Timestamp','Volume','night_sum'],hide='True')
    gridoptions = gd.build()
    AgGrid(daily_sum,gridOptions=gridoptions)    
    cmRaincsv=daily_sum.to_csv(index=False)
    st.download_button('ดาวน์โหลดข้อมูล',data=cmRaincsv,file_name='cmRainCSV.csv',mime='text/scv',
        help='กดปุ่มตรงนี้เพื่อดาวน์โหลดข้อมูลในรูปแบบ CSV')

