# -*- coding: utf-8 -*-

from django import forms

class GreetingForm(forms.Form):
    name=forms.CharField()

class SlackVerificationForm(forms.Form):
    token=forms.CharField()
    challenge=forms.CharField()
    type=forms.CharField()
