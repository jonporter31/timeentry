# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import HttpResponseNotFound
# from django.http import HttpResponse, HttpResponseRedirect
# from django.shortcuts import render, redirect

from .models import Main, Clients, PayRate, CurrentInvoice, Invoice
from appconfig.models import AppConfig
import os
import datetime
from tools.db_util import qtd
from django.core.exceptions import MultipleObjectsReturned
from appconfig.views import get_config, get_config_value
import thread
import logging
#from tools.log_util import get_log_string
import json
import math


from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import Paragraph, Table, TableStyle, Image
from reportlab.lib.pagesizes import letter, cm, landscape, portrait
from django.core.mail import EmailMessage


logger = logging.getLogger('jppapp')

def index(request):
	#for now, this is only accessible from Slack
	return HttpResponseNotFound('<h1>Page not found</h1>')

def get_timeentry():
	# designed to be called from outside to view information
	pass

def time_helper(action,parmsDict,user_name,**kwargs):
	# designed to be called from outside to do any action besides just viewing
	# this function calls other functions based on the action to do the updates/writing
	# i will need to pass date ranges in, need to build that as part of the parser - right now just focus on functionality
	
	# this returns a dictionary containing msg_status, command_status, and slack_text

	logger.debug('time_helper has been called with action '+action)
	logger.debug('time_helper : parmsDict '+json.dumps(parmsDict))
	logger.debug('time_helper : assigning parm variables...')

	client_name = None
	number_of_hours = None
	billable_flag = None
	work_completed_on_date = None
	starting_date = None
	ending_date = None
	period = None
	pay_date = None
	invoice_number = None
	work_desc = None
	project = None
	client_display_name = None
	format_of_date = None
	pay_rate = None
	record_id = None
	table = None
	as_of_date = None
	record_id = None
	pay_rate_id = None
	client_id = None
	invoice_date = None
	email_address = None

	if parmsDict != None:
		try:
			client_name = parmsDict['--client']
			logger.debug('time_helper : setting client_name to '+client_name)
			del parmsDict['--client']
		except KeyError:
			pass

		try:
			email_address = parmsDict['--email']
			logger.debug('time_helper : setting email_address to '+email_address)
			del parmsDict['--email']
		except KeyError:
			pass

		try:
			record_id = parmsDict['--id']
			pay_rate_id = parmsDict['--id']
			client_id = parmsDict['--id']
			logger.debug('time_helper : setting record_id, pay_rate_id, and client_id to '+record_id)
			del parmsDict['--id']
		except KeyError:
			pass

		try:
			record_id = parmsDict['--record']
			logger.debug('time_helper : setting record_id to '+record_id)
			del parmsDict['--record']
		except KeyError:
			pass

		try:
			table = parmsDict['--table']
			logger.debug('time_helper : setting table to '+table)
			del parmsDict['--table']
		except KeyError:
			pass

		try:
			client_name = parmsDict['--code']
			logger.debug('time_helper : setting client_name to '+client_name)
			del parmsDict['--code']
		except KeyError:
			pass

		try:
			number_of_hours = parmsDict['--hours']
			logger.debug('time_helper : setting number_of_hours to '+number_of_hours)
			del parmsDict['--hours']
		except KeyError:
			pass

		try:
			project = parmsDict['--project']
			logger.debug('time_helper : setting project to '+project)
			del parmsDict['--project']
		except KeyError:
			pass

		try:
			billable_flag = parmsDict['--bill']
			logger.debug('time_helper : setting billable_flag to '+billable_flag)
			del parmsDict['--bill']
		except KeyError:
			pass

		try:
			work_completed_on_date = parmsDict['--date']
			pay_date = parmsDict['--date']
			as_of_date = parmsDict['--date']
			invoice_date = parmsDict['--date']
			logger.debug('time_helper : setting work_completed_on_date, pay_date, as_of_date, and invoice_date to '+pay_date)
			del parmsDict['--date']
		except KeyError:
			pass

		try:
			starting_date = parmsDict['--start']
			logger.debug('time_helper : setting starting_date to '+starting_date)
			del parmsDict['--start']
		except KeyError:
			pass

		try:
			ending_date = parmsDict['--end']
			logger.debug('time_helper : setting ending_date to '+ending_date)
			del parmsDict['--end']
		except KeyError:
			pass

		try:
			period = parmsDict['--period']
			logger.debug('time_helper : setting period to '+period)
			del parmsDict['--period']
		except KeyError:
			pass

		try:
			invoice_number = parmsDict['--inv']
			logger.debug('time_helper : setting invoice_number to '+invoice_number)
			del parmsDict['--inv']
		except KeyError:
			pass

		try:
			work_desc = parmsDict['--desc']
			logger.debug('time_helper : setting work_desc to '+work_desc)
			del parmsDict['--desc']
		except KeyError:
			pass

		try:
			format_of_date = parmsDict['--format']
			logger.debug('time_helper : setting format_of_date to '+format_of_date)
			del parmsDict['--format']
		except KeyError:
			pass

		try:
			client_display_name = parmsDict['--name']
			logger.debug('time_helper : setting client_display_name to '+client_display_name)
			del parmsDict['--name']
		except KeyError:
			pass

		try:
			pay_rate = parmsDict['--rate']
			logger.debug('time_helper : setting pay_rate to '+pay_rate)
			del parmsDict['--rate']
		except KeyError:
			pass

	logger.debug('time_helper : finished setting parm variables')

	output_dict = {}

	output_dict['slack_text'] = 'Oh no! There was a problem processing your request. Please verify you are using the correct options and that your values are as intended, then try again. If the issue persists, please contact your administrator.'
	output_dict['msg_status'] = 'error'
	output_dict['command_status'] = 'fail'

	if action == 'doinvoice' and client_name != None and invoice_date != None:
		if email_address == None:
			logger.debug('time_helper : activating doinvoice')
			invoice_number = do_invoice(client_name,period,starting_date,ending_date,transform_string_to_date(invoice_date,format_of_date))
		else:
			logger.debug('time_helper : activating doinvoice and passing email address '+email_address)
			invoice_number = do_invoice(client_name,period,starting_date,ending_date,transform_string_to_date(invoice_date,format_of_date),email_address=email_address)


		if invoice_number:
			logger.debug('time_helper : do_invoice returned True')
			output_dict['msg_status'] = 'success'
			output_dict['command_status'] = 'pass'
			output_dict['slack_text'] = 'Yay! Invoice #' + str(invoice_number) + ' has successfully been queued.'
		else:
			output_dict['msg_status'] = 'success'
			logger.debug('time_helper : do_invoice returned False')
			if get_config('timeentry','longmsgs'):
				output_dict['slack_text'] = 'Oh no! There was a problem gathering records and creating your invoice. Please try again, and if your issue persists, contact your system administrator.'


	elif action == 'createinvoice' and (invoice_number != None or period != None) and invoice_date != None:
		logger.debug('time_helper : activating createinvoice')
		if period == 'current':
			# either period or invoice_number will be populated, period takes precident
			# check db to figure out which is the current invoice
			logger.debug('time_helper : getting current invoice number from CurrentInvoice...')
			current_invoice_record = CurrentInvoice.objects.all()
			for item in current_invoice_record:
				current_invoice = item.invoice_number
			logger.debug('time_helper : current invoice retreived!')
		else:
			logger.debug('time_helper : taking user-provided invoice number...')
			current_invoice = invoice_number

		if create_invoice(current_invoice,transform_string_to_date(invoice_date,format_of_date)):
			logger.debug('time_helper : create_invoice returned True')
			output_dict['msg_status'] = 'success'
			output_dict['command_status'] = 'pass'
			output_dict['slack_text'] = 'Yay! A new invoice was successfully created for invoice number: ' + str(current_invoice) + '.'
		else:
			output_dict['msg_status'] = 'success'
			logger.debug('time_helper : create_invoice returned False')
			if get_config('timeentry','longmsgs'):
				output_dict['slack_text'] = 'Oh no! There was a problem creating your invoice. Please try again, and if your issue persists, contact your system administrator.'

	elif action == 'markpaid' and starting_date != None and ending_date != None and pay_date != None and invoice_number == None:
		logger.debug('time_helper : activating markpaid with start and end dates')
		# will probably need to transform starting_date and ending_date into datetime objects
		# should call central function to understand things like "today" and "2 weeks ago"

		pay_date_transformed = transform_string_to_date(pay_date,format_of_date) # transform pay_date into datetime object

		if mark_paid(pay_date_transformed,starting_date=starting_date,ending_date=ending_date):
			logger.debug('time_helper : mark_invoice returned True')
			output_dict['msg_status'] = 'success'
			output_dict['command_status'] = 'pass'
			output_dict['slack_text'] = 'Yay! You\'ve been paid for the following days: ' + starting_date + ' thru ' + ending_date + '. Congrats!'
		else:
			output_dict['msg_status'] = 'success'
			logger.debug('time_helper : mark_paid returned False')
			if get_config('timeentry','longmsgs'):
				output_dict['slack_text'] = 'Oh no! There was a problem marking your invoice(s) paid. Please try again, and if your issue persists, contact your system administrator.'

	elif action == 'markpaid' and starting_date == None and ending_date == None and pay_date != None and invoice_number != None:
		logger.debug('time_helper : activating markpaid with invoice number')
		# will probably need to transform starting_date and ending_date into datetime objects

		pay_date_transformed = transform_string_to_date(pay_date,format_of_date) # transform pay_date into datetime object

		if mark_paid(pay_date_transformed,invoice_number=invoice_number):
			logger.debug('time_helper : mark_paid returned True')
			output_dict['msg_status'] = 'success'
			output_dict['command_status'] = 'pass'
			output_dict['slack_text'] = 'Yay! Invoice # ' + invoice_number + ' has been paid. Congrats!'
		else:
			output_dict['msg_status'] = 'success'
			logger.debug('time_helper : mark_paid returned False')
			if get_config('timeentry','longmsgs'):
				output_dict['slack_text'] = 'Oh no! There was a problem marking your invoice(s) paid. Please try again, and if your issue persists, contact your system administrator.'

	elif action == 'add' and client_name != None and number_of_hours != None and billable_flag != None and work_completed_on_date != None and work_desc != None:
		logger.debug('time_helper : activating add')

		# it is intentional that 'project' is not included in the if statement b/c project is not required and can be passed on as None

		new = add_record(client_name,number_of_hours,billable_flag,transform_string_to_date(work_completed_on_date,format_of_date),work_desc,project)
		if new:
			logger.debug('time_helper : add_record returned new record_id '+str(new))
			output_dict['msg_status'] = 'success'
			output_dict['command_status'] = 'pass'
			if project != None:
				output_dict['slack_text'] = 'Yay! ' + number_of_hours + ' hour(s) was/were charged to ' + get_client_display_name(client_name) + ' for completing: ' + work_desc + ' on ' + project + '.'
				# for some reason it's not getting to this point.... somehow getting stuck sthutting it down for tonight
				#print(output_dict)
			else:
				output_dict['slack_text'] = 'Yay! ' + number_of_hours + ' hour(s) were charged to ' + get_client_display_name(client_name) + ' for completing: ' + work_desc + '.'
		else:
			output_dict['msg_status'] = 'success'
			logger.debug('time_helper : add_record returned False')
			if get_config('timeentry','longmsgs'):
				output_dict['slack_text'] = 'Oh no! There was a problem adding your new record. Please try again, and if your issue persists, contact your system administrator.'

	elif action == 'addclient' and client_name != None and client_display_name != None:
		logger.debug('time_helper : activating addclient')

		new = add_client(client_name,client_display_name)
		if new:
			logger.debug('time_helper : add_client returned new client_id '+str(new))
			output_dict['msg_status'] = 'success'
			output_dict['command_status'] = 'pass'
			output_dict['slack_text'] = 'Yay! A new client was added: ' + client_display_name + ' / ' + client_name
		else:
			output_dict['msg_status'] = 'success'
			logger.debug('time_helper : add_client returned False')
			if get_config('timeentry','longmsgs'):
				output_dict['slack_text'] = 'Oh no! There was a problem adding your new client. Please try again, and if your issue persists, contact your system administrator.'


	elif action == 'addpay' and client_name != None and starting_date != None and ending_date != None and pay_rate != None:
		logger.debug('time_helper : activating addpay')


		new = add_payrate(client_name,pay_rate,transform_string_to_date(starting_date,format_of_date),transform_string_to_date(ending_date,format_of_date),project)
		if new:
			logger.debug('time_helper : add_payrate returned new pay_rate_id '+str(new))
			output_dict['msg_status'] = 'success'
			output_dict['command_status'] = 'pass'
			output_dict['slack_text'] = 'Yay! A new pay rate was added for ' + client_name + '.'
		else:
			output_dict['msg_status'] = 'success'
			logger.debug('time_helper : add_payrate returned False')
			if get_config('timeentry','longmsgs'):
				output_dict['slack_text'] = 'Oh no! There was a problem adding your new pay rate. Please try again, and if your issue persists, contact your system administrator.'

	elif action == 'update' and record_id != None:
		logger.debug('time_helper : activating update')

		# it is intentional that 'project' is not included in the if statement b/c project is not required and can be passed on as None
		if work_completed_on_date != None:
			work_completed_on_date = transform_string_to_date(work_completed_on_date,format_of_date)

		updated = update_record(record_id,client_name,project,number_of_hours,work_desc,work_completed_on_date,billable_flag)
		if updated:
			logger.debug('time_helper : update_record returned updated record_id '+str(updated))
			output_dict['msg_status'] = 'success'
			output_dict['command_status'] = 'pass'
			output_dict['slack_text'] = 'Yay! Record ' + record_id + ' was successfully updated.'
		else:
			output_dict['msg_status'] = 'success'
			logger.debug('time_helper : update_record returned False')
			if get_config('timeentry','longmsgs'):
				output_dict['slack_text'] = 'Oh no! There was a problem updating your record. Please try again, and if your issue persists, contact your system administrator.'

	elif action == 'updateclient' and client_id != None:
		logger.debug('time_helper : activating updateclient')
		# it is intentional that 'project' is not included in the if statement b/c project is not required and can be passed on as None
		if work_completed_on_date != None:
			work_completed_on_date = transform_string_to_date(work_completed_on_date,format_of_date)

		updated = update_client(client_id,client_name,client_display_name)
		if updated:
			logger.debug('time_helper : update_client returned updated client_id '+str(updated))
			output_dict['msg_status'] = 'success'
			output_dict['command_status'] = 'pass'
			output_dict['slack_text'] = 'Yay! client ' + client_id + ' was successfully updated.'
		else:
			output_dict['msg_status'] = 'success'
			logger.debug('time_helper : update_client returned False')
			if get_config('timeentry','longmsgs'):
				output_dict['slack_text'] = 'Oh no! There was a problem updating your client. Please try again, and if your issue persists, contact your system administrator.'

	elif action == 'updatepay' and pay_rate_id != None:
		logger.debug('time_helper : activating updatepay')
		# it is intentional that 'project' is not included in the if statement b/c project is not required and can be passed on as None
		if work_completed_on_date != None:
			work_completed_on_date = transform_string_to_date(work_completed_on_date,format_of_date)

		updated = update_payrate(pay_rate_id,client_name,project,pay_rate,starting_date,ending_date)
		if updated:
			logger.debug('time_helper : update_payrate returned updated pay_rate_id '+str(updated))
			output_dict['msg_status'] = 'success'
			output_dict['command_status'] = 'pass'
			output_dict['slack_text'] = 'Yay! Pay rate ' + pay_rate_id + ' was successfully updated.'
		else:
			output_dict['msg_status'] = 'success'
			logger.debug('time_helper : update_payrate returned False')
			if get_config('timeentry','longmsgs'):
				output_dict['slack_text'] = 'Oh no! There was a problem updating your pay rate. Please try again, and if your issue persists, contact your system administrator.'

	elif action == 'delete' and record_id != None:
		logger.debug('time_helper : activating delete')
		# it is intentional that 'project' is not included in the if statement b/c project is not required and can be passed on as None

		if delete('record',record_id):
			logger.debug('time_helper : successfully deleted record with id '+str(record_id))
			output_dict['msg_status'] = 'success'
			output_dict['command_status'] = 'pass'
			output_dict['slack_text'] = 'Yay! Record ' + record_id + ' was successfully deleted.'
		else:
			output_dict['msg_status'] = 'success'
			logger.debug('time_helper : delete_record returned False')
			if get_config('timeentry','longmsgs'):
				output_dict['slack_text'] = 'Oh no! There was a problem deleting your record. Please try again, and if your issue persists, contact your system administrator.'


	elif action == 'deleteclient' and client_id != None:
		logger.debug('time_helper : activating deleteclient')
		# it is intentional that 'project' is not included in the if statement b/c project is not required and can be passed on as None

		if delete('client',client_id):
			logger.debug('time_helper : successfully deleted client with id '+str(client_id))
			output_dict['msg_status'] = 'success'
			output_dict['command_status'] = 'pass'
			output_dict['slack_text'] = 'Yay! Client ' + client_id + ' was successfully deleted.'
		else:
			output_dict['msg_status'] = 'success'
			logger.debug('time_helper : delete_client returned False')
			if get_config('timeentry','longmsgs'):
				output_dict['slack_text'] = 'Oh no! There was a problem deleting your client. Please try again, and if your issue persists, contact your system administrator.'

	elif action == 'deletepay' and pay_rate_id != None:
		logger.debug('time_helper : activating deleteclient')
		# it is intentional that 'project' is not included in the if statement b/c project is not required and can be passed on as None

		if delete('payrate',pay_rate_id):
			logger.debug('time_helper : successfully deleted payrate with id '+str(pay_rate_id))
			output_dict['msg_status'] = 'success'
			output_dict['command_status'] = 'pass'
			output_dict['slack_text'] = 'Yay! Pay rate ' + pay_rate_id + ' was successfully deleted.'
		else:
			output_dict['msg_status'] = 'success'
			logger.debug('time_helper : delete_payrate returned False')
			if get_config('timeentry','longmsgs'):
				output_dict['slack_text'] = 'Oh no! There was a problem deleting your pay rate. Please try again, and if your issue persists, contact your system administrator.'

	elif action == 'view' and client_name != None and ((starting_date != None and ending_date != None) or (period != None)):
		logger.debug('time_helper : activating view')

		if period != None:
			logger.debug('time_helper : calling view_records using client and period...')
			display_records = view_records(client_name,period=period)
		else:
			logger.debug('time_helper : calling view_records using client and start / end dates...')
			display_records = view_records(client_name,starting_date=starting_date,ending_date=ending_date)

		if display_records:
			logger.debug('time_helper : records successfully returned '+str(len(display_records.keys())))
			output_dict['msg_status'] = 'success'
			output_dict['command_status'] = 'pass'
			output_dict['slack_text'] = 'The following record(s) were returned for the given criteria:\n*ID | Work Date | Work Description | Project | Billable | Hours | Dollars*\n-------------------------------------------------------------------------------'
			rec_num = 0
			for key in display_records.keys():
				if key != 'total':
					output_dict['slack_text'] += '\n' + str(display_records[rec_num]['record_id']) + ' | ' + transform_date_to_string(display_records[rec_num]['work_date'],format_of_date) + ' | ' + str(display_records[rec_num]['work_desc']) + ' | ' + str(display_records[rec_num]['project_name']) + ' | ' + str(display_records[rec_num]['billable_flag']) + ' | ' + str(display_records[rec_num]['hours']) + ' | ' + str(display_records[rec_num]['dollars'])
					rec_num += 1
			output_dict['slack_text'] += '\n*Last Week\'s Summary:* ' + str(display_records['total']['week_1_hours']) + ' hour(s) | ' + str(display_records['total']['week_1_disp_dollars'])
			output_dict['slack_text'] += '\n*This Week\'s Summary:* ' + str(display_records['total']['week_2_hours']) + ' hour(s) | ' + str(display_records['total']['week_2_disp_dollars'])
			if display_records['total']['other_week_hours'] != 0.00:
				output_dict['slack_text'] += '\n*All Other Week\'s Summary:* ' + str(display_records['total']['other_week_hours']) + ' hour(s) | ' + str(display_records['total']['other_week_disp_dollars'])
			output_dict['slack_text'] += '\n*TOTAL SUMMARY:* ' + str(display_records['total']['total_hours']) + ' hour(s) | ' + str(display_records['total']['total_disp_dollars'])
		else:
			output_dict['msg_status'] = 'success'
			logger.debug('time_helper : view_records returned False')
			if get_config('timeentry','longmsgs'):
				output_dict['slack_text'] = 'Oh no! There was a problem gathering your records for viewing. Please try again, and if your issue persists, contact your system administrator.'

	elif action == 'viewpay' and client_name != None:
		logger.debug('time_helper : activating viewpay')

		logger.debug('time_helper : querying payrates using client...')
		display_records = view_payrate(client_name, project, as_of_date)

		if display_records:
			logger.debug('time_helper : records successfully returned '+str(len(display_records.keys())))
			output_dict['msg_status'] = 'success'
			output_dict['command_status'] = 'pass'
			output_dict['slack_text'] = 'The following record(s) were returned for the given criteria:\n*ID | Project | Rate | Valid From | Valid To*\n---------------------------------------------'
			rec_num = 0
			for key in display_records.keys():
				#print(display_records[rec_num])
				output_dict['slack_text'] += '\n' + str(display_records[rec_num]['pay_rate_id']) + ' | ' + str(display_records[rec_num]['project_name']) + ' | ' + '${:,.2f}'.format(display_records[rec_num]['hourly_rate']) + ' | ' + str(display_records[rec_num]['valid_from'].split(' ',1)[0]) + ' | ' + str(display_records[rec_num]['valid_to'].split(' ',1)[0])
				rec_num += 1
		else:
			output_dict['msg_status'] = 'success'
			logger.debug('time_helper : view_payrate returned False')
			if get_config('timeentry','longmsgs'):
				output_dict['slack_text'] = 'Oh no! There was a problem gathering your pay rates for viewing. Please try again, and if your issue persists, contact your system administrator.'

	elif action == 'viewinv':
		logger.debug('time_helper : activating viewinv')

		logger.debug('time_helper : querying invoice based on user inputs...')
		if invoice_number != None:
			logger.debug('time_helper : using invoice_number - '+str(invoice_number))
			display_records = view_invoice(invoice_number=invoice_number)
		elif client_name != None and (starting_date == None or ending_date == None):
			logger.debug('time_helper : using client_name - '+str(client_name))
			display_records = view_invoice(client_name=client_name)
		elif client_name != None and starting_date != None and ending_date != None:
			logger.debug('time_helper : using client_name / starting_date / ending_date - '+str(client_name)+' / '+str(starting_date)+' / '+str(ending_date))
			display_records = view_invoice(client_name=client_name,starting_date=starting_date,ending_date=ending_date)
		elif starting_date != None and ending_date != None:
			logger.debug('time_helper : using starting_date / ending_date - '+str(starting_date)+' / '+str(ending_date))
			display_records = view_invoice(starting_date=starting_date,ending_date=ending_date)
		else:
			logger.debug('time_helper : no user inputs - returning all records!')
			display_records = view_invoice()


		if display_records:
			logger.debug('time_helper : records successfully returned '+str(len(display_records.keys())))
			output_dict['msg_status'] = 'success'
			output_dict['command_status'] = 'pass'
			output_dict['slack_text'] = 'The following record(s) were returned for the given criteria:\n*Full Inv. # | Client Name | Invoice Date | Total Hours | Total Dollars | Paid? | Paid Date*\n---------------------------------------------------------------------------------------------'
			rec_num = 0
			total_paid_dollars = 0
			total_outstanding_dollars = 0
			for key in display_records.keys():
				#print(display_records[rec_num])
				if display_records[rec_num]['paid_date'] == None:
					paid_date_formatted = 'Not Paid'
				else:
					paid_date_formatted = str(display_records[rec_num]['paid_date'].split(' ',1)[0])

				if display_records[rec_num]['paid_flag'] == 'y':
					paid_flag_formatted = 'Yes'
					total_paid_dollars += int(display_records[rec_num]['total_dollars'])
				else:
					paid_flag_formatted = 'No'
					total_outstanding_dollars += int(display_records[rec_num]['total_dollars'])

				
				output_dict['slack_text'] += '\n' + str(display_records[rec_num]['full_invoice_id']) + ' | ' + str(get_client_display_name_from_id(display_records[rec_num]['client_id_id'])) + ' | ' + str(display_records[rec_num]['invoice_date'].split(' ',1)[0]) + ' | ' + '${:,.2f}'.format(display_records[rec_num]['total_hours']) + ' | ' + '${:,.2f}'.format(display_records[rec_num]['total_dollars']) + ' | ' + paid_flag_formatted + ' | ' + paid_date_formatted
				rec_num += 1
			output_dict['slack_text'] += '\n*SUMMARY*' + '\nTotal Dollars Paid: '+'*${:,.2f}'.format(total_paid_dollars) + '*\nTotal Outstanding Dollars: '+'*${:,.2f}'.format(total_outstanding_dollars)+'*'
		else:
			output_dict['msg_status'] = 'success'
			logger.debug('time_helper : view_invoice returned False')
			if get_config('timeentry','longmsgs'):
				output_dict['slack_text'] = 'Oh no! There was a problem gathering your invoices for viewing. Please try again, and if your issue persists, contact your system administrator.'


	elif action == 'viewclients':
		logger.debug('time_helper : activating viewclients')

		logger.debug('time_helper : querying clients...')
		display_records = view_clients(client_name)

		if display_records:
			logger.debug('time_helper : records successfully returned '+str(len(display_records.keys())))
			output_dict['msg_status'] = 'success'
			output_dict['command_status'] = 'pass'
			output_dict['slack_text'] = 'The following record(s) were returned for the given criteria:\n*ID | Client Short Name | Client Long Name*\n------------------------------------------------'
			rec_num = 0
			for key in display_records.keys():
				output_dict['slack_text'] += '\n' + str(display_records[rec_num]['client_id']) + ' | ' + str(display_records[rec_num]['client_name']) + ' | ' + str(display_records[rec_num]['client_display_name'])
				rec_num += 1
		else:
			output_dict['msg_status'] = 'success'
			logger.debug('time_helper : view_clients returned False')
			if get_config('timeentry','longmsgs'):
				output_dict['slack_text'] = 'Oh no! There was a problem gathering your clients for viewing. Please try again, and if your issue persists, contact your system administrator.'

	elif action == 'purge' and table != None:
		logger.debug('time_helper : activating purge')
		if purge(table):
			logger.debug('time_helper : all records that were marked for deletion have been successfully purged from '+str(table)+' table!')
			output_dict['msg_status'] = 'success'
			output_dict['command_status'] = 'pass'
			output_dict['slack_text'] = 'Yay! Records for ' + table + ' table(s) have been purged.'
		else:
			output_dict['msg_status'] = 'success'
			logger.debug('time_helper : purge returned False')
			if get_config('timeentry','longmsgs'):
				output_dict['slack_text'] = 'Oh no! There was a problem purging your records. Please try again, and if your issue persists, contact your system administrator.'

	elif action == 'revinvoice' and invoice_number != None:
		logger.debug('time_helper : activating reverseinvoice')
		if reverse_invoice(invoice_number):
			logger.debug('time_helper : invoice '+str(invoice_number)+' successfully reversed!')
			output_dict['msg_status'] = 'success'
			output_dict['command_status'] = 'pass'
			output_dict['slack_text'] = 'Yay! Invoice #' + str(invoice_number) + ' successfully reversed.'
		else:
			output_dict['msg_status'] = 'success'
			logger.debug('time_helper : reverse_invoice returned False')
			if get_config('timeentry','longmsgs'):
				output_dict['slack_text'] = 'Oh no! There was a problem reversing your invoice. Please try again, and if your issue persists, contact your system administrator.'

	elif action == 'sendinvoice' and invoice_number != None and email_address != None:
		logger.debug('time_helper : activating sendinvoice')
		email_sent = False
		try:
			logger.debug('time_helper : attempting to get full_invoice_id based on provided invoice_number...')
			invoice_record = Invoice.objects.get(invoice_number=invoice_number)
			#build this call in separate thread
			#build way to get default client email - populate client name in that case since you'll have to hit Clients table anyways
			logger.debug('time_helper : invoice record returned! calling email_invoice_pdf with provided email_address...')
			email_sent = email_invoice_pdf(invoice_record.full_invoice_id,to_address=email_address)
		except Invoice.DoesNotExist:
			logger.debug('time_helper : exception - no invoice record returned for provided invoice_number')
			email_sent = False
		except MultipleObjectsReturned:
			logger.debug('time_helper : exception - multiple invoice records returned for provided invoice_number - check database')
			email_sent = False
		
		if email_sent:

			logger.debug('time_helper : invoice '+str(invoice_number)+' successfully sent to '+str(email_address))
			output_dict['msg_status'] = 'success'
			output_dict['command_status'] = 'pass'
			output_dict['slack_text'] = 'Yay! Invoice #' + str(invoice_number) + ' successfully sent to ' + str(email_address) + '.'
		else:
			output_dict['msg_status'] = 'success'
			logger.debug('time_helper : email not sent')
			if get_config('timeentry','longmsgs'):
				output_dict['slack_text'] = 'Oh no! There was a problem emailing your invoice. Please try again, and if your issue persists, contact your system administrator.'

	elif action == 'help':
		logger.debug('time_helper : activating help - returning standard help message')
		output_dict['msg_status'] = 'success'
		output_dict['command_status'] = 'pass'
		help_message = '*Welcome to Time Entry v2.5*\n'
		help_message += '\nAvailable commands and expected inputs:'
		help_message += '\n*doinvoice*: gathers records for invoicing, and configurably auto-creates invoice'
		help_message += '\n----> _name (client short name), date (invoice date), period or start/end (i.e. \'current\' or beginning and ending dates), email (optional, client email address to deliver invoice)_'
		help_message += '\n*createinvoice*: creates the invoice records, and configurably auto-generating the pdf and delivering to email'
		help_message += '\n----> _inv (invoice number), period or start/end (i.e. \'current\' or beginning and ending dates), email (optional, client email address to deliver invoice)_'
		help_message += '\n*markpaid*: updates records to reflect payment received.'
		help_message += '\n----> _date (pay date), either inv (invoice number) or start/end (beginning and ending dates)_'
		help_message += '\n*sendinvoice*: emails an already created invoice to a provided address'
		help_message += '\n----> _inv (invoice number), email (email address to deliver invoice)_'
		help_message += '\n*revinvoice*: undoes invoicing updates for a recently created invoice in the event of any errors'
		help_message += '\n----> _inv (invoice number)_'
		help_message += '\n*viewinv*: returns invoice header information'
		help_message += '\n----> _either none, just inv (invoice number), just name (client short name), just start/end (beginning and ending dates), or name and start/end_'
		help_message += '\n*view*: returns individual record level information'
		help_message += '\n----> _name (client short name), period or start/end (i.e. \'current\' or beginning and ending dates)_'
		help_message += '\n*viewpay*: returns pay rate information'
		help_message += '\n----> _name (client short name)_'
		help_message += '\n*viewclients*: returns client information'
		help_message += '\n----> _none_'
		help_message += '\n*add*: adds a new time entry record'
		help_message += '\n----> _name (client short name), hours (number of hours worked), desc (description of work), date (date work performed MM/DD/YY), bill (billable work, y/n)_'
		help_message += '\n*addpay*: adds a new pay rate for a given client'
		help_message += '\n----> _name (client short name), rate (pay rate), start/end (beginning and ending validity dates)_'
		help_message += '\n*addclient*: adds a new client to the system'
		help_message += '\n----> _code (client short name), name (client display name)_'
		help_message += '\n*update*: updates a given record based on provided id (use view first)'
		help_message += '\n----> _id or record, then the object(s) to update: name, hours, desc, date, bill_'
		help_message += '\n*updatepay*: updates a given pay rate record based on provided id (use viewpay first)'
		help_message += '\n----> _id or record, then the object(s) to update: name, rate, start/end_'
		help_message += '\n*updateclient*: updates a given client record based on provided id (use viewclients first)'
		help_message += '\n----> _id or record, then the object(s) to update: code, name_'
		help_message += '\n*delete*: removes a given record from the system (i.e. marks for deletion)'
		help_message += '\n----> _id or record_'
		help_message += '\n*deletepay*: removes a given pay rate from the system (i.e. marks for deletion)'
		help_message += '\n----> _id or record_'
		help_message += '\n*deleteclient*: removes a given client from the system (i.e. marks for deletion)'
		help_message += '\n----> _id or record_'
		help_message += '\n*purge*: deletes all records marked for deletion from the provided table'
		help_message += '\n----> _table (table to purge or \'all\')_'

		output_dict['slack_text'] = help_message




	else:
		logger.debug('time_helper : exception block triggered')
		if action == None:
			logger.debug('time_helper : exception - missing action')
			output_dict['msg_status'] = 'success'
			output_dict['slack_text'] = 'Oh no! You haven\'t entered any action - please try again.'
		elif parmsDict == None:
			logger.debug('time_helper : exception - missing parmsDict')
			output_dict['msg_status'] = 'success'
			output_dict['slack_text'] = 'Oh no! You haven\'t entered any parameters - please try again.'
		elif action not in ['doinvoice','createinvoice','markpaid','add','addclient','addpay','update','updateclient','updatepay','delete','deleteclient','deletepay','purge','view','viewclients','viewpay']:
			logger.debug('time_helper ; exception - invalid action '+str(action))
			output_dict['msg_status'] = 'success'
			output_dict['slack_text'] = 'Oh no! You entered an action that is not valid - please try again (hint: type _/time help_ for more info).'


		elif action == 'doinvoice':
			if client_name == None:
				logger.debug('time_helper : exception - missing client_name when calling doinvoice')
				output_dict['msg_status'] = 'success'
				output_dict['slack_text'] = 'Oh no! The "client" parameter (client code) is required when calling doinvoice - please try again.'

			elif invoice_date == None:
				logger.debug('time_helper : exception - missing invoice_date when calling doinvoice')
				output_dict['msg_status'] = 'success'
				output_dict['slack_text'] = 'Oh no! The "date" parameter (invoice date) is required when calling doinvoice - please try again.'

			else:
				logger.debug('time_helper : exception - UNCAUGHT ERROR resulting from doinvoice')
				output_dict['slack_text'] = 'An unknown error occured when calling doinvoice - please try again or contact your administrator.'

		elif action == 'sendinvoice':
			if invoice_number == None:
				logger.debug('time_helper : exception - missing invoice_number when calling sendinvoice')
				output_dict['msg_status'] = 'success'
				output_dict['slack_text'] = 'Oh no! The "inv" parameter (invoice number) is required when calling sendinvoice - please try again.'

			elif email_address == None:
				logger.debug('time_helper : exception - missing email_address when calling sendinvoice')
				output_dict['msg_status'] = 'success'
				output_dict['slack_text'] = 'Oh no! The "email" parameter (email address) is required when calling sendinvoice - please try again.'

			else:
				logger.debug('time_helper : exception - UNCAUGHT ERROR resulting from sendinvoice')
				output_dict['slack_text'] = 'An unknown error occured when calling sendinvoice - please try again or contact your administrator.'

		elif action == 'createinvoice':
			if invoice_date == None:
				logger.debug('time_helper ; exception - missing invoice_date when calling createinvoice')
				output_dict['msg_status'] = 'success'
				output_dict['slack_text'] = 'Oh no! The "date" parameter (invoice date) is required when calling createinvoice - please try again.'

			elif period == None and invoice_number == None:
				logger.debug('time_helper : exception - missing period or invoice_number when calling createinvoice')
				output_dict['msg_status'] = 'success'
				output_dict['slack_text'] = 'Oh no! The "period" or "inv" parameter (either period or invoice number) is required when calling createinvoice - please try again.'

			else:
				logger.debug('time_helper : exception - UNCAUGHT ERROR resulting from createinvoice')
				output_dict['slack_text'] = 'An unknown error occured when calling createinvoice - please try again or contact your administrator.'

		elif action == 'markpaid':
			if pay_date == None:
				logger.debug('time_helper : exception - missing pay_date when calling markpaid')
				output_dict['msg_status'] = 'success'
				output_dict['slack_text'] = 'Oh no! The "date" parameter (pay date) is required when calling markpaid - please try again.'

			elif invoice_number == None and starting_date == None and ending_date == None:
				logger.debug('time_helper : exception - missing invoice number or start / end dates when calling markpaid')
				output_dict['msg_status'] = 'success'
				output_dict['slack_text'] = 'Oh no! The "inv" or "start" and "end" parameters (either invoice number or start / end dates) is required when calling markpaid - please try again.'

			elif starting_date == None and ending_date != None:
				logger.debug('time_helper : exception - missing starting_date when calling markpaid')
				output_dict['msg_status'] = 'success'
				output_dict['slack_text'] = 'Oh no! The "start" parameter (starting date) is required when calling markpaid - please try again.'

			elif starting_date != None and ending_date == None:
				logger.debug('time_helper : exception - missing ending_date when calling markpaid')
				output_dict['msg_status'] = 'success'
				output_dict['slack_text'] = 'Oh no! The "end" parameter (ending date) is required when calling markpaid - please try again.'

			else:
				logger.debug('time_helper : exception - UNCAUGHT ERROR resulting from markpaid')
				output_dict['slack_text'] = 'An unknown error occured when calling markpaid - please try again or contact your administrator.'

		elif action == 'add':
			if client_name == None:
				logger.debug('time_helper : exception - missing client_name when calling add')
				output_dict['msg_status'] = 'success'
				output_dict['slack_text'] = 'Oh no! The "client" parameter (client code) is required when calling add - please try again.'

			elif number_of_hours == None:
				logger.debug('time_helper : exception - missing number_of_hours when calling add')
				output_dict['msg_status'] = 'success'
				output_dict['slack_text'] = 'Oh no! The "hours" parameter (number of hours) is required when calling add - please try again.'

			elif billable_flag == None:
				logger.debug('time_helper : exception - missing billable_flag when calling add')
				output_dict['msg_status'] = 'success'
				output_dict['slack_text'] = 'Oh no! The "bill" parameter (billable flag) is required when calling add - please try again.'

			elif work_completed_on_date == None:
				logger.debug('time_helper : exception - missing work_completed_on_date when calling add')
				output_dict['msg_status'] = 'success'
				output_dict['slack_text'] = 'Oh no! The "date" parameter (work completed on date) is required when calling add - please try again.'

			elif work_desc == None:
				logger.debug('time_helper : exception - missing work_desc when calling add')
				output_dict['msg_status'] = 'success'
				output_dict['slack_text'] = 'Oh no! The "desc" parameter (description of work) is required when calling add - please try again.'

			else:
				logger.debug('time_helper : exception - UNCAUGHT ERROR resulting from add')
				output_dict['slack_text'] = 'An unknown error occured when calling add - please try again or contact your administrator.'

		elif action == 'addclient':
			if client_name == None:
				logger.debug('time_helper : exception - missing client_name when calling addclient')
				output_dict['msg_status'] = 'success'
				output_dict['slack_text'] = 'Oh no! The "client" parameter (client code) is required when calling addclient - please try again.'

			elif client_display_name == None:
				logger.debug('time_helper : exception - missing client_display_name when calling addclient')
				output_dict['msg_status'] = 'success'
				output_dict['slack_text'] = 'Oh no! The "name" parameter (client dislpay name) is required when calling addclient - please try again.'

			else:
				logger.debug('time_helper : exception - UNCAUGHT ERROR resulting from addclient')
				output_dict['slack_text'] = 'An unknown error occured when calling addclient - please try again or contact your administrator.'

		elif action == 'addpay':
			if client_name == None:
				logger.debug('time_helper : exception - missing client_name when calling addpay')
				output_dict['msg_status'] = 'success'
				output_dict['slack_text'] = 'Oh no! The "client" parameter (client code) is required when calling addpay - please try again.'

			elif starting_date == None:
				logger.debug('time_helper : exception - missing starting_date when calling addpay')
				output_dict['msg_status'] = 'success'
				output_dict['slack_text'] = 'Oh no! The "start" parameter (starting date) is required when calling addpay - please try again.'

			elif ending_date == None:
				logger.debug('time_helper : exception - missing ending_date when calling addpay')
				output_dict['msg_status'] = 'success'
				output_dict['slack_text'] = 'Oh no! The "end" parameter (ending date) is required when calling addpay - please try again.'

			elif pay_rate == None:
				logger.debug('time_helper : exception - missing pay_rate when calling addpay')
				output_dict['msg_status'] = 'success'
				output_dict['slack_text'] = 'Oh no! The "rate" parameter (pay rate) is required when calling addpay - please try again.'

			else:
				logger.debug('time_helper : exception - UNCAUGHT ERROR resulting from addpay')
				output_dict['slack_text'] = 'An unknown error occured when calling addpay - please try again or contact your administrator.'

		elif action == 'update':
			if record_id == None:
				logger.debug('time_helper : exception - missing record_id when calling update')
				output_dict['msg_status'] = 'success'
				output_dict['slack_text'] = 'Oh no! The "id" parameter (record id) is required when calling update - please try again (hint: use view first to get ID).'

			else:
				logger.debug('time_helper : exception - UNCAUGHT ERROR resulting from update')
				output_dict['slack_text'] = 'An unknown error occured when calling update - please try again or contact your administrator.'

		elif action == 'updateclient':
			if client_id == None:
				logger.debug('time_helper : exception - missing client_id when calling updateclient')
				output_dict['msg_status'] = 'success'
				output_dict['slack_text'] = 'Oh no! The "id" parameter (client id) is required when calling updateclient - please try again (hint: use view first to get ID).'

			else:
				logger.debug('time_helper : exception - UNCAUGHT ERROR resulting from updateclient')
				output_dict['slack_text'] = 'An unknown error occured when calling updateclient - please try again or contact your administrator.'

		elif action == 'updatepay':
			if pay_rate_id == None:
				logger.debug('time_helper : exception - missing pay_rate_id when calling updatepay')
				output_dict['msg_status'] = 'success'
				output_dict['slack_text'] = 'Oh no! The "id" parameter (pay rate id) is required when calling updatepay - please try again (hint: use view first to get ID).'

			else:
				logger.debug('time_helper : exception - UNCAUGHT ERROR resulting from updatepay')
				output_dict['slack_text'] = 'An unknown error occured when calling updatepay - please try again or contact your administrator.'

		elif action == 'delete':
			if record_id == None:
				logger.debug('time_helper : exception - missing record_id when calling delete')
				output_dict['msg_status'] = 'success'
				output_dict['slack_text'] = 'Oh no! The "id" parameter (record id) is required when calling delete - please try again (hint: use view first to get ID).'

			else:
				logger.debug('time_helper : exception - UNCAUGHT ERROR resulting from delete')
				output_dict['slack_text'] = 'An unknown error occured when calling delete - please try again or contact your administrator.'

		elif action == 'deleteclient':
			if client_id == None:
				logger.debug('time_helper : exception - missing client_id when calling deleteclient')
				output_dict['msg_status'] = 'success'
				output_dict['slack_text'] = 'Oh no! The "id" parameter (client id) is required when calling deleteclient - please try again (hint: use view first to get ID).'

			else:
				logger.debug('time_helper : exception - UNCAUGHT ERROR resulting from deleteclient')
				output_dict['slack_text'] = 'An unknown error occured when calling deleteclient - please try again or contact your administrator.'

		elif action == 'deletepay':
			if pay_rate_id == None:
				logger.debug('time_helper : exception - missing pay_rate_id when calling deletepay')
				output_dict['msg_status'] = 'success'
				output_dict['slack_text'] = 'Oh no! The "id" parameter (pay rate id) is required when calling deletepay - please try again (hint: use view first to get ID).'

			else:
				logger.debug('time_helper : exception - UNCAUGHT ERROR resulting from deletepay')
				output_dict['slack_text'] = 'An unknown error occured when calling deletepay - please try again or contact your administrator.'

		elif action == 'revinvoice':
			if invoice_number == None:
				logger.debug('time_helper : exception - missing invoice_number when calling reverse_invoice')
				output_dict['msg_status'] = 'success'
				output_dict['slack_text'] = 'Oh no! The "inv" parameter (invoice number) is required when calling revinvoice - please try again (hint: use view first to get ID).'

			else:
				logger.debug('time_helper : exception - UNCAUGHT ERROR resulting from reverse_invoice')
				output_dict['slack_text'] = 'An unknown error occured when calling revinvoice - please try again or contact your administrator.'

		elif action == 'view':
			if client_name == None:
				logger.debug('time_helper : exception - missing client_name when calling view')
				output_dict['msg_status'] = 'success'
				output_dict['slack_text'] = 'Oh no! The "client" parameter (client code) is required when calling view - please try again.'

			elif period == None and starting_date == None and ending_date == None:
				logger.debug('time_helper : exception - missing period or start / end dates when calling view')
				output_dict['msg_status'] = 'success'
				output_dict['slack_text'] = 'Oh no! The "period" or "start" and "end" parameters (period or start / end dates) is required when calling view - please try again.'

			elif starting_date == None and ending_date != None:
				logger.debug('time_helper : exception - missing period or start / end dates when calling view')
				output_dict['msg_status'] = 'success'
				output_dict['slack_text'] = 'Oh no! The "start" parameter (start date) is required when calling view - please try again.'

			elif starting_date != None and ending_date == None:
				logger.debug('time_helper : exception - missing period or start / end dates when calling view')
				output_dict['msg_status'] = 'success'
				output_dict['slack_text'] = 'Oh no! The "end" parameter (end date) is required when calling view - please try again.'

			else:
				logger.debug('time_helper : exception - UNCAUGHT ERROR resulting from view')
				output_dict['slack_text'] = 'An unknown error occured when calling view - please try again or contact your administrator.'

		elif action == 'viewpay':
			if client_name == None:
				logger.debug('time_helper : exception - missing client_name when calling viewpay')
				output_dict['msg_status'] = 'success'
				output_dict['slack_text'] = 'Oh no! The "client" parameter (client code) is required when calling view - please try again.'

			else:
				logger.debug('time_helper : exception - UNCAUGHT ERROR resulting from viewpay')
				output_dict['slack_text'] = 'An unknown error occured when calling viewpay - please try again or contact your administrator.'

		elif action == 'viewclients':
			logger.debug('time_helper : exception - UNCAUGHT ERROR resulting from viewclients')
			output_dict['slack_text'] = 'An unknown error occured when calling viewclients - please try again or contact your administrator.'

		elif action == 'purge':
			if table == None:
				logger.debug('time_helper : exception - missing table when calling purge')
				output_dict['msg_status'] = 'success'
				output_dict['slack_text'] = 'Oh no! The "table" parameter is required when calling purge - please try again.'

			else:
				logger.debug('time_helper : exception - UNCAUGHT ERROR resulting from purge')
				output_dict['slack_text'] = 'An unknown error occured when calling purge - please try again or contact your administrator.'

		else:
			logger.debug('time_helper : unknown exception - get your error handling shit together porter')
			output_dict['slack_text'] = 'There was a combination of inputs that caused an error which was not caught in the "else" exception block after the actions are dished out in time_helper.'




	logger.debug('time_helper : final output_dict '+json.dumps(output_dict))
	return output_dict


##### MINOR FUNCTIONS

def format_action(action):
	if action != None and action != '' and action != ' ':
		if action[-1] == 'e':
			action = action[:-1]
		return action+'ing'
	return 'viewing'

def insert_line_breaks(string,length=50):
	num_lines = int(math.ceil(float(len(string))/float(length)))
	new_string = ''
	for line_num in range(num_lines):
		if line_num+1 == num_lines:
			new_string += string[:length]
		else:
			new_string += string[:length]+'\n'
		string = string[length:]
	return new_string


def get_client_display_name(client_name):
	logger.debug('get_client_display_name : checking database for client_display_name based on client_name '+client_name)
	query = Clients.objects.get(client_name=client_name,mark_for_deletion='n')
	return str(query.client_display_name)

def get_client_display_name_from_id(client_id):
	logger.debug('get_client_display_name_from_id : checking database for client_display_name based on client_id '+str(client_id))
	try:
		query = Clients.objects.get(client_id=int(client_id),mark_for_deletion='n')
	except:
		return 'Invalid Client ID'
	return str(query.client_display_name)

def get_client_id(client_name):
	# could add cache check like with get_config
	logger.debug('get_client_id : checking database for client_id based on client_name '+client_name)
	query = Clients.objects.get(client_name=client_name,mark_for_deletion='n')
	#return str(query.client_id)
	return query

def transform_string_to_date(date,format_of_date):
	logger.debug('transform_string_to_date : converting '+str(date)+' from a string to a date')
	if date == 'today':
		return datetime.datetime.now().date()
	elif date == 'yesterday':
		return (datetime.datetime.now() - datetime.timedelta(days=1)).date()
	elif date == 'twodaysago' or date == '2daysago':
		return (datetime.datetime.now() - datetime.timedelta(days=2)).date()
	elif date == 'threedaysago' or date == '3daysago':
		return (datetime.datetime.now() - datetime.timedelta(days=3)).date()
	elif date == 'fourdaysago' or date == '4daysago':
		return (datetime.datetime.now() - datetime.timedelta(days=4)).date()
	elif date == 'fivedaysago' or date == '5daysago':
		return (datetime.datetime.now() - datetime.timedelta(days=5)).date()
	elif date == 'sixdaysago' or date == '6daysago':
		return (datetime.datetime.now() - datetime.timedelta(days=6)).date()
	elif date == 'lastweek' or date == 'last_week' or date == 'last week':
		return (datetime.datetime.now() - datetime.timedelta(days=7)).date()
	elif date == 'lastmonth' or date == 'last_month' or date == 'last month':
		return (datetime.datetime.now() - datetime.timedelta(days=28)).date()

	if format_of_date != None:
		date_format = format_of_date
	else:
		date_format = '%m/%d/%y'

	if len(date.split('/')[2]) == 4:
		logger.debug('transform_string_to_date : 4 digit date detected!! cleaning up sloppy date format setting...')
		date_format = '%m/%d/%Y'
			
	return datetime.datetime.strptime(date,date_format)

def transform_date_to_string(date,format_of_date):
	logger.debug('transform_date_to_string : converting '+str(date)+' to a proper string')
	if format_of_date != None:
		date_format = format_of_date
	else:
		date_format = '%m/%d/%y'
			
	return datetime.datetime.strftime(date,date_format)

def build_str_number(integer):
	logger.debug('build_str_number : formatting string for full_invoice_id...')
	string = str(integer)
	if len(string) == 1:
		final = '00'+string
	elif len(string) == 2:
		final = '0'+string
	else:
		final = string
	return final


def get_pay_rates(client_name,**kwargs):
	logger.debug('get_pay_rates : checking database for pay_rates associated with client_name '+client_name)
	pay_rate_dict = {}

	#what happens when client_name DNE?????
	pay_rate_query = PayRate.objects.all().filter(client_id=get_client_id(client_name),mark_for_deletion='n')

	for item in pay_rate_query:
		if datetime.datetime.now() >= item.valid_from.replace(tzinfo=None) and datetime.datetime.now() <= item.valid_to.replace(tzinfo=None) and item.mark_for_deletion == 'n':
			pay_rate_dict[item.project_name] = item.hourly_rate

	return pay_rate_dict
	



##### ADVANCED ACTION FUNCTIONS

def do_invoice(client_name,period,starting_date,ending_date,inv_date,**kwargs):
	# either everything that has yet to be invoicd or a selected range, based on the recordsList passed in
	# this function should assign and invoice number and market the records as invoiced 
		# and will update current_invoice_flag in order to select the correct records during create_invoice
	# then once the upates are done, pass the invoice number to create_invoice
	# have a config option for creating the invoice vs just marking them as invoiced
		# this will end up calling create_invoice if config is enabled and invoicing prep is successful

	logger.debug('do_invoice : getting last invoice number from database...')
	old_vqs = CurrentInvoice.objects.values()
	old = qtd(old_vqs)#[0]
	#print(old)
	if old != []:
		CurrentInvoice.objects.get(pk=old[0]['id']).delete()

		new_inv_number = old[0]['invoice_number'] + 1

	else:
		new_inv_number = 1
	logger.debug('do_invoice : new invoice number set to '+str(new_inv_number))

	include_str = ''

	if period != None:
		logger.debug('do_invoice : gathering records using client and period...')
		if period == 'current':
			query = Main.objects.all().filter(client_id=get_client_id(client_name),current_invoice_flag='y',mark_for_deletion='n',billable_flag='y')
	elif starting_date != None and ending_date != None:
		logger.debug('do_invoice : gathering records using client and start / end dates...')
		query = Main.objects.all().filter(client_id=get_client_id(client_name),billable_flag='y',work_date__gte=transform_string_to_date(starting_date,None),work_date__lte=transform_string_to_date(ending_date,None),mark_for_deletion='n')
	else:
		logger.debug('do_invoice : not enough info provided to gather records - missing start/end dates or period')
		return False

	for record in query:
		include_str += str(record.record_id)+','

	query.update(invoiced_flag = 'y',invoice_number = new_inv_number,current_invoice_flag = 'n')
	logger.debug('do_invoice : records successfully gathered for invoice '+str(new_inv_number))

	new = CurrentInvoice(invoice_number=new_inv_number,records_included=include_str)
	new.save()
	logger.debug('do_invoice : CurrentInvoice updated!')

	if get_config('timeentry','autocreate'):
		#can add feedback like 'generating pdf...'
		logger.debug('do_invoice : auto calling create_invoice in a new thread...')

		if 'email_address' in kwargs:
			thread.start_new_thread(create_invoice,(new_inv_number,inv_date,kwargs['email_address']))
		else:
			thread.start_new_thread(create_invoice,(new_inv_number,inv_date,None))
	#print(new_inv_number)
	return new_inv_number

def create_invoice(inv_number,inv_date,email_address=None,**kwargs):
	# takes in an invoice number, gathers necessary records and outputs in tbd format to be used as invoice
		# could use djanog templates for the time being as save as a pdf from browser maybe?
		# i'd rather make it more robust though and write to a csv or something

	logger.debug('create_invoice : collecting records for the invoice - querying Main...')
	records_query = Main.objects.all().filter(invoice_number=inv_number).order_by('work_date')

	logger.debug('create_invoice : beginning unique client check...')
	unique_client_checker = None
	for record in records_query:
		client = record.client_id 
		#print(client)
		if unique_client_checker == None:
			unique_client_checker = client
		else:
			if unique_client_checker != client:
				logger.error(get_log_string('create_invoice','ERROR - multiple clients detected for the same invoice'))
				return 'ERROR - multiple clients detected'
	logger.debug('create_invoice : unique client confirmed!')

	logger.debug('create_invoice : getting client display name from database...')
	client_query = Clients.objects.get(client_id=client.client_id)
	client_display_name = client_query.client_display_name
	logger.debug('create_invoice : display name found '+str(client_display_name))

	key = 0
	line_no = 1

	pay_rate_dict = get_pay_rates(client_query.client_name)


	records_dict = {}
	logger.debug('create_invoice : begin building records_dict...')
	for record in records_query:
		logger.debug('create_invoice : starting line # '+str(line_no))
		records_dict[key] = {
			"line_no":str(line_no),
			"work_date":record.work_date,
			"work_desc":record.work_desc,
			"hours":record.hours,
		}

		logger.debug('create_invoice : calculating dollar values...')
		rate = float(get_config_value('timeentry','dfltrate'))
		if record.project_name in pay_rate_dict.keys():
			rate = pay_rate_dict[record.project_name]
		if record.billable_flag == 'y':
			records_dict[key]['dollars'] = float(record.hours)*float(rate)
		else:
			records_dict[key]['dollars'] = 0

		records_dict[key]['disp_dollars'] = '${:,.2f}'.format(records_dict[key]['dollars'])
		logger.debug('create_invoice : line  # '+str(line_no)+' written successfully!')

		key += 1
		line_no += 1

	logger.debug('create_invoice : building formatted full invoice number...')
	inv_num_formatted = build_str_number(inv_number)+'_'+transform_date_to_string(inv_date,None).replace('/','-')
	logger.debug('create_invoice : invoice number successfully formatted to '+str(inv_num_formatted))

	start_of_cycle_date = inv_date - datetime.timedelta(days=13)
	end_of_week_1_date = inv_date - datetime.timedelta(days=7)
	middle_of_cycle_date = inv_date - datetime.timedelta(days=6)

	try:
		start_of_cycle_date = start_of_cycle_date.date()
	except AttributeError:
		pass
	try:
		end_of_week_1_date = end_of_week_1_date.date()
	except AttributeError:
		pass
	try:
		middle_of_cycle_date = middle_of_cycle_date.date()
	except AttributeError:
		pass
	try:
		inv_date = inv_date.date()
	except AttributeError:
		pass

	week_1_hours = 0.00
	week_1_dollars = 0.00
	week_2_hours = 0.00
	week_2_dollars = 0.00
	other_week_hours = 0.00
	other_week_dollars = 0.00


	logger.debug('create_invoice : begin calculating totals...')
	total_dollars = 0.00
	total_hours = 0.00
	for key in records_dict:
		if records_dict[key]['work_date'] >= start_of_cycle_date and records_dict[key]['work_date'] <= end_of_week_1_date:
			week_1_hours += float(records_dict[key]['hours'])
			week_1_dollars += float(records_dict[key]['dollars'])
		elif records_dict[key]['work_date'] >= middle_of_cycle_date and records_dict[key]['work_date'] <= inv_date:
			week_2_hours += float(records_dict[key]['hours'])
			week_2_dollars += float(records_dict[key]['dollars'])
		else:
			other_week_hours += float(records_dict[key]['hours'])
			other_week_dollars += float(records_dict[key]['dollars'])
		total_dollars += float(records_dict[key]['dollars'])
		total_hours += float(records_dict[key]['hours'])

	total_disp_dollars = '${:,.2f}'.format(total_dollars)
	week_1_disp_dollars = '${:,.2f}'.format(week_1_dollars)
	week_2_disp_dollars = '${:,.2f}'.format(week_2_dollars)
	other_week_disp_dollars = '${:,.2f}'.format(other_week_dollars)

	logger.debug('create_invoice : totals calculated!')

	logger.debug('create_invoice : buliding header_dict...')
	header_dict = {
		"inv_no":inv_number,
		"inv_no_formatted":inv_num_formatted,
		"client":client_display_name,
		"total_disp_dollars":total_disp_dollars,
		"week_1_disp_dollars":week_1_disp_dollars,
		"week_2_disp_dollars":week_2_disp_dollars,
		"other_week_disp_dollars":other_week_disp_dollars,
		"total_hours":total_hours,
		"week_1_hours":week_1_hours,
		"week_2_hours":week_2_hours,
		"other_week_hours":other_week_hours,
		"inv_date":inv_date,
		"start_of_cycle_date":start_of_cycle_date,
		"end_of_week_1_date":end_of_week_1_date,
		"middle_of_cycle_date":middle_of_cycle_date
	}
	if email_address != None:
		header_dict['email_address'] = email_address
	else:
		header_dict['email_address'] = 'default'
	logger.debug('create_invoice : header_dict - '+str(header_dict))
	logger.debug('create_invoice : total_dollars - '+str(total_dollars))

	logger.debug('create_invoice : writing new Invoice record')
	new = Invoice(
		invoice_number=inv_number,
		full_invoice_id=inv_num_formatted,
		invoice_date=inv_date,
		client_id=client_query,
		total_hours=round(total_hours,2),
		total_dollars=round(total_dollars,2)
		)
	new.save()
	logger.debug('create_invoice : new record written successfully! id '+str(new.invoice_id))

	if get_config('timeentry','genpdf'):
		logger.debug('create_invoice : calling generate_pdf with...')
		logger.debug('create_invoice : records_dict - '+str(records_dict))
		generate_pdf(new.invoice_id,header_dict,records_dict)


	return new.invoice_id,header_dict,records_dict

def generate_pdf(invoice_id,header_dict,records_dict):
	# YOU STILL NEED TO DEAL WITH OVERFLOW PAGES

	logger.debug('generate_pdf : beginning pdf creation for invoice '+str(header_dict['inv_no']))

	logger.debug('generate_pdf : creating canvas...')
	pdf = canvas.Canvas('output/Invoice_'+str(header_dict['inv_no_formatted'])+'.pdf', pagesize=portrait(letter))
	#pdf.translate(inch,inch)

	logger.debug('generate_pdf : writing static header...')
	pdf.setFont('Helvetica',24)
	pdf.drawString(inch, 10*inch, "Invoice of Work Performed")
	pdf.setFont('Helvetica',16)
	pdf.drawString(inch,9.25*inch,"Jonathan Porter | Porter Software")
	pdf.drawString(inch,9*inch,"me@jporter.io | (404) 625-9140")
	pdf.drawString(inch,8.75*inch,'1140 Church St NW Atlanta GA 30318')

	logger.debug('generate_pdf : populating invoice specific information...')
	pdf.drawString(inch,8.25*inch,'Client: '+header_dict['client'])
	pdf.drawString(inch,8*inch,'Invoice #: '+header_dict['inv_no_formatted'])
	pdf.drawString(4.5*inch,8*inch,'Invoice Date: '+transform_date_to_string(header_dict['inv_date'],None))

	logger.debug('generate_pdf : building details table data...')
	data = [['#','Date','Description of Work','Hours','Dollars']]
	for record in records_dict:
		formatted_work_desc = records_dict[record]['work_desc']
		if len(formatted_work_desc) > 50:
			formatted_work_desc = insert_line_breaks(formatted_work_desc)
		data += [[records_dict[record]['line_no'],transform_date_to_string(records_dict[record]['work_date'],None),str(formatted_work_desc),records_dict[record]['hours'],records_dict[record]['disp_dollars']]]
	#print(data)
	logger.debug('generate_pdf : details table data list generated! '+str(data))

	logger.debug('generate_pdf : writing data to table...')
	table = Table(data)#, colWidths=2*inch, rowHeights=0.50*inch)
	table.setStyle(TableStyle([
						   ('INNERGRID', (0,0), (-1,-1), 0.25, colors.white),
						   ('INNERGRID', (0,1), (-1,-1), 0.25, colors.black),
						   ('BOX', (0,0), (-1,-1), 0.25, colors.black),
						   ('BACKGROUND',(0,0),(-1,0),colors.black),
						   ('TEXTCOLOR',(0,0),(-1,0),colors.white),
						   ('BACKGROUND',(0,1),(-1,-1),colors.lightgrey)
						   ]))
	table.wrapOn(pdf,inch,3.5*inch)	# find required space
	table.drawOn(pdf,inch,3.5*inch)

	logger.debug('generate_pdf : writing summary section...')
	pdf.drawString(inch,3*inch,'Summary')
	pdf.setFont('Helvetica',12)
	pdf.drawString(inch,2.75*inch,'Week 1: '+transform_date_to_string(header_dict['start_of_cycle_date'],None)+' - '+transform_date_to_string(header_dict['end_of_week_1_date'],None))
	pdf.drawString(inch,2.5*inch,str(header_dict['week_1_hours']) + ' hour(s) | ' + str(header_dict['week_1_disp_dollars']))
	pdf.drawString(inch,2.25*inch,'Week 2: '+transform_date_to_string(header_dict['middle_of_cycle_date'],None)+' - '+transform_date_to_string(header_dict['inv_date'],None))
	pdf.drawString(inch,2*inch,str(header_dict['week_2_hours']) + ' hour(s) | ' + str(header_dict['week_2_disp_dollars']))
	if header_dict['other_week_hours'] != 0.00:
		pdf.drawString(inch,1.75*inch,'Other:')
		pdf.drawString(inch,1.5*inch,str(header_dict['other_week_hours']) + ' hour(s) | ' + str(header_dict['other_week_disp_dollars']))

	logger.debug('generate_pdf : writing totals section...')
	pdf.setFont('Helvetica-Bold',14)
	pdf.drawString(4*inch,1.75*inch,'Total Billing Period: '+transform_date_to_string(header_dict['start_of_cycle_date'],None)+' - '+transform_date_to_string(header_dict['inv_date'],None))
	pdf.setFont('Helvetica-Bold',18)
	pdf.drawString(4.5*inch,1.5*inch,'TOTAL HOURS:   '+'  '+' '+str(header_dict['total_hours']))
	pdf.drawString(4.5*inch,1.25*inch,'TOTAL DOLLARS: '+str(header_dict['total_disp_dollars']))
	pdf.setFont('Helvetica',12)
	pdf.drawString(1.25*inch,0.5*inch,'Thank you so much for your business, I look forward to continuing working together!')

	logger.debug('generate_pdf : rendering the pdf')
	pdf.showPage()
	pdf.save()

	if get_config('timeentry','emailpdf'):
		if get_config('timeentry','emailtoclt') and header_dict['email_address'] != 'default':
			logger.debug('generate_pdf : calling email_invoice_pdf and sending email to client\'s email...')
			email_invoice_pdf(str(header_dict['inv_no_formatted']),to_address=header_dict['email_address'])
		else:
			logger.debug('generate_pdf : calling email_invoice_pdf with default email...')
			email_invoice_pdf(str(header_dict['inv_no_formatted']))

	return True
   # return response

def email_invoice_pdf(full_invoice_id,to_address='me@jporter.io',**kwargs):
	logger.debug('email_invoice_pdf : checking if sending to porter or not...')
	if to_address == 'me@jporter.io':
		logger.debug('email_invoice_pdf : emailing file to porter - me@jporter.io')
		nownow = datetime.datetime.now()
		subject = 'your invoice has been generated: ' + full_invoice_id #+ ' | ' + str(nownow.year) + str(nownow.month) + str(nownow.day) + '_' + str(nownow.hour) + str(nownow.minute) + str(nownow.second)
	
		body = 'the invoice pdf you generated is attached'


	else:
		logger.debug('email_invoice_pdf : sending invoice directly to the client - '+str(to_address))
		subject = 'Your invoice from Porter Software - Invoice_' + full_invoice_id

		body = 'Hello,\n\nThank you for your business! An invoice has been sent to you from Porter Software. Please see the attached document and reply to this email with any questions.\n\nBest,\nPorter Software Financial Team\n\n\n\nNOTE: If you believe you have received this message in error, please disregard the attached document and reply to this email to let us know. Thanks!'

	logger.debug('email_invoice_pdf : creating email...')
	email = EmailMessage(subject, body, to=[to_address])
	logger.debug('email_invoice_pdf : email created! attaching invoice...')
	email.attach_file('output/Invoice_'+full_invoice_id+'.pdf')
	logger.debug('email_invoice_pdf : invoice attached! sending email...')
	email.send()
	logger.debug('email_invoice_pdf : email sent!')
	return True

def reverse_invoice(invoice_number,**kwargs):
	invoice_number = int(invoice_number)
	invoice_record = Invoice.objects.all().filter(invoice_number=invoice_number)
	invoice_record.delete()
	current_invoice_record = CurrentInvoice.objects.all().filter(invoice_number=invoice_number)
	current_invoice_record.update(invoice_number=invoice_number-1)
	main_records = Main.objects.all().filter(invoice_number=invoice_number)
	main_records.update(current_invoice_flag='y',invoice_number=None,invoiced_flag='n')
	return True

def mark_paid(pay_date,invoice_number=None,starting_date=None,ending_date=None,**kwargs):
	# marks the records as paid
	# if already marked paid, does not overwrite unless force option is enabled

	invoice_list = []

	logger.debug('mark_paid : begin building included invoice list...')
	if invoice_number != None:
		# then an invoice has been passed in by the user, and the entire invoice should be marked paid
		logger.debug('create_invoice : specific invoice passed in '+str(invoice_number))
		invoice_list += [invoice_number]
	else:
		# invoices within a date range should be marked paid, in which case start and end date will be populated
		logger.debug('create_invoice : start / end dates used - querying Invoice to find invoice_number\'s...')
		inv_query = Invoice.objects.all().filter(invoice_date__gte=transform_string_to_date(starting_date,None),invoice_date__lte=transform_string_to_date(ending_date,None),mark_for_deletion='n')
		for indiv_inv in inv_query:
			if indiv_inv.invoice_number not in invoice_list:
				invoice_list += [indiv_inv.invoice_number]

	if invoice_list == []:
		logger.debug('create_invoice : no invoices returned')
		return False

	logger.debug('create_invoice : using the following invoice list '+str(invoice_list))

	for invoice in invoice_list:	
		logger.debug('create_invoice : updating record in Invoice for '+str(invoice))
		try:
			inv_query = Invoice.objects.get(invoice_number=invoice,mark_for_deletion='n')
			inv_query.paid_flag = 'y'
			inv_query.paid_date = pay_date
			inv_query.save()
		except Invoice.DoesNotExist:
			logger.debug('create_invoice : invoice did not exist when attempting to mark it paid')
			return False

		logger.debug('create_invoice : updating records in Main for '+str(invoice))
		records_query = Main.objects.all().filter(invoice_number=invoice,mark_for_deletion='n')
		records_query.update(paid_flag='y',paid_date=pay_date)

		logger.debug('create_invoice : invoice '+str(invoice)+' marked paid successfully!')

	return True

def view_records(client_name,period=None,starting_date=None,ending_date=None,**kwargs):
	#this should output a dictionary of ordered records, ordered by the work completed on date 
	# the keys of the dict will be numbers: 0,1,2... [arrays start at 0] and correspond to the order the records should be displayed, from oldest date to newest
	# should also include a total records for total hours and dollars (based on pay rate for client and project - if no project included use 'default')
		# should really do line by line math in a for loop to multiple by the correct project for each record
		# should read all payrates for the client into a var/list or something then match the correct one for each multiplication
		# adding to a running total of course
	# one of the things that should be returned with this is the record ID, which can then be used by the user to update and delete certain records
		# this is the appraoch taht should be suggested in the help for update and delete
		# similar concept should be employed for clients and payrates
	# each value of the dict should be a dict of each record - can do similar tools db_util on this server
		# will need to add in 'dollars' field after doing pay_rate math

	pay_rate_dict = get_pay_rates(client_name)
	
	vqs = None

	if period != None:
		# viewing a particular period (current, last, etc.)
		logger.debug('view_records : gathering records using client and period...')
		if period == 'current':
			vqs = Main.objects.values().filter(client_id=get_client_id(client_name),current_invoice_flag='y',mark_for_deletion='n').order_by('work_date')[:20]
			


	else:
		# viewing a particular date range
		logger.debug('view_records : gathering records using client and start / end dates...')
		vqs = Main.objects.values().filter(client_id=get_client_id(client_name),mark_for_deletion='n',work_date__gte=transform_string_to_date(starting_date,None),work_date__lte=transform_string_to_date(ending_date,None)).order_by('work_date')[:20]


	record_query_list = qtd(vqs)
	logger.debug('view_records : records returned '+str(len(record_query_list)))
	cnt = 0 #arrays start at 0
	logger.debug('view_records : begin building record_dict...')
	record_dict = {}
	for record in record_query_list:
		rate = float(get_config_value('timeentry','dfltrate'))
		if record['project_name'] in pay_rate_dict.keys():
			rate = pay_rate_dict[record['project_name']]
		if record['billable_flag'] == 'y':
			record['dollars'] = '${:,.2f}'.format(float(record['hours'])*float(rate))
			record['dollars_float'] = float(record['hours'])*float(rate)
		else:
			record['dollars'] = '$0.00'
			record['dollars_float'] = 0.00
		record_dict[cnt] = record
		cnt += 1


	logger.debug('view_records : figuring out cycle dates...')
	today = datetime.date.today()
	date_compare = today.weekday() - 4

	if date_compare == 0:
		# rebecca black
		friday_of_current_week = today
	elif date_compare > 0:
		# before friday
		friday_of_current_week = today + datetime.timedelta(days=date_compare)
	else:
		# after friday
		friday_of_current_week = today + datetime.timedelta(days=(date_compare+7))
	start_of_cycle_date = friday_of_current_week - datetime.timedelta(days=13)
	end_of_week_1_date = friday_of_current_week - datetime.timedelta(days=7)
	middle_of_cycle_date = friday_of_current_week - datetime.timedelta(days=6)

	week_1_hours = 0.00
	week_1_dollars = 0.00
	week_2_hours = 0.00
	week_2_dollars = 0.00
	other_week_hours = 0.00
	other_week_dollars = 0.00


	logger.debug('view_records : begin calculating totals...')
	total_dollars = 0.00
	total_hours = 0.00
	for key in record_dict:
		if record_dict[key]['work_date'] >= start_of_cycle_date and record_dict[key]['work_date'] <= end_of_week_1_date:
			week_1_hours += float(record_dict[key]['hours'])
			week_1_dollars += float(record_dict[key]['dollars_float'])
		elif record_dict[key]['work_date'] >= middle_of_cycle_date and record_dict[key]['work_date'] <= friday_of_current_week:
			week_2_hours += float(record_dict[key]['hours'])
			week_2_dollars += float(record_dict[key]['dollars_float'])
		else:
			other_week_hours += float(record_dict[key]['hours'])
			other_week_dollars += float(record_dict[key]['dollars_float'])
		total_dollars += float(record_dict[key]['dollars_float'])
		total_hours += float(record_dict[key]['hours'])

	total_disp_dollars = '${:,.2f}'.format(total_dollars)
	week_1_disp_dollars = '${:,.2f}'.format(week_1_dollars)
	week_2_disp_dollars = '${:,.2f}'.format(week_2_dollars)
	other_week_disp_dollars = '${:,.2f}'.format(other_week_dollars)

	logger.debug('view_records : totals calculated! writing to record_dict...')
	record_dict['total'] = {
		"total_hours":total_hours,
		"total_disp_dollars":total_disp_dollars,
		"week_1_hours":week_1_hours,
		"week_1_disp_dollars":week_1_disp_dollars,
		"week_2_hours":week_2_hours,
		"week_2_disp_dollars":week_2_disp_dollars,
		"other_week_hours":other_week_hours,
		"other_week_disp_dollars":other_week_disp_dollars
	}


	logger.debug('view_records : returning record_dict '+str(record_dict))
	return record_dict

def view_clients(client_name):
	if client_name == None:
		logger.debug('view_clients : gathering all client records...')
		vqs = Clients.objects.values().filter(mark_for_deletion='n').order_by('client_name')[:20]

		############################33 NEED TO BUILD A NEXT FUNCTION
	else:
		logger.debug('view_clients : looking for records containing provided client_name '+str(client_name))
		vqs = Clients.objects.values().filter(mark_for_deletion='n',client_name__contains=client_name).order_by('client_name')[:20]

	record_query_list = qtd(vqs)
	logger.debug('view_clients : records returned '+str(len(record_query_list)))

	record_dict = {}
	cnt = 0
	for record in record_query_list:
		record_dict[cnt] = record 
		cnt += 1
	logger.debug('view_clients : returned record_dict '+str(record_dict))
	return record_dict

def view_invoice(invoice_number=None,client_name=None,starting_date=None,ending_date=None,**kwargs):

	logger.debug('view_invoice : forming query based on user inputs - inv / client / start / end '+str(invoice_number)+' / '+str(client_name)+' / '+str(starting_date)+' / '+str(ending_date))
	if invoice_number != None:
		vqs = Invoice.objects.values().filter(mark_for_deletion='n',invoice_number=invoice_number).order_by('invoice_number')
	elif client_name != None and (starting_date == None or ending_date == None):
		vqs = Invoice.objects.values().filter(mark_for_deletion='n',client_id=get_client_id(client_name)).order_by('invoice_number')
	elif client_name != None and starting_date != None and ending_date != None:
		vqs = Invoice.objects.values().filter(mark_for_deletion='n',client_id=get_client_id(client_name),invoice_date__gte=transform_string_to_date(starting_date,None),invoice_date__lte=transform_string_to_date(ending_date,None)).order_by('invoice_number')
	elif starting_date != None and ending_date != None:
		vqs = Invoice.objects.values().filter(mark_for_deletion='n',invoice_date__gte=transform_string_to_date(starting_date,None),invoice_date__lte=transform_string_to_date(ending_date,None)).order_by('invoice_number')
	else:
		vqs = Invoice.objects.values().filter(mark_for_deletion='n').order_by('invoice_number')

	record_query_list = qtd(vqs)
	logger.debug('view_invoice : records returned '+str(len(record_query_list)))

	record_dict = {}
	cnt = 0
	for record in record_query_list:
		record_dict[cnt] = record 
		cnt += 1
	logger.debug('view_invoice : returned record_dict '+str(record_dict))
	return record_dict

def view_payrate(client_name,project,as_of_date):

	logger.debug('view_payrate : setting as_of_date...')
	if as_of_date == None:
		as_of_date == datetime.datetime.now()
	else:
		as_of_date = transform_string_to_date(as_of_date)

	logger.debug('view_payrate : forming query based on user inputs - client_name / project combination '+str(client_name)+' / '+str(project))
	if client_name == None and project == None:
		vqs = PayRate.objects.values().filter(mark_for_deletion='n').order_by('valid_from')[:20]
	elif client_name != None and project == None:
		vqs = PayRate.objects.values().filter(mark_for_deletion='n',client_id=get_client_id(client_name)).order_by('valid_from')[:20]
	elif client_name == None and project != None:
		vqs = PayRate.objects.values().filter(mark_for_deletion='n',project_name=project).order_by('valid_from')[:20]
	else:
		vqs = PayRate.objects.values().filter(mark_for_deletion='n',client_id=get_client_id(client_name),project_name=project).order_by('valid_from')[:20]

	record_query_list = qtd(vqs)
	logger.debug('view_payrate : records returned '+str(len(record_query_list)))

	record_dict = {}
	cnt = 0
	for record in record_query_list:
		record_dict[cnt] = record 
		cnt += 1
	logger.debug('view_payrate : returned record_dict '+str(record_dict))
	return record_dict

#### BASIC ACTION FUNCTIONS

def add_record(client_name,number_of_hours,billable_flag,work_date_transformed,work_desc,project,**kwargs):
	# project can be passed in as null if not included, should write 'default' to the db in that case
	if project == None:
		logger.debug('add_record : defaulting project...')
		project = 'default'

	if validate_client_name(client_name) and validate_number_of_hours(number_of_hours) and validate_billable_flag(billable_flag) and validate_date_is_in_the_past(work_date_transformed) and validate_work_desc(work_desc) and validate_project(project):
		client_id = get_client_id(client_name)

		logger.debug('add_record : writing new record...')
		new = Main(
			client_id = client_id,
			hours = float(number_of_hours),
			work_desc = work_desc,
			project_name = project,
			work_date = work_date_transformed,
			billable_flag = billable_flag,
			current_invoice_flag = 'y'
		)
		new.save()
		logger.debug('add_record : new record written '+str(new.record_id))
		return new.record_id
	return False

def add_client(client_name,client_display_name,**kwargs):
	
	if validate_client_name(client_name) and validate_client_display_name(client_display_name):
		logger.debug('add_client : writing new record...')
		new = Clients(
			client_name = client_name,
			client_display_name = client_display_name
		)
		new.save()
		logger.debug('add_client : new record written '+str(new.client_id))
		return new.client_id 
	return False



def add_payrate(client_name,pay_rate,starting_date,ending_date,project,**kwargs):
	# will have the option to add a freeform project field to the pay rate
		# if no project is included, then write a default record
		# if a project is included, also write a default record in cause no project is included in the query
	if project == None:
		logger.debug('add_payrate : defaulting project...')
		project = 'default'
		write_default = 0
	else:
		logger.debug('add_payrate : project included in user inputs')
		write_default = 1

	if validate_client_name(client_name) and validate_pay_rate(pay_rate) and validate_project(project):
		client_id = get_client_id(client_name)
		logger.debug('add_payrate : writing new record...')
		new = PayRate(
			client_id = client_id,
			project_name = project,
			hourly_rate = float(pay_rate),
			valid_from = starting_date,
			valid_to = ending_date
		)
		new.save()
		logger.debug('add_payrate : new record written '+str(new.pay_rate_id))
		if write_default == 1 and project != 'default':
			logger.debug('add_payrate : because project included in user inputs, checking if default record already exists...')
			#this part is NOT YET TESTED ##########################################################
			does_it_exist_query = PayRate.objects.get(client_id=client_id,project_name='default')
			if float(does_it_exist_query.hourly_rate) >= 0:
				#already exists
				logger.debug('add_payrate : non-zero defaul pay_rate exists, passing...')
				pass
			else:
				logger.debug('add_payrate : writing default record...')
				new2 = PayRate(
					client_id = client_id,
					project_name = 'default',
					hourly_rate = float(pay_rate),
					valid_from = starting_date,
					valid_to = ending_date
				)
				new2.save()
				logger.debug('add_payrate : new default record written '+str(new2.pay_rate_id))
		return new.pay_rate_id 
	return False

def update_record(record_id,client_name,project,hours,work_desc,work_date,billable_flag):
	logger.debug('update_record : update record '+str(record_id))
	record = Main.objects.get(record_id=record_id)
	if client_name != None and validate_client_name(client_name):
		logger.debug('update_record : updating client to '+str(client_name))
		record.client_id = get_client_id(client_name)
	if hours != None and validate_number_of_hours(hours):
		logger.debug('update_record : updating hours to '+str(hours))
		record.hours = float(hours)
	if work_desc != None and validate_work_desc(work_desc):
		logger.debug('update_record : updating work_desc to '+str(work_desc))
		record.work_desc = work_desc
	if work_date != None and validate_date_is_in_the_past(work_date):
		logger.debug('update_record : updating work_date to '+str(work_date))
		record.work_date = work_date
	if billable_flag != None and validate_billable_flag(billable_flag):
		logger.debug('update_record : updating billable_flag to '+str(billable_flag))
		record.billable_flag = billable_flag
	record.save()
	return record.record_id

def update_client(client_id,client_name,client_display_name):
	logger.debug('update_client : update client '+str(client_id))
	client = Clients.objects.get(client_id=client_id)
	if client_name != None and validate_client_name(client_name):
		logger.debug('update_client : updating client_name to '+str(client_name))
		client.client_name = client_name
	if client_display_name != None and validate_client_display_name(client_display_name):
		logger.debug('update_client : updating display_name to '+str(client_display_name))
		client.client_display_name = client_display_name
	client.save()
	return client.client_id 

def update_payrate(pay_rate_id,client_name,project,pay_rate,starting_date,ending_date):
	logger.debug('update_payrate : update payrate '+str(pay_rate_id))
	payrate = PayRate.objects.get(pay_rate_id=pay_rate_id)
	if client_name != None and validate_client_name(client_name):
		logger.debug('update_payrate : updating client to '+str(client_name))
		payrate.client_id = get_client_id(client_name)
	if project != None and validate_project(project):
		logger.debug('update_payrate : updating project to '+str(project))
		payrate.project_name = project
	if pay_rate != None and validate_pay_rate(pay_rate):
		logger.debug('update_payrate : updating payrate to '+str(pay_rate))
		payrate.hourly_rate = float(pay_rate)
	if starting_date != None:
		logger.debug('update_payrate : updating start date to '+str(starting_date))
		payrate.valid_from = transform_string_to_date(starting_date,None)
	if ending_date != None:
		logger.debug('update_payrate : updating end date to '+str(ending_date))
		payrate.valid_to = transform_string_to_date(ending_date,None)
	payrate.save()
	return payrate.pay_rate_id


def delete(type,record_id):
	#updates the mark for deletion flag
	try:
		logger.debug('delete : deleting record '+str(record_id))
		if type == 'record':
			existing = Main.objects.get(record_id=record_id)
		elif type == 'client':
			existing = Client.objects.get(record_id=record_id)
		elif type == 'payrate':
			existing = PayRate.objects.get(record_id=record_id)
		else:
			#unknown deletion type
			return False
		existing.mark_for_deletion = 'y'
		existing.save()
		logger.debug('delete : record deleted')
		return True
	except Main.DoesNotExist:
		#no record to mark
		logger.debug('delete : no record to delete!')
		return True #for now
	except MultipleObjectsReturned:
		#too many records
		logger.error('delete : more than one record returned with the same id, check database!')
		return False



def purge(table,**kwargs):
	# actually deletes everything that has been marked for deletion from the table passed into the function
	logger.debug('purge : deleting records for table '+str(table))

	if table == 'all':
		model1 = Main.objects.all().filter(mark_for_deletion='y')
		model2 = Clients.objects.all().filter(mark_for_deletion='y')
		model3 = PayRate.objects.all().filter(mark_for_deletion='y')
		model4 = Invoice.objects.all().filter(mark_for_deletion='y')
		model5 = CurrentInvoice.objects.all()

		model1.delete()
		model2.delete()
		model3.delete()
		model4.delete()
		model5.delete()

		return True

	elif table == 'main':
		model1 = Main.objects.all().filter(mark_for_deletion='y')
		model1.delete()

		return True

	elif table == 'client':
		model2 = Clients.objects.all().filter(mark_for_deletion='y')
		model2.delete()

		return True


	elif table == 'payrate':
		model3 = PayRate.objects.all().filter(mark_for_deletion='y')
		model3.delete()

	elif table == 'invoice':
		model3 = Invoice.objects.all().filter(mark_for_deletion='y')
		model3.delete()

	elif table == 'currentinvoice':
		model3 = CurrentInvoice.objects.all()
		model3.delete()

		return True

	else:
		return False


#### VALIDATORS

def validate_client_name(client_name):
	logger.debug('validate_client_name : checking if client_name is less than 50 characters...')
	if len(client_name) <= 50:
		return True
	return False

def validate_client_display_name(client_display_name):
	logger.debug('validate_client_display_name : checking if disp_name is less than 100 characters...')
	if len(client_display_name) <= 100:
		return True
	return False

def validate_number_of_hours(hours):
	logger.debug('validate_number_of_hours : checking if number_of_hours is a float and >= 0...')
	try:
		hours = float(hours)
	except ValueError:
		return False

	if hours >= 0:
		return True
	return False

def validate_billable_flag(flag):
	logger.debug('validate_billable_flag : checking if billable_flag is y or n...')
	if flag.lower() in ['y','n']:
		return True
	return False

def validate_date_is_in_the_past(work_date):
	logger.debug('validate_date_is_in_the_past : checking if the date is in the past...')
	if type(work_date) == datetime.datetime:
		work_date = work_date.date()
	if work_date <= datetime.datetime.now().date():
		return True
	return False

def validate_work_desc(desc):
	logger.debug('validate_work_desc : checking if work_desc is less than 100 characters...')
	if len(desc) <= 100:
		return True
	return False

def validate_project(project):
	logger.debug('validate_project : checking if project is less than 50 characters...')
	if len(project) <= 50:
		return True
	return False

def validate_pay_rate(pay_rate):
	logger.debug('validate_pay_rate : checking if pay_rate is a float and >= 0...')
	try:
		pay_rate = float(pay_rate)
	except ValueError:
		return False

	if pay_rate >= 0:
		return True
	return False