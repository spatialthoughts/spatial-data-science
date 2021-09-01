import streamlit as st
import pandas as pd
import numpy as np
import folium 
from streamlit_folium import folium_static
import webbrowser
import requests
import pickle
import datetime
import os
from IPython.display import display,Javascript
from dotenv import load_dotenv
load_dotenv()
from bokeh.models.widgets import Div
ORS_API_KEY = os.getenv('ORS_API_KEY')


    
categories_to_hour = {
    1: [0, 6],
    2: [7, 9],
    3: [10, 15],
    4: [16, 18],
    5: [19, 23]
}

def get_time_period(hour):
    for category, (start_hour, end_hour) in categories_to_hour.items():
        if hour >= start_hour and hour <= end_hour:
            return category
    
def get_driving_route(source_coordinates, dest_coordinates):
    parameters = {
    'api_key': ORS_API_KEY,
    'start' : '{},{}'.format(source_coordinates[1], source_coordinates[0]),
    'end' : '{},{}'.format(dest_coordinates[1], dest_coordinates[0])
    }

    response = requests.get(
        'https://api.openrouteservice.org/v2/directions/driving-car', params=parameters)

    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print('Request failed.')
        return -9999




def get_route(source, destination, date,departure_time,holiday):
    
    day = date.day
    time_period = get_time_period(departure_time.hour)
    dow = date.weekday()
    driving_data = get_driving_route(source, destination)
    summary = driving_data['features'][0]['properties']['summary']
    distance = summary['distance']
    input = [day, time_period, dow, source[1], source[0], destination[1], destination[0], distance, holiday]
    travel_time = round(regressor.predict([input])[0]/60)
    ors_travel_time = round(summary['duration']/60)
    route= driving_data['features'][0]['geometry']['coordinates']
    
    def swap(coord):
        coord[0],coord[1]=coord[1],coord[0]
        return coord

    route=list(map(swap, route))
    m = folium.Map(location=[(source[0] + destination[0])/2,(source[1] + destination[1])/2], zoom_start=13)
    
    tooltip = 'Model predicted time = {} mins, \
        Default travel time = {} mins'.format(travel_time, ors_travel_time)
    folium.PolyLine(
        route,
        weight=8,
        color='blue',
        opacity=0.6,
        tooltip=tooltip
    ).add_to(m)

    folium.Marker(
        location=(source[0],source[1]),
        icon=folium.Icon(icon='play',color='green')
    ).add_to(m)

    folium.Marker(
        location=(destination[0],destination[1]),
        icon=folium.Icon(icon='stop',color='red')
    ).add_to(m)
    st.write("Expected travel time is: ", travel_time,"minutes")
    folium_static(m)




def run():
    date = st.sidebar.date_input('Select date', datetime.date(2020,1,1))
    time = st.sidebar.time_input('Select time', datetime.time(0))
    dateplustime=datetime.datetime.combine(date,time)
    #seconds=1572926400
    seconds=int((dateplustime-datetime.datetime(1970,1,1)).total_seconds())
    st.write('Date of Journey:',date)
    st.write('Time:',time)
    points=['Select','Point 1','Point 2','Point 3','Point 4', 'Point 5', 'Point 6', 'Point 7','Point 8','Point 9','Point 10' ]
    s_point = st.sidebar.selectbox('Choose the source',points)
    source = coordinate_list.get(s_point)
    st.write('You selected source:', source)
    d_point = st.sidebar.selectbox('Choose the destination',points)
    destination=coordinate_list.get(d_point)
    st.write('You selected destination:', destination)
    
    #url='https://www.google.com/maps/dir/{},{}/{},{}/data=!3m1!4b1!4m5!4m4!2m3!6e0!7e2!8j{}'.format(source[0],source[1],destination[0],destination[1],seconds)

    holiday_check = st.sidebar.checkbox("Holiday")
    if holiday_check:
        holiday=1
    else:
        holiday=0
    departure_time = time
    
    if source != destination:
        col1,col2=st.sidebar.beta_columns(2)
        if col1.button('Navigate'):
            get_route(source, destination, date,departure_time,holiday)
        if col2.button("Google Map"):
                js = "window.open('https://www.google.com/maps/dir/{},{}/{},{}/data=!3m1!4b1!4m5!4m4!2m3!6e0!7e2!8j{}')".format(source[0],source[1],destination[0],destination[1],seconds)  # New tab or window
                #js = "window.location.href = 'https://www.streamlit.io/'"  # Current tab
                html = '<img src onerror="{}">'.format(js)
                div = Div(text=html)
                st.bokeh_chart(div)
           #display(Javascript('window.open("{url}");'.format(url=url)))  
           #webbrowser.open(url)
           
    else:
        st.warning("please choose different source or destination")
     


if __name__ == "__main__":
    # front end elements of the web page 
    html_temp = """ 
    <div style ="background-color:yellow;padding:13px"> 
    <h1 style ="color:black;text-align:center;">Travel Time Predictor app</h1> 
   
    """
      
    # display the front end aspect
    st.markdown(html_temp, unsafe_allow_html = True) 
    city_list=['Bangalore','Hyderabad']
    city=st.sidebar.selectbox('Choose the City',city_list)
    st.write('City: ',city)
    if city=='Bangalore':
        coordinate_list={'Select':'Select','Point 1':(12.946538, 77.579975),'Point 2':(13.04438892,77.60185844),'Point 3':(12.95275348,77.72982887),'Point 4':(12.88962743,77.63661686),
                         'Point 5':(12.95067179,77.75920658),'Point 6':(12.95275348,77.72982887),'Point 7':(12.88243717,77.54024708),'Point 8':(12.8753325,77.54171853),
                         'Point 9':(13.07513833,77.64474206),'Point 10':(13.01596484,77.6713507)}
                         #,(12.87707686,77.512009),(12.89076576,77.50186805),
                         #(13.10954031,77.61893643),(12.99447522,77.60787194),(13.01571239,77.6809775),(12.87034121,77.63979306)]
        pkl_filename = "Est_time_pred.pkl"
    if city=='Hyderabad':
        coordinate_list={'Select':'Select', 'Point 1':(17.4990737222447,78.5484425537565),'Point 2':(17.3228369187765,78.4003341997112),'Point 3':(17.4289313805497,78.3074137286198),
                         'Point 4':(17.5338767879618,78.4312953607305),'Point 5':(17.3858281961646,78.4022854930672),'Point 6':(17.5237690238243,78.5091847750287),
                         'Point 7':(17.4894454531734,78.4112496777986),'Point 8':(17.4308989846564,78.5238677530526),'Point 9':(17.3011570696757,78.4250332621834),
                         'Point 10':(17.4819236326137,78.5411551171801)}
                         #,(17.3227843624735,78.4201698954023),(17.4501231060621,78.3179062429442)]
        pkl_filename = "Est_time_pred_hyd.pkl"
    with open(pkl_filename, 'rb') as file:
        regressor = pickle.load(file)    
    run()

