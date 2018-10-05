from django.contrib.auth import get_user_model
from django.db import models
from datetime import datetime

User=get_user_model()
class Team(models.Model):
	employee	=	models.ForeignKey(User, on_delete=models.CASCADE)
	teamname	=	models.CharField(max_length=50)

	def __str__(self):
		return '%s %s' % (self.employee.id, self.teamname)

#gives filename's extension
def get_filename_ext(filepath):
	base_name = os.path.basename(filepath)
	name, ext= os.path.splitext(base_name)
	return name, ext

def upload_audio_path(instance, filename):
	# print(instance)
	# print(filename)
	#generating a new file name to avoid any issues using a random number as the name of the file
	new_filename = random.randint(1,39102089312)
	name, ext=get_filename_ext(filename)
	final_filename='{new_filename}{ext}'.format(new_filename=new_filename, ext=ext)
	print(new_filename)
	print(final_filename)
	return "transcripts/{new_filename}/{final_filename}".format(
		new_filename=new_filename,
		final_filename=final_filename
		)

class Meeting(models.Model):
	conductor		=	models.ForeignKey(User, on_delete=models.CASCADE)
	meetingname		=	models.CharField(max_length=50)
	datetime		= 	models.DateTimeField(default=datetime.now(),blank=True)
	recording		=	models.FileField(upload_to=upload_audio_path)

	def __str__(self):
		return '%s %s' % (self.meetingname, self.conductor.id)

class MeetingAttendee(models.Model):
	meeting 		=	models.ForeignKey(Meeting, on_delete=models.CASCADE)
	conductor		=	models.ForeignKey(User, on_delete=models.CASCADE, related_name = 'conductor')
	attendee 		=	models.ForeignKey(User, on_delete=models.CASCADE, related_name = 'attendee')

	def __str__(self):
		return '%s %s %s' % (self.meeting.id, self.mconductor.id, self.attendee.id)

class Decision(models.Model):
	meeting 		=	models.ForeignKey(Meeting, on_delete=models.CASCADE)
	decision 		=	models.TextField()
	decisionfor		=	models.ForeignKey(Team, on_delete=models.CASCADE)

	def __str__(self):
		return '%s %s %s' % (self.meeting.id, self.decision, self.decisionfor)