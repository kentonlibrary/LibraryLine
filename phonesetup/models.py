from django.db import models
from django.utils import timezone

class button(models.Model):
	button_name = models.CharField(max_length=100)
	file_name = models.CharField(max_length=100, null=True)

	def __str__(self):
		return str(self.file_name)

class statsession(models.Model):
	session_id = models.IntegerField(primary_key=True)
	start_time = models.DateTimeField(default=timezone.now)
	end_time = models.DateTimeField(null=True)

	def __str__(self):
		return self.session_id

class statactivity(models.Model):
	activity_id = models.IntegerField(primary_key=True)
	button_name = models.ForeignKey(button, on_delete=models.CASCADE)
	button_file_name = models.CharField(max_length=100)
	session_id = models.ForeignKey(statsession, on_delete=models.CASCADE)
	timestamp = models.DateTimeField(default=timezone.now)
