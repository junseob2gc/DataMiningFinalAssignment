#install the following libraries to run the code
#install azure-ai-textanalytics (version 3)
#install sqlalchemy
#install pymysql
#install wordcloud
#install matplotlib
#install pandas
#pip install azure-cognitiveservices-vision-customvision
#pip install azure-cognitiveservices-vision-computervision
#pip3 install time

# import libraries
#import trainer as trainer
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential
from sqlalchemy import create_engine, text
import pandas as pd
import matplotlib.pyplot as plt
#needed to create wordcloud
from wordcloud import WordCloud, STOPWORDS
import re
from azure.cognitiveservices.vision.customvision.training import CustomVisionTrainingClient
from azure.cognitiveservices.vision.customvision.training.models import ImageFileCreateBatch, ImageFileCreateEntry
import time
from azure.cognitiveservices.vision.customvision.prediction import CustomVisionPredictionClient
from msrest.authentication import ApiKeyCredentials

# frameworks for the Word Cloud:
# First of all, you need to download the c++ build tools for the VS 2019 (the size is 4.76 g)
# https://visualstudio.microsoft.com/thank-you-downloading-visual-studio/?sku=BuildTools&rel=16


#authenticates with Azure for Sentiment Analysis
def authenticate_text_client():
    key = "a41d5581d6a146438b741ae0f5ba719a"
    endpoint = "https://eastus.api.cognitive.microsoft.com/"
    # paramaters needed for Azure Analytics
    ta_credential = AzureKeyCredential(key)
    text_analytics_client = TextAnalyticsClient(endpoint=endpoint, credential=ta_credential)
    return text_analytics_client

#runs sentiment analysis on tweets
def sentiment_analysis(tweets):
    tweeetlist = [tweets]
    response = client.analyze_sentiment(tweeetlist)
    keyphrase = client.extract_key_phrases(tweeetlist)
    list = [[response],[keyphrase]]
    return list

#function that gets just the text and image columns data from the database
#filters for tweets and images related to Donald Trump
def get_db_data():
    db_connection_str = 'mysql+pymysql://admin:bdat1007@rssnews-db.cmhk8qnm6hfj.us-east-2.rds.amazonaws.com/data_mining'
    db_connection = create_engine(db_connection_str)
    query= 'SELECT images, text FROM data_mining.twitter_w_images WHERE text like "%Donald Trump%" or text like "%Trump%" or text like "@donaldjtrump%"'
    print(query)
    df = pd.read_sql_query(text(query),con=db_connection)
    return df

#runs Azure cognitive analysis on tweets
def scoresource(alltweets,images):
    #These lists are needed to get the results of the sentiment analysis
    positive_score = []
    neutral_score = []
    negative_score  = []
    keyphrases = []
    #get the sentiment score overall
    for i in range(0,len(alltweets)):
        results = sentiment_analysis(alltweets[i])
        scores = results[0][0][0]
        phrases = results[1][0][0]
        positive_score.append(scores.confidence_scores.positive)
        neutral_score.append(scores.confidence_scores.neutral)
        negative_score.append(scores.confidence_scores.negative)
        keyphrases.append(phrases.key_phrases)
    tuples = list(zip(alltweets,positive_score,neutral_score,negative_score,keyphrases,images))
    results_df = pd.DataFrame(tuples,columns=['tweet_text','Positive','Neutral','Negative','Key_Phrases','images'])
    return results_df

# cleans the tweets of punctuation
def cleankeyphrases(df):
    comment_words = ''
    # typecaste every value to the string
    for val in df.Key_Phrases:
        val = str(val)
        # then split
        tokens = val.split()
        # Converts each token to lowercase
        for i in range(len(tokens)):
            tokens[i] = re.sub(r'[\',-./]|\sBD', r'', tokens[i]).lower()
        for words in tokens:
            comment_words = comment_words + words + ' '
    return comment_words

#creates the tweets dataframe
tweet_df = get_db_data()
tweet_text = tweet_df['text'].tolist()
image_urls = tweet_df['images'].tolist()
client = authenticate_text_client()
tweet_df = scoresource(tweet_text,image_urls)


#create the string for wordcloud and generate word clouds
tweets_wordlcoud_string =cleankeyphrases(tweet_df)
stopwords = set(STOPWORDS)
stopwords.update(["€™", "©"])
# wordcloud_tweets = WordCloud(width = 800, height = 800,
#                      background_color ='white',
#                      stopwords = stopwords,
#                      min_font_size = 10).generate(tweets_wordlcoud_string)
#
# # create a wordcloud
# plt.figure(figsize=(8, 8), facecolor=None)
# plt.imshow(wordcloud_tweets)
# plt.axis("off")
# plt.tight_layout(pad=0)
# plt.show()
#
# # Overall statistics for the pie
# # Pie chart, where the slices will be ordered and plotted counter-clockwise:
# labels = 'Positive', 'Neutral', 'Negative'
# sizes = [tweet_df['Positive'].mean(), tweet_df['Neutral'].mean(), tweet_df['Negative'].mean()]
# explode = (0.1, 0.1, 0.1)
# colors = ['lightgreen', 'orange', 'orangered']
# fig1, ax1 = plt.subplots()
# ax1.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',
#         shadow=True, startangle=90, colors=colors)
# ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
# plt.show()

ENDPOINT = "https://dataminingasgfour-prediction.cognitiveservices.azure.com/"
training_key = "08acd5cf3c8948829673c53d930d2f50"
prediction_key = "dfe4b7746ad74c1f98b130d7bfc5048a"
credentials = ApiKeyCredentials(in_headers={"Training-key": training_key})
trainer = CustomVisionTrainingClient(ENDPOINT, credentials)


#constants for the prediction model and tags
project = trainer.create_project("TrumpAnalytics")
prediction_resource_id = "/subscriptions/31dad0b5-b624-4e49-815e-51e72ad9f6e4/resourceGroups/GeorgianCollege/providers/Microsoft.CognitiveServices/accounts/DataMiningAsgFour-Prediction"
publish_iteration_name = "classifyModel"
image_list = []

import os
import urllib

home_folder = os.getcwd()
os.chdir(".\\TrumpImageLibrary")
trump_tag = trainer.create_tag(project.id, "Trump")
training_image_url =
x = 0
for link in prediction_images:
    x = x + 1
    name = "image{}.jpg".format(x)
    try:
        training_resource = urllib.request.urlopen(link)
    except:
        print("one of the file doesn't exists")
    output = open(name, "wb")
    output.write(resource.read())
    output.close()

#iterate over the images
#change list to 17 when done
for image_num in range(1, 17):
    file_name = ".\\image{}.jpg".format(image_num)
    with open(file_name, "rb") as image_contents:
        image_list.append(ImageFileCreateEntry(name=file_name, contents=image_contents.read(), tag_ids=[trump_tag.id]))
upload_result = trainer.create_images_from_files(project.id, ImageFileCreateBatch(images=image_list))
if not upload_result.is_batch_successful:
    print("Image batch upload failed.")
    for image in upload_result.images:
        print("Image status: ", image.status)
    exit(-1)
#return to home folder
os.chdir(home_folder)

iteration = trainer.train_project(project.id)
while iteration.status != "Completed":
    iteration = trainer.get_iteration(project.id, iteration.id)
    print ("Training status: " + iteration.status)
    time.sleep(1)

# The iteration is now trained. Publish it to the project endpoint
trainer.publish_iteration(project.id, iteration.id, publish_iteration_name, prediction_resource_id)

import urllib
# Firstly create a folder for the image which we need to predict
if not os.path.exists('Folder_for_predictions'):
    os.makedirs('Folder_for_predictions')

# moving to this folder (will back to root later)
os.chdir(".\\Folder_for_predictions")

# Then we download all pictures from prediction_images to this folder:
prediction_images = tweet_df['images']

x = 0
for link in prediction_images:
    x = x + 1
    name = "image{}.jpg".format(x)
    try:
        resource = urllib.request.urlopen(link)
    except:
        print("one of the file doesn't exists")
    output = open(name, "wb")
    output.write(resource.read())
    output.close()

# back to the root folder
os.chdir(home_folder)
results_list = []

# prepare information for the predict model
path_for_count_files = home_folder + "\\Folder_for_predictions\\"
prediction_images_count = os.listdir(path_for_count_files)

# Finally, predict the images
prediction_credentials = ApiKeyCredentials(in_headers={"Prediction-key": prediction_key})
predictor = CustomVisionPredictionClient(ENDPOINT, prediction_credentials)

for image in prediction_images_count:

    image_url = path_for_count_files + image

    try:
        with open(image_url, "rb") as image_contents:
            results = predictor.classify_image(project.id, publish_iteration_name, image_contents.read())

            # Display the results.
            for prediction in results.predictions:
                x = "\t" + prediction.tag_name + ": {0:.2f}%".format(prediction.probability * 100)

                # Take a score for tweet_df
                y = "{0:.2f}%".format(prediction.probability * 100)
                results_list.append(y)

                print(x)

    except:
        results_list.append(0) # Otherwise it will be more difficult to match score and tweet
        print("one of the file isn't image or image is difficult to predict")

print("the algorithm is finished")

# append score result to tweet_df
#at this point
tweet_df['Score'] = results_list

#unpublish and delete the project to stay under the Azure limit
#credentials:
##username = stupidgeorgian@hotmail.com
##password = Essc1234
#https://www.customvision.ai/projects
