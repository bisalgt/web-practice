from django.shortcuts import render
from django.http import JsonResponse

from ratelimit.decorators import ratelimit

import requests
from inltk.inltk import setup
from inltk.inltk import get_sentence_similarity
from nltk.corpus import wordnet
from nltk.tokenize import word_tokenize
import nltk
import spacy
import string

import warnings
warnings.filterwarnings('ignore')

nlp = spacy.load('en_core_web_sm')
stopwords = nlp.Defaults.stop_words

import mysql.connector
import json

# # ratelimit key
# def key_finder(group, request):
#     return request.META['REMOTE_ADDR'] + request.user.username


try:
    connection = mysql.connector.connect(host='localhost',
                                         database='quizes',
                                         user='root'
                                         )

    if connection.is_connected():
        db_Info = connection.get_server_info()
        print("Connected to MySQL Server version ", db_Info)
        cursor = connection.cursor()
        cursor.execute("select * from quizes where sub_id=15;")
        result = cursor.fetchall()
        print(len(result))

except Exception as e:
    print("Error while connecting to MySQL", e)

# finally:
#     if connection.is_connected():
#         cursor.close()
#         connection.close()
#         print("MySQL connection is closed")





# print(connection)
# @ratelimit(key=key_finder(), rate='3/m')
def home(request):
	# global nlp
	# global stopwords
	# print(id)
	# print(request)
	# print('----------')
	# print(str)
	# print(dir(request))
	# print(request.body.decode("utf-8"))
	body_in_bytes = request.body

	body_in_json = body_in_bytes.decode('utf-8')
	# print(body_in_str, type(body_in_str))
	# body_json = json.dumps(body_in_str)
	body = json.loads(body_in_json)
	print(body, type(body))
	# print(request._current_scheme_host) # current ip of host
	# print(request.META['HTTP_HOST'])
	# print('-----------------')
	# print(request.path)
	# print(request.user)
	url = 'http://promech:6p{f(SDz>7$E9JJd@35.154.93.222/api/v1.1/quiz/?subject_id=47&per_page=54&page=1'
	r = requests.get(url).json()
	# print(dir(r))
	# print(r)
	# print(len(r))
	total_number_of_question = len(r["data"])
	question_listed = list()
	for i in range(total_number_of_question):
		question_listed.append(r["data"][i]["question"])
	# print(question_listed)

	# first time 
	# setup('en')
	# nltk.download('punkt')



	# nlp = spacy.load('en_core_web_sm')
	# stopwords = nlp.Defaults.stop_words
	# print(len(stopwords))

	url_slug_split = slug.split('-')

	user_input = ' '.join(url_slug_split)
	user_input_without_punctuation = user_input.translate(str.maketrans('', '', string.punctuation))
	user_input_tokenized = word_tokenize(user_input_without_punctuation)


	
	required_user_input = []
	for data in user_input_tokenized:
	    if data.isdigit() == False:
	        if data not in stopwords:
	            required_user_input.append(data)

	final_user_input = " ".join(required_user_input)
	# print(final_user_input)

	questions_from_database = [question.lower() for question in question_listed]
	# print(questions_from_database)

	questions_from_database_punctuation_removed = []
	for each in questions_from_database:
	    out = each.translate(str.maketrans('', '', string.punctuation))
	    questions_from_database_punctuation_removed.append(out)
	# print(questions_from_database_punctuation_removed)

	tokenized_questions_from_database = []
	for each in questions_from_database_punctuation_removed:
	    tokenized = word_tokenize(each)
	    tokenized_questions_from_database.append(tokenized)

	# print(tokenized_questions_from_database)

	required_questions_from_database = []
	for data in tokenized_questions_from_database:
	    required_value_list = []
	    for value in data:
	        if value.isdigit() == False:
	            if value not in stopwords:
	                required_value_list.append(value)
	    required_questions = " ".join(required_value_list)
	    required_questions_from_database.append(required_questions)

	# print(required_questions_from_database)

	similar_questions = []
	for i,j in enumerate(required_questions_from_database):
	    value = get_sentence_similarity(final_user_input, j, 'en')
	    if value>0.6 and value < 1.0:
	        temp_dict = dict()
	        temp_dict["Question"] = questions_from_database[i]
	        temp_dict["Similarity Percentage"] = int(value*100)
	        similar_questions.append(temp_dict)
	# print(similar_questions)

	final_list = sorted(similar_questions, key=lambda k: k['Similarity Percentage'], reverse = True)

	# print(final_list)

	return JsonResponse(final_list, safe=False)