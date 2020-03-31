from django.shortcuts import render
from django.http import JsonResponse
import requests

from inltk.inltk import setup
from inltk.inltk import get_sentence_similarity
from nltk.corpus import wordnet
from nltk.tokenize import word_tokenize
import nltk
import pandas as pd
import spacy
import string

import warnings
warnings.filterwarnings('ignore')

# Create your views here.

def home(request, str):
	print(request)
	print('----------')
	print(str)
	# print(dir(request))
	print('-----------------')
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
	setup('en')
	nltk.download('punkt')



	nlp = spacy.load('en_core_web_sm')
	stopwords = nlp.Defaults.stop_words
	# print(len(stopwords))

	#

	slug = 'population-of-nepal'
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