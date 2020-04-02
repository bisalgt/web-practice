
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated


import json
from nltk.tokenize import word_tokenize
from inltk.inltk import setup
from inltk.inltk import get_sentence_similarity
from nltk.corpus import wordnet
import nltk
import spacy
import string
import warnings
import mysql.connector


nlp = spacy.load('en_core_web_sm')
stopwords = nlp.Defaults.stop_words
setup('en')
nltk.download('punkt')
warnings.filterwarnings('ignore')




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

	######### user input block ###############
	body_in_bytes = request.body
	body_in_json = body_in_bytes.decode('utf-8')
	body = json.loads(body_in_json)
	
	user_input = body["question"].lower()
	user_input_without_punctuation = user_input.translate(str.maketrans('', '', string.punctuation))
	user_input_tokenized = word_tokenize(user_input_without_punctuation)
	
	required_user_input = []
	for data in user_input_tokenized:
	    if data.isdigit() == False:
	        if data not in stopwords:
	            required_user_input.append(data)

	final_user_input = " ".join(required_user_input)
	print(final_user_input)


	######## question by subject ###############
	question_by_sub = [question for question in result if list(question)[1]==body["id"]]
	questions_from_database = [question[2].lower() for question in question_by_sub]


	######## questions punctuation removed ######
	questions_from_database_punctuation_removed = []
	for each in questions_from_database:
	    out = each.translate(str.maketrans('', '', string.punctuation))
	    questions_from_database_punctuation_removed.append(out)

	######## questions tokenized ##########
	tokenized_questions_from_database = []
	for each in questions_from_database_punctuation_removed:
	    tokenized = word_tokenize(each)
	    tokenized_questions_from_database.append(tokenized)


	######## required question from database ##########
	required_questions_from_database = []
	for data in tokenized_questions_from_database:
	    required_value_list = []
	    for value in data:
	        if value.isdigit() == False:
	            if value not in stopwords:
	                required_value_list.append(value)
	    required_questions = " ".join(required_value_list)
	    required_questions_from_database.append(required_questions)


	######### similar questions ###########
	similar_questions = []
	for i,j in enumerate(required_questions_from_database):
	    value = get_sentence_similarity(final_user_input, j, 'en')
	    if value>0.6 and value < 1.0:
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


	
