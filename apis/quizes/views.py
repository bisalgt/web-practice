
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import JSONParser


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
import io



# stopwords download for use
nltk.download('stopwords')
# sw contains the list of stopwords 
sw = stopwords.words('english') 


# using the model from the root directory
model = KeyedVectors.load_word2vec_format("GoogleNews-vectors-negative300.bin", binary = True, limit = 100000)
index2word_set = set(model.index2word)




# function to average all workds vectors in a given paragraph
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





# connecting with mysql database and retriving all the questions
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






@api_view(['GET','POST'])
@authentication_classes([BasicAuthentication,])
@permission_classes([IsAuthenticated,])
def suggestor(request):
	# print(request.data)

	# print(dir(request))
	# print((request.query_params['id']))
	# print(type(dict(request.query_params)['id']))

	if request.body or request.query_params:
		if request.body:
			print('request.body runs')
			body_in_bytes = request.body
			body_in_json = io.BytesIO(body_in_bytes)
			body = JSONParser().parse(body_in_json)
		elif request.query_params:
			print('request.query_params runs')
			body = {'id':request.query_params['id'], 'question':request.query_params['question']}
		# elif request.data:
		# 	body = {'id':request.data['id'], 'question':request.data['question']}
	# body_1 = request.query_params
	print(body)
	######### user input block ###############
	# body_in_bytes = request.body
	# body_in_json = io.BytesIO(body_in_bytes)
	# body_2 = JSONParser().parse(body_in_json)
	# print(body)

	user_input = body["question"].lower()
	print(user_input)
	user_input_without_punctuation = user_input.translate(str.maketrans('', '', string.punctuation))
	user_input_tokenized = word_tokenize(user_input_without_punctuation)	
	final_user_input = [w for w in user_input_tokenized if not w in sw] 
	sentence_1_avg_vector = avg_sentence_vector(final_user_input, model=model, num_features=300, index2word_set = index2word_set)
	s1 = torch.from_numpy(sentence_1_avg_vector)


	######## question by subject ###############
	question_by_sub = [question for question in result if list(question)[1]==int(body["id"])]
	questions_from_database = [question[2].lower() for question in question_by_sub]
	# print(questions_from_database)

	######### similar questions ###########
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
	    if value >=0.6 and value <=1.0:
	        temp_dict = dict()
	        temp_dict["Question"] = questions_from_database[i]
	        temp_dict["Similarity Percentage"] = int(value*100)
	        similar_questions.append(temp_dict)


	######## final data ############
	final_list = sorted(similar_questions, key=lambda k: k['Similarity Percentage'], reverse = True)
	final_data = {
		"status_code": Response.status_code,
		"request_method": request.method,
		"total_matched": len(final_list),
		"subject_id": body["id"],
		"data": final_list
	}

	return Response(final_data)


	
