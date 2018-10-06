from __future__ import print_function

from django.shortcuts import render
from django.http import HttpResponse, Http404, HttpResponseRedirect
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


import json,io
from os.path import join, dirname
from watson_developer_cloud import SpeechToTextV1
from watson_developer_cloud.websocket import RecognizeCallback, AudioSource
import threading
import math
from django.template import Template, Context
from django.http import HttpResponse

# Make it work for Python 2+3 and with Unicode
try:
    to_unicode = unicode
except NameError:
    to_unicode = str

keywords=[['frontend','front-end','responsive','color','theme','scheme','CSS','HTML','JS','javascript'],#frontend
		  ['script','backend','back-end','database','query','object','script','python'],#backend
		  ['people','business','analyse']]#management


def sttxt(request,filename,textfilepath,textfilename):
    kl = []
    service = SpeechToTextV1(
        username='80a593b1-5a21-4ea4-adb1-e7218fb5a9fa',
        password='1RGsVJJw8BlB',
        url='https://stream.watsonplatform.net/speech-to-text/api')

    models = service.list_models().get_result()
    #print(json.dumps(models, indent=2))

    model = service.get_model('en-US_NarrowbandModel').get_result()
    #print(json.dumps(model, indent=2))
    # with open(join(dirname(__file__), filename),'rb') as audio_file:
    print(filename)
    with open(filename,'rb') as audio_file:
        with io.open('data.json', 'w', encoding='utf8') as outfile:
            str_ = json.dumps(service.recognize(audio=audio_file,content_type='audio/mp3',speaker_labels=True).get_result(),indent=2)
            outfile.write(to_unicode(str_))

        outfile.close()
        

    # Read JSON file
    with open('data.json') as data_file:
        data_loaded = json.load(data_file)
    spea = []
    l=0

    for i in data_loaded['speaker_labels']:
        temp = ""
        if l == int(i['speaker']):
            for z in range(math.floor(i['from']),math.ceil(i['to'])):
                for v in data_loaded['results']:
                    for m in v['alternatives']:
                        for n in m['timestamps']:         
                            if n[1] >= i['from'] and n[2] <= i['to']:
                                if temp is not n[0]:
                                    spea.append(n[0])
                                    temp = n[0]
                                
                                #print(spea)
                            
                    
        else:
            str1 = ' '.join(spea)
            print(textfilepath+'transcripts/'+textfilename+'/'+textfilename+".txt")
            with io.open(textfilepath+'transcripts/'+textfilename+'/'+textfilename+".txt", 'a', encoding='utf8') as outfile:
            	
            	# print("Speaker "+str(l)+": "+str1+"\n")
            	str_ = outfile.write(" Speaker "+str(l)+": "+str1+"\n")

            	kl.append("Speaker "+str(l)+": "+str1+"\n")
            outfile.close()
            l = i['speaker']
            del spea[0:len(spea)-1]
            

            
    str1 = ' '.join(spea)
    with io.open(textfilepath+'transcripts/'+textfilename+'/'+textfilename+".txt", 'a', encoding='utf8') as outfile:
    	# print("Speaker "+str(l)+": "+str1+"\n")
    	str_ = outfile.write(" Speaker "+str(l)+": "+str1+"\n")
    	kl.append("Speaker "+str(l)+": "+str1+"\n")
    outfile.close()
    


    u = summary_function(textfilepath+'transcripts/'+textfilename+'/'+textfilename+".txt")

    print('vvvvvvvvvvvvvvvvvvv summarize VVVVVVVVVVVVVVVv')

    print(u)
    print('------------------- decisions ------------------------------------')
    decision=nltk(textfilepath+'transcripts/'+textfilename+'/'+textfilename+".txt")

    print(decision)
    request.session['summ'] = u
    request.session['trans1'] = kl
    request.session['deci'] = decision

    context={
    	'summarize':u,
    	'trans':kl,

    }

    return render(request,'Analyse/transcript.html',context)
    
    #return render(request,'Analyse/transcript.html',context)

def transcript(request):
    context={
    	'summarize':request.session['summ'],
    	'trans':request.session['trans1'],
    	'deci':request.session['deci'],
    }

    return render(request,'Analyse/transcript.html',context)

def summary_function(textfilepathfinal):

	with open(textfilepathfinal, 'r') as myfile:
		text=myfile.read().replace('\n','')	

	fs = FrequencySummarizer()
	s = fs.summarize(str(text), 2)
	return s

def nltk(textfilepathfinal):
# def nltk(request):

	BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
	MEDIA_ROOT = os.path.join(os.path.dirname(BASE_DIR), "static_cdn", "media_root")

	with open(textfilepathfinal, 'r') as myfile:
		text=myfile.read().replace('\n','')	

	# text="Decide, the frontend team needs to make the website mobile reponsive decision end"

	print(text)

	datas=word_tokenize(text)

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

	final_decisions=[]
	# final_decisions=[[0 for x in range(100)] for y in range(100)]
	z=0

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
					# stemmed_word=ps.stem(decision[j])
					# print(stemmed_word)

					# now checking if the stemmed word is in any of the keywords ka list and appropriately assigning scores
					for x in range(len(keywords)):
						for y in range(len(keywords[x])):
							# print(str(x)+","+str(y))

							if ps.stem(decision[j]).lower() == ps.stem(keywords[x][y]) :
								scores[x][1] = scores[x][1]+1

			print(scores)
			
			score=[]
			score.append(scores[0][1])
			score.append(scores[1][1])
			score.append(scores[2][1])

			notify=score.index(max(score))
			notify_team=scores[notify][0]
			
			# final_decisions[z][0]=decision_string
			# final_decisions[z][1]=notify_team
			final_decisions.append(decision_string)
			final_decisions.append(notify_team)

			z=z+1

			print(notify_team)
			decision_string=str('')

		if flag==True and datas[i].lower() != 'speaker' and i!=0:
			# i=i+1
			if datas[i] in string.punctuation:
				
				# if not any(p in datas[i] for p in string.punctuation):
				# print(datas[i])
				if datas[i] == ":" and datas[i-1].isdigit():
					print("in")
				else:
					decision_string = decision_string + datas[i]
			else:

				if (datas[i].isdigit()  and datas[i+1]== ":") or (i < len(datas) and datas[i] == datas[i+1]):
					print("in")
				else:
					decision_string = decision_string + ' ' + datas[i]
				

	context={
		'datas':'hello'
	}
	# return render(request, "Analyse/nltk.html", context)

	# print(final_decisions)
	return final_decisions

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

		filepath=MEDIA_ROOT+'/'+recording
		newfilepath=MEDIA_ROOT+'/'

		print(filepath)
		m=Meeting.objects.get(id=1)
		m.recording = filepath  # change field
		m.save() # this will update only

		sttxt(request, filepath,newfilepath,folder_name)

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
		'meetatten':ma,

	}
	return render(request, "Analyse/meetings.html", context)


def calenda(request):

	if method == 'POST':

		agenda = request.POST['agenda']
		print(agenda)