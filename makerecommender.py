import pandas as pd
import numpy as np

full = pd.read_csv('./data/strippeddata.csv')
df = pd.read_csv('./data/code_name_label.csv')
xy = pd.read_csv('./data/coords.csv')
rec1 = pd.read_csv('./data/recommender1.csv') # based on non-text aspects of the cache, + log sentiment

K0 = '0918273645.1425367.908.9012783465'

KEY = [pd.to_numeric(K0[7] +K0[0] +K0[24] +K0[20]+K0[10]+K0[8]), 
       pd.to_numeric(K0[13]+K0[20]+K0[0]  +K0[24]+K0[10]+K0[13]), 
       pd.to_numeric(K0[23]+K0[24]+K0[20] +K0[0] +K0[22]+K0[29])]

def CoordstoCode(xy_list):
    A = [np.power(xy,0.5) for xy in xy_list]
    c_list = [np.round(KEY[1]+aa) if aa%1>0.5 else np.round(KEY[1]-aa) for aa in A]
    c_list = [int(cc) for cc in c_list]
    return c_list

def OtherInfotoCode(z_list):
    A = [np.power(zz,0.5) for zz in z_list]
    c_list = [np.round(KEY[2]+aa) if aa%1>0.5 else np.round(KEY[2]-aa) for aa in A]
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

full = full[['difficulty', 'terrain', 'size', 'hints', 'is_premium', 'index']]
full['code_index'] = OtherInfotoCode(list(full['index']))
full.drop(columns=['index'],inplace=True)
full = full.sort_values(by='code_index')

ndexs = list(df.index)
codes = list(df['code']) 
code_index = {codes[n]:ndexs[n] for n in range(df.shape[0])}
index_code = {ndexs[n]:codes[n] for n in range(df.shape[0])}

def find_distance(code0,code_recs):
    x0 = list(df[df['code']==code0]['X'])[0]
    y0 = list(df[df['code']==code0]['Y'])[0]
    x = np.array([list(df[df['code']==c]['X'])[0] for c in code_recs]) - x0
    y = np.array([list(df[df['code']==c]['Y'])[0] for c in code_recs]) - y0
    x = (6371*np.cos(y0*np.pi/180)*np.pi/180)*x
    y = (6371*np.pi/180)*y
    distances = np.power((np.power(x,2) + np.power(y,2)),0.5)
    
    return distances

def find_clstr_recs(code):
    cluster = list(df[df['code']==code]['label'])[0]
    code_recs = list(df[df['label']==cluster]['code'])
    code_recs.remove(code)
    name_recs = list([list(df[df['code']==c]['name'])[0] for c in code_recs])
    dist_recs = find_distance(code,code_recs)
    
    N = len(code_recs)
    if N > 5:
        chk = pd.DataFrame({'code': code_recs, 'name': name_recs, 'distance': dist_recs})
        chk = chk.sort_values(by='distance')
        chk = chk[0:5]
        code_recs = list(chk['code'])
        name_recs = list(chk['name'])
        dist_recs  = list(chk['distance'])
  
    return code_recs, name_recs, dist_recs, N

def find_cos_recs(code):
    code_no = str(code_index[code])
    recs = list(rec1[[code_no]].sort_values(by=code_no).index)[1:6]    
    cdis_recs = list(rec1[[code_no]].sort_values(by=code_no)[code_no])[1:6]    
    code_recs = [df['code'][r] for r in recs]
    name_recs = [df['name'][r] for r in recs]
    dist_recs = find_distance(code,code_recs)
    
    return code_recs, name_recs, dist_recs, cdis_recs


def get_params(code_list):
    
    difficulties = []
    terrains     = []
    sizes        = []
    hints        = []
    premiums     = []
    for code in code_list:
        code_no = code_index[code]
        params = list(full.loc[code_no])
        difficulties.append(params[0])
        terrains.append(params[1])
        sizes.append(params[2])
        hints.append(params[3])
        premiums.append(params[4])
        
    return difficulties, terrains, sizes, hints, premiums

def get_kclusters(code,code_list):
    cluster0 = list(df[df['code']==code]['label'])[0]
    clusters = [1 if list(df[df['code']==c]['label'])[0]==cluster0 else 0 for c in code_list]
    return clusters


def get_outpt(code):

    # K means recommendations (0-5):
    code_recsK, name_recsK, dist_recsK, N = find_clstr_recs(code)
    diff_recsK, terr_recsK, size_recsK, hint_recsK, prem_recsK = get_params(code_recsK)
    dist_recsK = list(dist_recsK)

    if N==0:
        outpt = 'You picked a somewhat unusual cache - there are no other caches in our 12000+ within the same KMeans cluster.'
    elif N<=5:
        outpt = 'Here are all of the caches within the same KMeans cluster:'
        outpt+='\n'
        for n in range(N):
            outpt +='\n' + code_recsK[n] + ': ' + name_recsK[n]
    else:         
        outpt = 'There were many caches within the same KMeans cluster, so here are the 5 that are geographically closest:'
        outpt+='\n'
        for n in range(5):
            outpt +='\n' + code_recsK[n] + ': ' + name_recsK[n]
    if N>0:
        outpt+='\n'
        if np.max(diff_recsK)<=3:   outpt+='\nThese are all nice and easy '
        elif np.min(diff_recsK)<=3: outpt+='\nSome of these are higher difficulty '
        else:                       outpt+='\nBetter put on your thinking cap for these tough caches '
        if np.max(terr_recsK)<=3:   outpt+='and the terrain should be not too bad.'
        elif np.min(terr_recsK)<=3: outpt+='and some have some rough terrain.'
        else:                       outpt+='and hiking boots and TecNu may be in order for these.'


    # cos dist recommendations (5):
    code_recs1, name_recs1, dist_recs1, pdis_recs1 = find_cos_recs(code)
    cltr_recs1 = get_kclusters(code,code_recs1)
    diff_recs1, terr_recs1, size_recs1, hint_recs1, prem_recs1 = get_params(code_recs1)
    dist_recs1 = list(dist_recs1)

    outpt+='\n\n'
    outpt+= 'Here are the five caches with the lowest Cosine Distance from your cache. Note that cos dist is always between 0 and 2.'
    outpt+='\n'
    for n in range(5):
        outpt +='\n' + code_recs1[n] + ': ' + name_recs1[n] + ', cos dist = ' + str(np.round(pdis_recs1[n],3))
        if cltr_recs1[n]==1: outpt+= ', also in the same KMeans cluster'

    outpt+='\n'
    if np.max(diff_recs1)<=3:   outpt+='\nThese are all nice and easy '
    elif np.min(diff_recs1)<=3: outpt+='\nSome of these are higher difficulty '
    else:                       outpt+='\nBetter put on your thinking cap for these tough caches '
    if np.max(terr_recs1)<=3:   outpt+='and the terrain should be not too bad.'
    elif np.min(terr_recs1)<=3: outpt+='and some have some rough terrain.'
    else:                       outpt+='and hiking boots and TecNu may be in order for these.'

    outpt+='\n\n'
    outpt+='Thank you, and have fun! Email me at clh@cholland.me if you have any comments or feedback.'


    #print(outpt)
    return outpt



codes = list(df['code'])

output_strings = []
for n,code in enumerate(codes):
    outpt = get_outpt(code)
    output_strings.append(outpt)
    print(f'Cache #{n}: {code}, {n*100/12432}% completed ...')   
    
df['output string'] = output_strings
df.to_csv('./data/recommendations_file.csv',index=False)
