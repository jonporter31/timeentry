from django import forms 
from .models import Clients, HourType, Milestones
#import re
#from django.core.validators import RegexValidator


class AddForm(forms.Form):
	#client_name = forms.ModelChoiceField(label="Client",queryset=Clients.objects.all().only('client_name').order_by('client_name'))
	#client_id = forms.ChoiceField(label="Client", required=False, choices='')
	client_id = forms.CharField(label="Client", required=False, widget=forms.Select(choices=[]))
	#milestone_name = forms.ModelChoiceField(label="Milestone",queryset=Milestones.objects.all().only('milestone_name').order_by('milestone_name'),to_field_name='milestone_name')
	#milestone_id = forms.ChoiceField(label="Milestone", required=False)
	milestone_id = forms.CharField(label="Milestone", required=False, widget=forms.Select(choices=[]))
	hours = forms.IntegerField(label="Number of Hours")
	billable = forms.BooleanField(label="Billable?", required=False)
	#hour_type = forms.ModelChoiceField(label="Type of Work",queryset=HourType.objects.all().only('hour_type_desc').order_by('hour_type_desc'))
	#hour_type = forms.ChoiceField(label="Type of Work", required=False)
	hour_type = forms.CharField(label="Type of Work", required=False, widget=forms.Select(choices=[]))

class ClientForm(forms.Form):
	old_client_name = forms.ModelChoiceField(label="Client Name",queryset=Clients.objects.all().only('client_name').order_by('client_name'))
	new_client_name = forms.CharField(label="Update Name",max_length=100)

class MilestoneForm(forms.Form):
	old_milestone_name = forms.ModelChoiceField(label="Milestone Name",queryset=Milestones.objects.all().only('milestone_name').order_by('milestone_name'))
	new_milestone_name = forms.CharField(label="Update Name",max_length=100)

class HourTypeForm(forms.Form):
	old_hour_type_name = forms.ModelChoiceField(label="Hour Type",queryset=HourType.objects.all().only('hour_type_desc').order_by('hour_type_desc'))
	new_hour_type_name = forms.CharField(label="Update Type",max_length=100)

class EditForm(forms.Form):
	entry_id = forms.IntegerField()
	hours = forms.IntegerField(label="Number of Hours")
	billable = forms.BooleanField(label="Billable?",required=False)
	hour_type_desc = forms.ModelChoiceField(label="Type of Work",queryset=HourType.objects.all().only('hour_type_desc').order_by('hour_type_desc'))