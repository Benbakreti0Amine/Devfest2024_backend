# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Clients(models.Model):
    ip_address = models.TextField(unique=True)

    class Meta:
        managed = False
        db_table = 'clients'


class MetricsBandwidth(models.Model):
    client = models.ForeignKey(Clients, models.DO_NOTHING)
    bw_requested = models.FloatField()
    frames = models.IntegerField()
    bytes = models.IntegerField()
    timestamp = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'metrics_bandwidth'
