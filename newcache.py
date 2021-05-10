import streamlit as st
import pickle
import numpy as np
import pandas as pd

st.title('Planning your next geocache placement')

st.header('Welcome Geocachers!!')
st.write('There are so many things to think about as you plan your next cache placement.')
st.write('Obviously it needs to be clever and fun and as water-proof, bug-proof, and muggle-proof as possible, to stand the test of time,')
st.write('but beyond that, how can you know if your cache is going to be popular?')
st.write('')
st.write('This app uses a Random Forest Classifier model, trained on over 12,000 caches in Georgia, to predict FavPoints per cache being at least 2, or less than 2.')
st.write('Of the caches used to train the model, 51.9% of them had 0 or 1 Fav Point, 48.1% had 2 or more.')
st.write('This model has a precision (correct predictions of FP>=2 / all predictions of FP>=2) of 73%, vs. the NULL model at 51.9%')
st.write('')
st.write('This model is highly non-linear and depends on a lot of factors - you may be surprised by the results.')
st.write('')


filename1 = 'modelfornewcaches.sav'
rf = pickle.load(open(filename1, 'rb'))

st.write('')
st.write('Please set your parameters in the sidebar (be sure to scroll to them all), then look below for your prediction.')
diff = st.sidebar.slider('Difficulty Level', min_value=1, max_value=5)
terr = st.sidebar.slider('Terrain Level', min_value=1, max_value=5)
prmm = st.sidebar.radio('Will it be a premium cache?', ['Yes, premium members only', 'No, open to all'])
prmm_dict = {'Yes, premium members only': 1, 'No, open to all': 0}
shds = st.sidebar.radio('Will you have a short description available (in addition to the full long description)?', ['Yes', 'No'])
hint = st.sidebar.radio('Will you include a encrypted hint?', ['Yes', 'No'])
ysno_dict = {'Yes': 1, 'No': 0}
ctype = st.sidebar.radio('What kind of cache is it?', ['Traditional', 'Earth', 'Event', 'LetterboX', 'Lost & Found Event',
                                               'Maze Exhibit', 'Mega Event', 'Multi', 'Mystery', 'Virtual', 'Webcam',
                                               'Whereigo', 'Other/NotListed'])
cntr = 'none/other'
container_caches = ['LetterboX', 'Multi', 'Traditional', 'Mystery', 'Whereigo']
if ctype in container_caches: cntr = st.sidebar.radio('What Kind of Container?', ['micro', 'small', 'regular', 'large', 'none/other'])
size_dict = {'none/other': 0, 'micro': 1, 'small': 2, 'regular': 3, 'large': 4}

ctype_list = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
if ctype=='Earth'             : ctype_list[0] = 1
if ctype=='Event'             : ctype_list[1] = 1
if ctype=='LetterboX'         : ctype_list[2] = 1
if ctype=='Lost & Found Event': ctype_list[3] = 1
if ctype=='Maze Exhibit'      : ctype_list[4] = 1
if ctype=='Mega Event'        : ctype_list[5] = 1
if ctype=='Multi'             : ctype_list[6] = 1
if ctype=='Traditional'       : ctype_list[7] = 1
if ctype=='Mystery'           : ctype_list[8] = 1
if ctype=='Virtual'           : ctype_list[9] = 1
if ctype=='Webcam'            : ctype_list[10]= 1
if ctype=='Wherigo'           : ctype_list[11]= 1

test_model = pd.DataFrame({
    'difficulty'                     : [diff],
    'terrain'                        : [terr],
    'size'                           : [size_dict[cntr]],
    'status'                         : [1],
    'is_premium'                     : [prmm_dict[prmm]],
    'short_description'              : [ysno_dict[shds]],
    'long_description'               : [1],
    'hints'                          : [ysno_dict[hint]],
    'travel_bugs'                    : [0],
    'cache_type_Earth'               : [ctype_list[0]],
    'cache_type_Event'               : [ctype_list[1]],
    'cache_type_LetterboX'           : [ctype_list[2]],
    'cache_type_Lost and Found Event': [ctype_list[3]],
    'cache_type_Maze Exhibit'        : [ctype_list[4]],
    'cache_type_Mega event'          : [ctype_list[5]],
    'cache_type_Multi'               : [ctype_list[6]],
    'cache_type_Traditional'         : [ctype_list[7]],
    'cache_type_Unknown/Mystery'     : [ctype_list[8]],
    'cache_type_Virtual'             : [ctype_list[9]],
    'cache_type_Webcam'              : [ctype_list[10]],
    'cache_type_Wherigo'             : [ctype_list[11]]
})

pred = rf.predict(test_model)
probs = rf.predict_proba(test_model)
probs = 100*np.round(probs[0][1],3)
if probs > 99.9: probs = 99.9

st.header('Your Prediction:')
if pred[0]==0:
    st.write(f'Sorry, a cache with these characteristics will probably NOT reach FavPoints of 2 or more')
    st.write(f'(probability of success={probs}%.)')
    st.write('You can try some other permutations if you want, though!')
else:
    st.write(f'This cache is {probs}% likely to reach at least 2 FavPoints.')
    st.write("So go place it already ... I can't wait to find it.")

st.write('')
st.write('Thank you for using this app! Please email clh@cholland.me if you have any comments or feedback.')
