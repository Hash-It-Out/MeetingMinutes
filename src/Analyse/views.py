from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.contrib.auth import get_user_model
import os

from django.core.mail import send_mail

import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords

import string

from .models import Meeting, MeetingAttendee, Team, upload_audio_path,get_filename_ext

from .FrequencySummarizer import FrequencySummarizer

keywords=[['frontend','front-end','responsive','color','theme','scheme','CSS','HTML','JS','javascript'],#frontend
		  ['script','backend','back-end','database','query','object','script','python'],#backend
		  ['people','business','analyse']]#management

def nltk(request):

	# EXAMPLE_TEXT = "Hello Mr. Smith, how are you doing today? The weather is great, and Python is awesome. The sky is pinkish-blue. You shouldn't eat cardboard."

	# text="Decide, the frontend team needs to make the website mobile reponsive decision end"

	BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
	MEDIA_ROOT = os.path.join(os.path.dirname(BASE_DIR), "static_cdn", "media_root")

	with open(MEDIA_ROOT+'/transcripts/transcript.txt', 'r') as myfile:
		text=myfile.read().replace('\n','')	

	print(text)

	datas=word_tokenize(text)
	# print(datas)
	# print(datas[0])

	#print ([i for i, item in enumerate(datas) if item == 'Decide'])

	decision_string = str('')
	decision=[]

	frontend_score=0
	backend_score=0
	management_score=0

	scores=[['Front-End Team',	0],
			['Back-End Team', 	0],
			['Management Team',	0]]

	flag=False # to see if 'Decide' word was said

	ps=PorterStemmer() # variable for stemming

	for i in range(len(datas)):
		# print(datas[i]+","+str(flag))
		if datas[i].lower() == 'decide':
			flag=True	

		if flag==True and datas[i].lower() == 'decision' and datas[i+1].lower() == "end":
			# print("hie")
			flag=False
			decision_string=decision_string.strip(' ')

			print(decision_string)

			# now doing the keyword matching using stemming
			decision=word_tokenize(decision_string)
			print(decision)

			for j in range(len(decision)):
				if decision[j] not in string.punctuation:
					stemmed_word=ps.stem(decision[j])
					print(stemmed_word)

					# now checking if the stemmed word is in any of the keywords ka list and appropriately assigning scores
					for x in range(len(keywords)):
						for y in range(len(keywords[x])):
							# print(str(x)+","+str(y))

							if stemmed_word.lower() == ps.stem(keywords[x][y]) :
								scores[x][1] = scores[x][1]+1

			print(scores)
			
			score=[]
			score.append(scores[0][1])
			score.append(scores[1][1])
			score.append(scores[2][1])

			notify=score.index(max(score))
			notify_team=scores[notify][0]
			
			print(notify_team)
			decision_string=str('')

		if flag==True :
			# i=i+1
			if datas[i] not in string.punctuation:
				decision_string = decision_string + ' ' + datas[i]
			else:
				decision_string = decision_string + datas[i]

	print("~~~~~~~~~~~~~~~~~summariser code~~~~~~~~~~~~~~~")
	
	fs = FrequencySummarizer()
	s = fs.summarize(str(text), 2)
	print (s)	

	context={
		'datas':'hello'
	}
	return render(request, "Analyse/nltk.html", context)

User=get_user_model()

def handle_uploaded_file(file, filename, foldername):
    
    print("--here--")
    print(filename)

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    MEDIA_ROOT = os.path.join(os.path.dirname(BASE_DIR), "static_cdn", "media_root")

    foldername= MEDIA_ROOT+'/transcripts/'+foldername
    if not os.path.exists(foldername):
    	print("not exists")
    	os.mkdir(foldername)

    with open(MEDIA_ROOT+'/'+filename, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)

def meeting(request, *args, **kwargs):

	print("hi")
	if request.method == "POST":
		print("haha")
		print(request.FILES['recording'])

		recording=upload_audio_path(request,str(request.FILES['recording']))

		print(recording)

		folder_name, ext=get_filename_ext(recording)

		print(folder_name)

		handle_uploaded_file(request.FILES['recording'], recording, folder_name)

		BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
		MEDIA_ROOT = os.path.join(os.path.dirname(BASE_DIR), "static_cdn", "media_root")
    	# foldername= MEDIA_ROOT+'/transcripts/'+foldername+'/'+

		m=Meeting.objects.get(id=1)
		# m.recording = 999  # change field
		# t.save() # this will update only

	print("hagre")

	user=request.user
	meeting=Meeting.objects.filter(conductor=request.user)
	# print(meeting)
	users=User.objects.exclude(username=request.user.username)
	# print(users)

	ma=[]

	for i in meeting:
		meetatten=MeetingAttendee.objects.filter(meeting=i)
		for j in meetatten:
			ma.append(j)		
	

	# print(ma)
	context={
		'datas':'hello',
		'meetatten':ma
	}
	return render(request, "Analyse/meetings.html", context)