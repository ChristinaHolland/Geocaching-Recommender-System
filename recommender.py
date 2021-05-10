
# imports:
import streamlit as st
import pandas as pd
import numpy as np

# load in datasets:
df = pd.read_csv('./data/code_name_label.csv')
xy = pd.read_csv('./data/coords.csv')
recs = pd.read_csv('./data/recommendations_file.csv') 

# get data organized:

K0 = '0918273645.1425367.908.9012783465'

KEY = [pd.to_numeric(K0[7] +K0[0] +K0[24] +K0[20]+K0[10]+K0[8]), 
       pd.to_numeric(K0[13]+K0[20]+K0[0]  +K0[24]+K0[10]+K0[13]), 
       pd.to_numeric(K0[23]+K0[24]+K0[20] +K0[0] +K0[22]+K0[29])]

def CoordstoCode(xy_list):
    A = [np.power(xy,0.5) for xy in xy_list]
    c_list = [np.round(KEY[1]+aa) if aa%1>0.5 else np.round(KEY[1]-aa) for aa in A]
    c_list = [int(cc) for cc in c_list]
    return c_list

xy['code_index'] = CoordstoCode(list(xy['coords_index']))
xy = xy.sort_values(by='code_index')

df['Y'] = xy['latitude']
df['X'] = xy['longitude']

y_min = df['Y'].min()
y_max = df['Y'].max()
x_min = df['X'].min()
x_max = df['X'].max()

ndexs = list(df.index)
codes = list(df['code']) 
code_index = {codes[n]:ndexs[n] for n in range(df.shape[0])}
index_code = {ndexs[n]:codes[n] for n in range(df.shape[0])}


# GET STARTING CACHE CODE:

# START User input: (1) enter code, (2) enter name (or partial), (3) enter latitude and longitude
# (1) If user selects to enter code: have them enter it
#     (1A)    If the code is in the database, return code
#     (1B)    If not, prompt them to retype or start over entirely
#             (1B-i)          If they choose to retype, go back to (1)
#             (1B-ii)         If they choose to start over, go back to START
# (2) If user selects to enter name: have them enter it
#     (2A)    Show the user the 4 names closest to what they typed (alphabetically), and 
#             allow them to choose one of them, retype, or choose start over entirely.
#             (2A-i)            If they choose a specific cache, return code
#             (2A-ii)           If they choose to retype, go back to (2)
#             (2A-iii)          If they choose to start over, go back to START
# (3) If user selects to enter latitude & longitude: have them enter it
#     (3A)    Show the user the 4 names closest to what they typed (geographically), and 
#             allow them to choose one of them, retype, or choose start over entirely.
#             (3A-i)            If they choose a specific cache, return code
#             (3A-ii)           If they choose to retype, go back to (3)
#             (3A-iii)          If they choose to start over, go back to START

codes = list(df['code'])
names = list(df['name'])
names = [name.upper() for name in names]

# SIDE BAR: USER SELECTS STARTING CACHE TO BASE RECOMMENDATIOS ON:

search_parameter = 'Unknown'
code0 = 'Unknown'
name0 = 'Unknown'
lat0 = 0
lon0 = 0
code = 'Unknown' # The cache code on which the recommendation will be made

# They can select by cache code, cache name, or by latitude and longitude:
if search_parameter=='Unknown':
    st.sidebar.header('How would you like to choose your starting point?')
    search_parameter = st.sidebar.radio('Select one:', 
                                    ['By Geo Code (GCXXXXX)', 'By Name', 'By Coordinates'])

# If they choose to select by cache code:
if search_parameter=='By Geo Code (GCXXXXX)':
    
    # Let them try typing in a code; prompt to retry if needed 
    # They can also go back up and select one of the other two methods.
    if code0=='Unknown':
        code0 = st.sidebar.text_input('Please input the code, starting with G:', value="GCXXXXX")
        if code0 in codes:
            code = code0
        else:
            st.sidebar.write('Sorry, that cache is not in the dataset, please retry.')

# If they choose to select by typing a name:
if search_parameter=='By Name':
    
    if name0=='Unknown':
        name0 = st.sidebar.text_input('Please type in what you can of the cache name:')
        name0 = name0.upper()
        
        # If they typed the full name perfectly, select the cache and find the cache code
        if name0 in names:
            ndx = names.index(name0)
            code = codes[ndx]
        
        # If they typed the name incorrecly, or not the complete name, offer them the 4 closest
        # matches, alpabetically. 
        else:
            names1 = names.copy()
            names1.append(name0)
            names1.sort()
            n = names1.index(name0)
            n_list = list(range(5))
            if n>2: 
                n_list = [(j + n - 2) for j in n_list]
            if len(names1)-n < 3:
                n_list = [len(names1)+j for j in list(range(-5,0))]
            names4closest = [names1[j] for j in n_list]
            names4closest.remove(name0)
            options = names4closest
            retry1 = st.sidebar.radio('Which cache did you mean? (or retry)', options)
            
            # If they choose one of the 4 selections, select the cache and get the cache code
            # They can also try tying in a different name or selecting the cache by code or lat,lon
            if retry1 in names4closest:
                ndx = names.index(retry1)
                code = codes[ndx]

# If they choose to select the cache by lat, lon coordinates:
if search_parameter=='By Coordinates':

    # Prompt to input a latitude and longitude:
    if lat0+lon0==0:
        lat0str = st.sidebar.text_input('Please input a decimal latitude value between 30 and 36 (north latitude)')
        lon0str = st.sidebar.text_input('Please input a decimal longitude value between -87 and -81 (west longitude is negative)')
        
        # Find the 4 caches in the data that are geographically closest to the input lat, lon:
        lat0 = pd.to_numeric(lat0str)
        lon0 = pd.to_numeric(lon0str)
        # All available lat,lon values:
        lats = list(df['Y'])
        lons = list(df['X'])
        # Subtract the input lat, lon.
        # The delta lon is also multiplied by the cosine of the latitude, 
        #    so that distance can be calculated in km on a spherical Earth.
        lats = [(lat-lat0) for lat in lats]
        lons = [np.cos(lat0*np.pi/180)*(lon-lon0) for lon in lons]
        # Distance by Pythagorean theorem:
        dist = [(6371*np.pi/180)*(lons[j]**2 + lats[j]**2)**0.5 for j in range(df.shape[0])]
        # Make a temporary pandas dataframe, sort by distance, and select the closest 4 caches:
        tempdf = pd.DataFrame({'ndex': list(df.index), 'dist': dist, 'code': codes, 'name': names})       
        tempdf = tempdf.sort_values(by='dist')
        tempdf = tempdf[0:4]
        codes1 = list(tempdf['code'])
        names1 = list(tempdf['name'])
        
        # Present the closest 4 caches (geographically) and prompt user to select one.
        # If they choose one of the 4 selections, select the cache and get the cache code
        # They can also try tying in a different lat,lon or selecting the cache by code or name.
        options = [codes1[j]+': '+names1[j] for j in range(4)]
        retry1 = st.sidebar.radio('Which cache did you mean? (or retry)', options) 
        if retry1 in options:
            code = codes1[options.index(retry1)]
        
st.sidebar.write('Current starting cache code:' + code)
st.sidebar.write()
st.sidebar.write('You can change this at any time.')

# MAIN PAGE: TOGGLE BETWEEN RECOMMENDATION OUTPUT AND "ABOUT THE APP"

data_list = ['CACHE TYPE and CONTAINER SIZE (if there is a container)']
data_list.append('DIFFICULTY and TERRAIN ratings')
data_list.append('WHEN it was placed, WHO placed it, and whether it is listed as ACTIVE')
data_list.append('Whether it has a SHORT DESCRIPTION as well as a LONG DESCRIPTION')
data_list.append('Whether it has a HINT')
data_list.append('Whether it is PREMIUM access only or open to all cachers')
data_list.append('How often it has been FAVORITED')
data_list.append('Whether is has ever had TRAVEL BUGS in it')
data_list.append('The frequency of each TYPE of logs left ("found it", "needs maintenence", ...)')
data_list.append('The composite SENTIMENT of recent logs (used VADER sentiment analysis)')
data_table_df = pd.DataFrame({'Cache parameters used to form the recommendations:': data_list})

# User can choose what they want to view:
st.header('YourNextGeocache: A recommender app for avid geocachers\n')
st.write('')

disp_mode = st.sidebar.radio('Please select what you would like to do now:', 
                                    ['Get Cache Recommendations', 'Learn More About This App'])

st.write()

# If they want to see the recommendations, show them:

start_options = []
start_options.append('You picked a somewhat unusual cache - there are no other caches in our 12000+ within the same KMeans cluster.')
start_options.append('Here are all of the caches within the same KMeans cluster:\n')
start_options.append('There were many caches within the same KMeans cluster, so here are the 5 that are geographically closest:\n')

mid_options = []
mid_options.append('\nThese are all nice and easy and the terrain should be not too bad.')
mid_options.append('\nThese are all nice and easy and some have some rough terrain.')
mid_options.append('\nThese are all nice and easy and hiking boots and TecNu may be in order for these.')
mid_options.append('\nSome of these are higher difficulty and the terrain should be not too bad.')
mid_options.append('\nSome of these are higher difficulty and some have some rough terrain.')
mid_options.append('\nSome of these are higher difficulty and hiking boots and TecNu may be in order for these.')
mid_options.append('\nBetter put on your thinking cap for these tough caches and the terrain should be not too bad.')
mid_options.append('\nBetter put on your thinking cap for these tough caches and some have some rough terrain.')
mid_options.append('\nBetter put on your thinking cap for these tough caches and hiking boots and TecNu may be in order for these.')

part2 =  '\n\nHere are the five caches with the lowest Cosine Distance from your cache. Note that cos dist is always between 0 and 2.\n'

ending = '\n\nThank you, and have fun! Email me at clh@cholland.me if you have any comments or feedback.'


if disp_mode == 'Get Cache Recommendations':
    
    if code in codes:
        
        st.write('')
        st.write('Here are the recommended caches, if you liked ' + code)
        ndx = list(recs[recs['code']==code]['startoption'])[0]
        st.write(start_options[ndx])
        ndx = list(recs[recs['code']==code]['num KM'])[0]
        if ndx > 0: cachelist = [list(recs[recs['code']==code]['KMcache0'])[0]]
        if ndx > 1: cachelist.append(list(recs[recs['code']==code]['KMcache1'])[0])
        if ndx > 2: cachelist.append(list(recs[recs['code']==code]['KMcache2'])[0])
        if ndx > 3: cachelist.append(list(recs[recs['code']==code]['KMcache3'])[0])
        if ndx > 4: cachelist.append(list(recs[recs['code']==code]['KMcache4'])[0])
        if ndx > 0:
            cache_table_df = pd.DataFrame({'KMeans Cluster Recommendations:': cachelist})
            st.table(cache_table_df)
            ndx1 = list(recs[recs['code']==code]['KMtxtoption'])[0]
            st.write(mid_options[ndx1])
            st.write('')
        st.write(part2)
        cachelist = [list(recs[recs['code']==code]['CDcache0'])[0]]
        cachelist.append(list(recs[recs['code']==code]['CDcache1'])[0])
        cachelist.append(list(recs[recs['code']==code]['CDcache2'])[0])
        cachelist.append(list(recs[recs['code']==code]['CDcache3'])[0])
        cachelist.append(list(recs[recs['code']==code]['CDcache4'])[0])
        cache_table_df = pd.DataFrame({'Cosine Distance Recommendations:': cachelist})
        st.table(cache_table_df)
        ndx = list(recs[recs['code']==code]['CDtxtoption'])[0]
        st.write(mid_options[ndx])
        st.write(ending)
        st.write('Please use the sidebar if you want to change your starting cache.')
    
    else:
        
        st.header('(Please use the sidebar to select a starting cache)')

# If they want to know more about the app, give them the details:

if disp_mode == 'Learn More About This App':
    
    # What is it?
    st.write("This app was created as part of a final 'capstone' project in my General Assembly Data Science Immersive course. You give it a starting cache, and it gives you 5-10 caches you'll hopefully enjoy. I hope you like it!")
    st.write()
    # What do I do?
    st.write("When you're ready to begin, choose a starting cache (one you like!) from the sidebar.")

    # Data:
    st.write('Geocache data were obtained using the Geocaching Swiss Army Knife tool (GSAK.net), and my geocaching.com login. For now, this app includes 12,432 caches covering the state of Georgia (where I live), from data pulled in late April of 2021. It is intended mainly as a proof of concept, which could be expanded geographically and kept up to date, given additional resources.')

    st.table(data_table_df)

    # How does it work?
    st.write('Recommendations are based on two basic algorithms: KMeans Cluster analyis and Cosine Distance minimization. The top five results from each of these two analyses are shown in the end recommendation, giving you up to 10 caches that you will hopefully really like.')
        
    st.write()

    st.write('Thank you, and have fun! Email me at clh@cholland.me if you have any comments or feedback.')
    
    