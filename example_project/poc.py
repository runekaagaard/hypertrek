from hypertrek import missions as ms
from hypertrek import trek

import django
from django import forms

import os
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'example_project.settings')
django.setup()

class PocForm(forms.Form):
    name = forms.CharField(max_length=4, label="What's your name?")
    description = forms.CharField(widget=forms.Textarea, label="Write a few words about yourself ...")

def poc_trek():
    return [
        ms.form.form(PocForm),
    ]

def fill_poc_trek():
    state = None
    while True:
        state = trek.forward(poc_trek, state=state)
        print(state)
        break

fill_poc_trek()
