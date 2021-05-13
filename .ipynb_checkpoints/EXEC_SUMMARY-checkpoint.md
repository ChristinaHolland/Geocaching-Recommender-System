# YourNextGeocache: A recommender app for avid geocachers

## Christina Holland

### Problem Statement: How should you pick your next cache?

My objective is to create a "content-based" recommender system for geocaches. For a geocacher using my app, they will get results something like: "If you liked GC47X42 'That Really Big Tree', then you'll probably enjoy ...."

#### Why is this needed?

This is designed for anyone who enjoys geocaching! My father & step-mom, my husband and myself are all geocachers. There are MILLIONS of caches world-wide. When I log in, I see 228 caches within 3.5 miles of my house. How should I decide where to go? Existing filters on geocaching.com are inadequate, and new caches are showing up all the time. This recommender app aims to solve this problem. If successful (and with full access to ALL the global data, far beyond the current scope of this project), geocaching.com could implement this app into their platform, to improve the experience for everyone within the geocaching community.

#### Questions Addressed:

The primary question is, what features of a geocache are most important for people's enjoyment? This will be addressed in two phases:

1. Predictive modeling of cache popularity. This is the supervised learning phase, using a variety of classification models. The target variable is "FavPoints", the number of times a cache has been favorited. This variable has been binarized, with "1" being 2 or more favpoints and "0" being 1 or no favpoints. This split leads to very balanced classes.

2. Recommender system for individual cachers to find caches they would like, based on a cache they already know they like. This analysis will use both clustering (KMeans and DBSCAN) and vector cosin similarity / cosine distance.


## SUMMARY

### [Data Acquisition and Cleaning is Summarized in the README.md](README.md)

| Data Grid Overlay | Cache Locations |
|---|---|
|<img src="./6_Notes_and_Images/assets/GAdatamap.png" alt="map" width="600"/>|<img src="./6_Notes_and_Images/assets/cachedata.png" alt="map" width="600"/>|

### Predictive Modeling of Popularity

Before beginning cluster analysis and cosine similarity analysis for a geocache recommender, I decided to do supervised learning as a preliminary step to see the relationships between the variables.

My target variable is "FavPoints", binarized to 1 if FP>=2, and 0 if FP is 0 or 1.

I initially used 4 different sets of features:
1. numerical, binary, and dummified categorical data only
2. numerical, binary, and dummified categorical data + sentiment of the cache's log corpus
3. count vectorization of the caches text name+description+hint, minus english stop words and words like "geocache"
4. set 2, + binary columns for the 10 most influential words, favorable and unfavorable, from the analysis of set 3

I tested the following models with default parameters:
1. Log Regression
2. KNeighborsClassifier
3. DecisionTreeClassifier
4. RandomForestClassifier
5. BaggingClassifier
6. AdaBoostClassifier
7. SVC

<img src="./6_Notes_and_Images/assets/model_comparison1.png" alt="map" width="600"/>

By 3 out of 4 measures (accuracy, recall, and f1-score), the best model is the random forest model using all of the data EXCEPT the cache text. It also comes out 2nd overall in precision. The winner on precision, SVC with the cache text only, does MUCH worse in all other measures.

So, I focused on refining the random forest model with a subset of those features, and use that for my streamlit app.

I want to see if I can achieve similar accuracy WITHOUT the creator input or the log sentiment, or latitude and longitude, since I would like to aim the streamlit app at cachers setting up a cache -- to help them see how to make a successful cache that earns favpoints.

<img src="./6_Notes_and_Images/assets/model_comparison2.png" alt="map" width="600"/>

Okay, time to think about the goal, and what metric to choose: If this app is to be aimed at cachers placing a new cache, then false positives are worse than false negatives. I want to be sure that if I'm telling them they are likely to succeed, that I am giving them accurate information.

This means I should be looking at precision.

The best RF model for precision had 50 estimators and a max depth of 20.It suffers a bit on recall compared to the other values of the hyperparameters, but that is less of a concern. The accuracy and f1-score are very close to the other models as well.

I also tried to build a neural net, but the precision in my best neural net only improved over this random forest model by less than a percent. So for interpretability and for ease of app deployment I am sticking with this model.

I have an app on streamlit, deployed at:
https://share.streamlit.io/christinaholland/cachepopularitypredictor/main/newcache.py

This app is aimed at any geocacher who is hoping to place a new cache that will be popular (as measured by 2 or more FavPoints). In contrast, I will later be deploying an app based on the recommender systems, aimed at geocachers trying to decide which cache to visit next.

Here are a couple screenshots of this first app:

| Prediction: POPULAR | Prediction: NOT POPULAR |
|---|---|
|<img src="./6_Notes_and_Images/assets/placementapp1.png" width="600"/> |<img src="./6_Notes_and_Images/assets/placementapp2.png" width="600"/>   |

### Cluster Analysis KMeans

Searching over k, k=50 produced maximum silhouette and the "elbow bend" in inertia.

Only 3 of the 50 clusters were single cache clusters. The median size is 86, with 50% of the clusters having between 56 and 173 caches, and the largest clusters being cluster 0 (2908), cluster 40 (1406), and cluster 2 (965).

### Cluster Analysis DBSCAN

The DBSCAN clusters match well with KMeans. For all parameter values tested, the DBSCAN clusters were almost exclusively single KMeans Labels. Of course, many of them have a lot more clusters than kmeans did, which means this method is further dividing some of those clusters.

Manual gridsearch over eps_list = [1, 2, 3, 4, 5] and n_list = [2, 3, 4, 5, 10],

then over eps_list = [5, 6, 8, 10], n_list = [2, 3, 4, 5, 6, 7, 8, 9, 10, 20]

Selected eps = 5 and min_samples = 2 on the basis of maximum silhouette and minimum percent noise.

These clusters on average were 98.44860500842285 of their dominant kmeans cluster.
Silhouette Score: 0.42408914927203 with cache data.
58 clusters, + 0.659535108179844% were NOT categorized.

Note, this is better than the best silhouette score for kmeans, which was 0.335615866756178.

And the number of clusters is comparable to kmeans (58 vs 50).

| DBSCAN cluster | number of caches | homogeneity |
|--- |--- |--- |
| noise | 82 | 0.0 |
| 0 | 8683 | 33.46769549694806 |
| 1 | 70 | 100.0 |
| 2 | 159 | 100.0 |
| 3 | 65 | 100.0 |
| 4 | 131 | 100.0 |
| 5 | 2 | 100.0 |
| 6 | 350 | 100.0 |
| 7 | 152 | 100.0 |
| 8 | 87 | 100.0 |
| 9 | 50 | 100.0 |
| 10 | 48 | 100.0 |
| 11 | 62 | 100.0 |
| 12 | 3 | 100.0 |
| 13 | 9 | 100.0 |
| 14 | 56 | 100.0 |
| 15 | 108 | 100.0 |
| 16 | 2 | 100.0 |
| 17 | 78 | 100.0 |
| 18 | 5 | 100.0 |
| 19 | 85 | 100.0 |
| 20 | 3 | 100.0 |
| 21 | 60 | 100.0 |
| 22 | 4 | 100.0 |
| 23 | 3 | 100.0 |
| 24 | 50 | 100.0 |
| 25 | 195 | 100.0 |
| 26 | 14 | 100.0 |
| 27 | 4 | 75.0 |
| 28 | 65 | 100.0 |
| 29 | 2 | 100.0 |
| 30 | 58 | 100.0 |
| 31 | 2 | 100.0 |
| 32 | 2 | 100.0 |
| 33 | 88 | 100.0 |
| 34 | 49 | 100.0 |
| 35 | 2 | 100.0 |
| 36 | 52 | 100.0 |
| 37 | 59 | 100.0 |
| 38 | 331 | 100.0 |
| 39 | 46 | 100.0 |
| 40 | 4 | 100.0 |
| 41 | 179 | 100.0 |
| 42 | 103 | 100.0 |
| 43 | 15 | 100.0 |
| 44 | 114 | 100.0 |
| 45 | 102 | 100.0 |
| 46 | 168 | 100.0 |
| 47 | 62 | 100.0 |
| 48 | 48 | 100.0 |
| 49 | 52 | 100.0 |
| 50 | 25 | 100.0 |
| 51 | 60 | 100.0 |
| 52 | 2 | 100.0 |
| 53 | 6 | 100.0 |
| 54 | 2 | 100.0 |
| 55 | 73 | 100.0 |
| 56 | 38 | 100.0 |
| 57 | 2 | 100.0 |
| 58 | 2 | 100.0 |

The DBSCAN clusters map directly to single KMeans clusters, EXCEPT for DBSCAN clusters 1 and 27.

Several KMeans clusters have been split into 2 or more DBSCANS clusters.

DBSCAN cluster #27 is just 4 caches, and 3 of them are the same KMeans label.

The only real issue is with DBSCAN cluster #0, with includes 99.9% of the KMeans cluster 0, which was already the largest cluster in KMeans, with 23.4% of the caches, PLUS another 5575 caches split among 8 other Kmeans clusters. Altogether, DBSCAN cluster #0 is 69.8% of the caches.

However, this is a big issue - nearly 70% of the caches are all the same cluster. Given the similarity between this and kmeans otherwise, I will opt to stick with the kmeans clusters going forward.

### Recommender Development  - Clusters

When a user selects a cache to start with, the recommender returns:

1. A message if there are no other caches in the same cluster (but there were only 3 singleton caches, out of 12432)

2. All of the caches within the same cluster, if 5 or fewer

3. The 5 caches within the same cluster that are geographically closest to the user's starting cache, if there are more than 5. Just to keep it manageable.

Assuming that there were caches with the same cluster (true in 99.9759% of cases), the output includes the geocaching code and name for each recommendation. It does not give any other details of individual caches, to protect the geocaching.com data -- the game is based on secret locations, requiring at least a free login to access.

However, the recommender does took at the range of difficulty and terrain in the caches, and adds to the output based on those ranges:

| condition             | comment part 1 | comment part 2                                 |
| ---                   | ---            | ---                                            |
| all 1-3 difficulty    | "These are all nice and easy "                            |     |
| some 3.5-5 difficulty | "Some of these are higher difficulty "                    |     |
| all 3.5-5 difficulty  | "Better put on your thinking cap for these tough caches " |     |
| all 1-3 terrain       |     | "and the terrain should be not too bad."                  |
| some 3.5-5 terrain    |     | "and some have some rough terrain."                       |
| all 3.5-5 terrain     |     | "and hiking boots and TecNu may be in order for these."   |

### Recommender Development Vectors: cosine similarities

Three attempts were made on a cosine similarity recommender:

1. Using the text of the cache's name, descriptions, and any hints, ONLY
2. Using everything BUT the cache text itself (but including log counts and log sentiment)
3. Combining the first two into a single recommender

Of these, the "everything but the cache text" turned out to be the best.

#### Text only recommender:

First, the name, short description, long description, and hints were combined into a single text corpus for each cache.

They contained a lot of HTML code, so they had to be cleaned. I used imports (mechanize, nltk, bs4.BeautifulSoup, and html2text) and a function I found at:

https://stackoverflow.com/questions/26002076/python-nltk-clean-html-not-implemented

#### No text recommender:

The following features were used:

| feature | type | notes |
| --- | --- | --- |
| cache type | categorical, converted to dummies | "traditional", "virtual", "multi", ... |
| container size | int, 0-4 | 0 if the cache has no container, 1=micro, 2=small, 3=regular, 4=large |
| difficulty rating | float | 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, set by cache creator |
| terrain rating | float | 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, set by cache creator |
| cache creator | categorical, converted to dummies | set to "other" for infrequent cache creators |
| date of cache creation | datetime | YYYY-MM-DD |
| status | binary | 1 if active in April 2021, 0 if temporarily disabled |
| short description | binary | 1 if present in cache info, if absent |
| long description | binary | 1 if present in cache info, if absent |
| hint(s) | binary | 1 if present in cache info, if absent |
| premium | binary | 1 if restricted to premium members, 0 if available to all cachers |
| favpoints | int | number of times the cache has been favorited |
| travel bugs | binary | 1 if at least one travel bug has visited the cache, 0 if not |
| good logs | int | number of the most recent 10 logs that were "good" type: found it, etc... |
| bad logs | int | number of the most recent 10 logs that were "bad" type: needs maintenance, etc... |
| neutral logs | int | number of the most recent 10 logs that were purely logisical types: coords altered, etc... |
| log sentiment | float, between -1 and 1 | VADER sentiment analysis of aggregated most recent 10 logs |


#### Combined recommender:

The two databases were combined. In all of the attempted recommenders, every feature was scaled according to

z = (x - mean[x])/std.dev.[x]

In combining these two, distributions of correlations and overlap in top 10 and top 100 recommendations were examined between each of the original two, and between each one and the combined.

To 95% confidence, the correlation between the two completely separate recommender dataframes is between 0.1052 and 0.1090.

When combined, the initial combined recommender showed strong correlation and overlap with the text only recommender, and hardly any with the no-text. This is probably because nearly 2/3 of the features were from the text (92 vs. 56). I tried to adjust this by reducing the scale of the every text-based feature by 50%, to reduce their impact on the overall recommendation. When I did so, to 95% confidence, the combined recommender is correlated to the parameter only recommender to between 0.880 and 0.884, and to the text only recommender to between 0.451 and 0.456.

#### Building the recommender:

Ultimately, when both the text-only and no-text cosine distance recommenders were compared to the output of the KMeans clustering, the no-text showed a strong tendency to agree with the clustering, and the text only did not. So the final app is built using the no-text version.

The recommendation dataframe was created using pivot_table, sparse.csr_matrix, and sklearn.metrics.pairwise.pairwise_distances, and was 12,433 x 12,433 when completed. Each row and each column shows the cosine distance between a specific cache and each of the caches in the dataset.

Cosine similarity is a measure of the cosine of the angle between each cache's vector, defined by it's representation in the 56-dimensional feature space. Cosines always range between 1 at 0, to -1 at pi/2 (90 degrees) and back to 1 at pi (180 degrees), so two caches that are nearly identical should have a cosine similarity of nearly 1, indicating a near zero angle between their vectors. Conversely, two caches that are nearly opposite should have vectors pointing 180 degrees apart in the N-dimensional space, with a cosine similarity near -1, and two caches without any clear relation would have a cosine similarity near 0.

Cosine DISTANCE, used here, is simply given by CD = 1 - CS.

| cos simularity | cos distance |
| --- | --- |
| -1 | 2 |
|  0 | 1 |
|  1 | 0 |

and so values range between 0 (strongly similar caches) to 2 (completely opposite caches).

Reference: https://www.youtube.com/watch?v=ieMjGVYw9ag

The output of this recommender is the 5 caches, other than the starting cache, with the lowest cosine distance from the user-selected starting cache.

The output includes the geocaching code and name and cosine distance for each recommendation. Again, it does not give any other details of individual caches, to protect the geocaching.com data -- the game is based on secret locations, requiring at least a free login to access.

However, the recommender does took at the range of difficulty and terrain in the caches, and adds to the output based on those ranges:

| condition             | comment part 1 | comment part 2                                 |
| ---                   | ---            | ---                                            |
| all 1-3 difficulty    | "These are all nice and easy "                            |     |
| some 3.5-5 difficulty | "Some of these are higher difficulty "                    |     |
| all 3.5-5 difficulty  | "Better put on your thinking cap for these tough caches " |     |
| all 1-3 terrain       |     | "and the terrain should be not too bad."                  |
| some 3.5-5 terrain    |     | "and some have some rough terrain."                       |
| all 3.5-5 terrain     |     | "and hiking boots and TecNu may be in order for these."   |

### StreamLit App Development and Deployment

The app is developed in recommender.py and deployed in streamlit.

LINK: https://share.streamlit.io/christinaholland/yournextgeocache/main/recommender.py

The cosine distance dataframe is very large. If the user had to allow the entire data to load before getting a recommendation, the process would be slow and frustrating. So, I have run the recommender (Kmeans and cosine distance) on the entire collection of 12432 caches in Georgia, and saved the text output of the recommender for each. The app only needs to load this, plus a few smaller files to facilitate the user selection of a starting cache, so it is much quicker. This does have the effect of "freezing" the recommendations, but that would be true regardless until such time as I am hypothetically able to incorporate real time additions to the database and new calculations of clustering and cosine distance.

There are three parts to the app:
1. user selection of the initial cache (SIDEBAR)
2. output of recommendations (MAIN PAGE, TOGGLED)
3. information about the model (MAIN PAGE, TOGGLED)

#### User selection of the initial cache (SIDEBAR):

To START, the user can choose to: (1) enter a code, (2) enter a name (or partial), (3) enter a latitude and longitude.

Here is the logic for cache selection:

| First Input Level | Second Input Level | Third Input Level |
| --- | --- | --- |
| (1) If user selects to enter code: have them enter it | | |
| | (1A) If the code is in the database, ___RETURN CODE___ | |
| | (1B) If not, prompt them to retype or start over entirely | |
| | | (1B-i) If they choose to retype, go back to (1) |
| | | (1B-ii) If they choose to start over, go back to START |
| (2) If user selects to enter name: have them enter it | | |
| | (2A) Show the user the 4 names closest to what they typed (alphabetically) | |
| | | (2A-i) If they choose a specific cache, ___RETURN CODE___ |
| | | (2A-ii) If they choose to retype, go back to (2) |
| | | (2A-iii) If they choose to start over, go back to START |
| (3) If user selects to enter latitude & longitude: have them enter it | | |
| | (3A) Show the user the 4 cache codes/names closest to what they typed (geographically) | |
| | | (3A-i) If they choose a specific cache, ___RETURN CODE___ |
| | | (3A-ii) If they choose to retype, go back to (3) |
| | | (3A-iii) If they choose to start over, go back to START |

And of course the user can change the cache selection at any time. All of this exists in the __SIDEBAR__.

#### Output of recommendations (MAIN PAGE, TOGGLED):

__HEADER__: 'Here are the recommended caches, if you liked ' + __CODE__

__OUTPUT CONTENT__: As previously saved for each cache, selected for __CODE__

__CLOSING__: '(Please use the sidebar if you want to change your starting cache)'

#### Information about the model (MAIN PAGE, TOGGLED):

1. A 2-sentence explanation of what this app is and why it was created.
2. How to start, to get a recommendation.
3. Where the data comes from (3 sentences).
4. An explanation of the "guts" of the recommender: 3 paragraphs and a list of the included features.
5. Thanks, and my contact info (email).

#### Screenshots:

| Screenshots |  |
|---|---|
|<img src="./6_Notes_and_Images/assets/app_ss0.png" width="600"/> |<img src="./6_Notes_and_Images/assets/app_ss1.png" width="600"/>   |
|<img src="./6_Notes_and_Images/assets/app_ss2.png" width="600"/> |<img src="./6_Notes_and_Images/assets/app_ss3.png" width="600"/>   |
|<img src="./6_Notes_and_Images/assets/app_ss4.png" width="600"/> |   |

#### Feedback:

I put a link to a short google form at the top of the app, with a single required question:

"If this app had all of the caches in your state and was kept fully up to date, would you find it useful enough to make it a regular part of your caching experience?",

and an optional space for more feedback. I then posted the app link on the Atlanta Area Geocachers group on facebook and on r:/geocaching on reddit. 

I started with a prior beta distribution completely unknown: alpha = beta = 1. I have since had just 3 replies to the survey (early days!), but the reddit post got 5 upvotes and no downvotes. Putting those together gives either:

alpha = 1 + 2 = 3
beta = 1 + 1 = 2

(3 - 1)/(3 + 2 - 2) = 0.6667

for the survey data so far, or 

alpha = 1 + 5 = 6
beta = 1 + 0 = 1

(6 - 1)/(6 + 1 - 2) = 1.0000

based on the reddit upvotes.

The reality, I would guess, is somewhere in between, but I'll have to wait for data.

<img src="./6_Notes_and_Images/assets/bayes.png" width="600"/>
