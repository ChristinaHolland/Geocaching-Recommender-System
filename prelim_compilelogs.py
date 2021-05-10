# This script runs through the raw csv file, which has a line for each log, 
# and counts to see how many logs there are in each cache.

# Import the basics:
import numpy as np
import pandas as pd

# Read in the raw data -- has a row for each log, therefore several for each unique cache:
df = pd.read_csv('./data/caches_raw.csv')

# Replace null log text values with empty strings:
df['lText'].fillna('',inplace=True)

# Get the names of the caches:
names = list(df['Name'].unique())
num_caches = len(names)

# Initialze data:
compiled_data = []

# Establish bins for aggregating log text:
log_bins = ["good", "neutral", "bad"]
bin_dicts = {}
bin_dicts['good']       = {'type': ["Found it", "Enable Listing", "Will Attend"]
                          }
bin_dicts['neutral']    = {'type': ["Write note", "Owner Maintenance", "Post Reviewer Note", \
                                    "Announcement", "Attended", "Publish Listing", "Webcam Photo Taken", \
                                    "Temporarily Disable Listing", "Update Coordinates", "Unarchive", "Archive"]
                          }
bin_dicts['bad']        = {'type': ["Didn't find it", "Needs Maintenance", "Needs Archived"]}

# Loop over the unique caches:
for n,name in enumerate(names):
    this_cache = df[df['Name']==name]

    # Pull the rows that go with this particular cache:
    this_cache = df[df['Name']==name]                

    # Get all log entries:
    log_types = list(this_cache['lType'])
    log_text  = list(this_cache['lText'])

    #Initialize counters and text fields:
    dict1 = {'good_num'   : 0,
             'neutral_num': 0,
             'bad_num'    : 0,
             'good_txt'   : '',
             'neutral_txt': '',
             'bad_txt'    : ''}

    # Check each log:
    for m,tp in enumerate(log_types):
        txt = log_text[m]

        # Add it to the count and text for 'good', 'neutral', or 'bad':
        for bin_type in log_bins:
            if tp in bin_dicts[bin_type]['type']:
                num_str = bin_type + '_num'
                txt_str = bin_type + '_txt'
                dict1[num_str] += 1
                dict1[txt_str] += ' '
                dict1[txt_str] += txt      

    # Assemble all the variables for this cache as a dictionary, and append to data list:
    compiled_data.append({
            'code':              list(this_cache['Code'])[0],
            'name':              name,
            'good_logs_num':     dict1['good_num'],
            'neutral_logs_num':  dict1['neutral_num'],
            'bad_logs_num':      dict1['bad_num'],
            'good_logs_txt':     dict1['good_txt'],
            'neutral_logs_txt':  dict1['neutral_txt'],
            'bad_logs_txt':      dict1['bad_txt'],
            'creator':           list(this_cache['PlacedBy'])[0],
            'cache_type':        list(this_cache['CacheType'])[0],
            'container':         list(this_cache['Container'])[0],
            'difficulty':        list(this_cache['Difficulty'])[0],
            'terrain':           list(this_cache['Terrain'])[0],
            'latitude':          list(this_cache['Latitude'])[0],
            'longitude':         list(this_cache['Longitude'])[0],
            'placed':            list(this_cache['PlacedDate'])[0],
            'status':            list(this_cache['Status'])[0],
            'is_premium':        list(this_cache['IsPremium'])[0],
            'fav_points':        list(this_cache['FavPoints'])[0],
            'short_description': list(this_cache['ShortDescription'])[0],
            'long_description':  list(this_cache['LongDescription'])[0],
            'hints':             list(this_cache['Hints'])[0],
            'travel_bugs':       list(this_cache['TravelBugs'])[0]  
    })
    
    # Periodically save the new data as a failsafe, and also output current progress:
    if n%50==0:
        new_data_df = pd.DataFrame(compiled_data)
        new_data_df.to_csv('./data/compiled_data.csv',index=False)
        pct_complete = np.round(n*100/num_caches,3)
        print(f'Compiled and saved {n} of {num_caches} caches, {pct_complete}% Complete...')

# Do final save and then message when finished:
new_data_df = pd.DataFrame(compiled_data)
new_data_df.to_csv('./data/compiled_data.csv',index=False)
print()
print(f'Finished! Compiled and saved {num_caches}.')