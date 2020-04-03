from gensim.models import word2vec, KeyedVectors
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import nltk
import numpy as np
import torch
import pandas as pd
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords 
import string
import mysql.connector
import json

from django.http import JsonResponse


nltk.download('stopwords')

try:
    connection = mysql.connector.connect(host='localhost',
                                         database='quizes',
                                         user='root'
                                         )

    if connection.is_connected():
        db_Info = connection.get_server_info()
        print("Connected to MySQL Server version ", db_Info)
        cursor = connection.cursor()
        cursor.execute("select * from quizes;")
        result = cursor.fetchall()
        print(len(result))
        print(type(result))
        print(type(result[1]))

except Exception as e:
    print("Error while connecting to MySQL", e)


model = KeyedVectors.load_word2vec_format("GoogleNews-vectors-negative300.bin", binary = True, limit = 100000)
index2word_set = set(model.index2word)
# sw contains the list of stopwords 
sw = stopwords.words('english') 



def avg_sentence_vector(words, model, num_features, index2word_set):
    #function to average all words vectors in a given paragraph
    featureVec = np.zeros((num_features,), dtype="float32")
    nwords = 0

    for word in words:
        if word in index2word_set:
            nwords = nwords+1
            featureVec = np.add(featureVec, model[word])

    if nwords>0:
        featureVec = np.divide(featureVec, nwords)
    return featureVec



def home(request):

	body_in_bytes = request.body
	body_in_json = body_in_bytes.decode('utf-8')
	body = json.loads(body_in_json)
	
	#get average vector for sentence 1
	user_input = body["question"].lower()
	user_input_without_punctuation = user_input.translate(str.maketrans('', '', string.punctuation))
	user_input_tokenized = word_tokenize(user_input_without_punctuation)

	final_user_input = [w for w in user_input_tokenized if not w in sw] 
	sentence_1_avg_vector = avg_sentence_vector(final_user_input, model=model, num_features=300, index2word_set = index2word_set)
	# print(sentence_1_avg_vector)
	s1 = torch.from_numpy(sentence_1_avg_vector)


	question_by_sub = [question for question in result if list(question)[1]==body["id"]]

	questions_from_database = [question[2].lower() for question in question_by_sub]


	similar_questions = []
	for i,each in enumerate(questions_from_database):
	    #get average vector for sentence 2
	    questions_from_database_punctuation_removed = each.translate(str.maketrans('', '', string.punctuation))
	    tokenized_questions_from_database = word_tokenize(questions_from_database_punctuation_removed)
	    final_questions_from_database = [w for w in tokenized_questions_from_database if not w in sw] 
	    sentence_2_avg_vector = avg_sentence_vector(final_questions_from_database, model=model, num_features=300, index2word_set = index2word_set)
	    # print(sentence_2_avg_vector)
	    s2 = torch.from_numpy(sentence_2_avg_vector)

	    # Calculate Similarity
	    # sen1_sen2_similarity =  cosine_similarity(sentence_1_avg_vector.reshape(-1, 1),sentence_2_avg_vector.reshape(-1, 1))
	    sen1_sen2_similarity = torch.nn.functional.cosine_similarity(s1, s2, dim = 0, eps = 1e-8)
	    value = sen1_sen2_similarity.item()
	    if value >=0.8 and value <=1.0:
	        temp_dict = dict()
	        temp_dict["Question"] = questions_from_database[i]
	        temp_dict["Similarity Percentage"] = int(value*100)
	        similar_questions.append(temp_dict)


	final_list = sorted(similar_questions, key=lambda k: k['Similarity Percentage'], reverse = True)
	print(final_list)


	return JsonResponse(final_list, safe=False)