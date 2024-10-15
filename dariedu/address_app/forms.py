from django import forms
from django.forms import ModelChoiceField, Select

from address_app.models import RouteSheet, Location
import logging

logging.basicConfig(level=logging.INFO)


class AddToRouteSheetForm(forms.Form):
    _selected_action = forms.CharField(widget=forms.MultipleHiddenInput, required=False)
    route_sheet = ModelChoiceField(queryset=RouteSheet.objects.all(), label='Маршрутный лист')


class AddToLocationForm(forms.Form):
    _selected_action = forms.CharField(widget=forms.MultipleHiddenInput, required=False)
    location = ModelChoiceField(queryset=Location.objects.all(), label='Локация')
