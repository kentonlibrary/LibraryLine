from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
import os
from .models import button
from django.core.files.storage import FileSystemStorage


def buttonUpdate(request): #Used to update which audio file plays on each button push
	path="mediaAssets/"
	file_list = sorted(os.listdir(path))
	#Form submit data
	if request.method == 'POST':
		buttonName = request.POST.get('button_name')
		buttonModel = button.objects.get(button_name=buttonName)

		fileName = request.POST.get('file_name')
		buttonModel.file_name = fileName
		buttonModel.save()

	context = {
		'buttons': button.objects.all().order_by('button_name'),
		'files': file_list
	}

	return render(request, 'phonesetup/button.html', context)

def listFiles(request): # used to rename files
	path="mediaAssets/"
	file_list = sorted(os.listdir(path))

	if 'old' in request.POST:
		old = request.POST.get('old')
		new = request.POST.get('new')
		os.rename(path + old, path + new)
		for buttonModel in button.objects.filter(file_name=old):
			buttonModel.file_name = new
			buttonModel.save()
		print("Rename")
	if 'delete' in request.POST:
		deleteFile = request.POST.get('delete')
		os.remove(path + deleteFile)
		print("Removed " + deleteFile)
	if 'submitFile' in request.POST:
		uploaded_file = request.FILES['audioFile']
		fs = FileSystemStorage()
		fs.save(uploaded_file.name, uploaded_file)

	file_list = sorted(os.listdir(path))
	context = {
		'files': file_list
	}
	return render(request, 'phonesetup/files.html', context)
