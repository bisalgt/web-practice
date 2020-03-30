from django.shortcuts import render
from django.http import HttpResponse
import requests
from inltk.inltk import get_sentence_similarity
from nltk.corpus import wordnet
from nltk.tokenize import word_tokenize
import pandas as pd
import spacy
import string

# Create your views here.

def home(request):
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

	return render(request, 'index.html')