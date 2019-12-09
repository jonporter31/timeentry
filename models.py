# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

class Clients(models.Model):
	client_id = models.AutoField(primary_key=True)
	client_name = models.CharField(max_length=50,unique=True)
	client_display_name = models.CharField(max_length=100)
	created_dttm = models.DateTimeField(auto_now_add=True)
	modified_dttm = models.DateTimeField(auto_now=True)
	mark_for_deletion = models.CharField(max_length=1,default='n')

class PayRate(models.Model):
	pay_rate_id = models.AutoField(primary_key=True)
	client_id = models.ForeignKey(Clients, on_delete=models.CASCADE)
	project_name = models.CharField(max_length=50)
	hourly_rate = models.DecimalField(max_digits=10,decimal_places=2)
	valid_from = models.DateTimeField()
	valid_to = models.DateTimeField()
	created_dttm = models.DateTimeField(auto_now_add=True)
	modified_dttm = models.DateTimeField(auto_now=True)
	mark_for_deletion = models.CharField(max_length=1, default='n')

class Main(models.Model):
	record_id = models.AutoField(primary_key=True)
	client_id = models.ForeignKey(Clients, on_delete=models.CASCADE)
	hours = models.DecimalField(max_digits=10,decimal_places=2)
	work_desc = models.CharField(max_length=100)
	project_name = models.CharField(max_length=50,blank=True,null=True)
	work_date = models.DateField()
	billable_flag = models.CharField(max_length=1) # this will be either a y or n most likely
	invoiced_flag = models.CharField(max_length=10,default='n')
	invoice_number = models.CharField(max_length=25,blank=True,null=True)
	current_invoice_flag = models.CharField(max_length=1,default='n')
	paid_flag = models.CharField(max_length=10,default='n')
	paid_date = models.DateTimeField(blank=True,null=True)
	mark_for_deletion = models.CharField(max_length=1,default='n')
	created_dttm = models.DateTimeField(auto_now_add=True)
	modified_dttm = models.DateTimeField(auto_now=True)

class CurrentInvoice(models.Model):
	invoice_number = models.IntegerField()
	records_included = models.CharField(max_length=200,blank=True,null=True)
	created_dttm = models.DateTimeField(auto_now_add=True)
	modified_dttm = models.DateTimeField(auto_now=True)

class Invoice(models.Model):
	invoice_id = models.AutoField(primary_key=True)
	invoice_number = models.IntegerField()
	full_invoice_id = models.CharField(max_length=50,default=None)
	invoice_date = models.DateTimeField()
	client_id = models.ForeignKey(Clients, on_delete=models.CASCADE)
	total_hours = models.DecimalField(max_digits=10,decimal_places=2)
	total_dollars = models.DecimalField(max_digits=10,decimal_places=2)
	paid_flag = models.CharField(max_length=1,default='n')
	paid_date = models.DateTimeField(blank=True,null=True)
	mark_for_deletion = models.CharField(max_length=1,default='n')