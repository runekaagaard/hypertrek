from hypertrek import missions as ms
from hypertrek import trek

import django
from django import forms

import os
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'example_project.settings')
django.setup()

class PocForm(forms.Form):
    name = forms.CharField(max_length=4, label="What's your name?", help_text="Please enter your name.")
    description = forms.CharField(widget=forms.Textarea, label="Write a few words about yourself ...",
                                  help_text="Dont' be shy!")
    options = forms.ChoiceField(choices=[("a", "A"), ("b", "B"), ("c", "C")], label="Which one?",
                                help_text="Choose one, god dammit!")

def poc_trek():
    return [
        ms.form.form(PocForm),
    ]

def fill_poc_trek():
    state = None
    command = trek.CONTINUE
    inpt = {}
    while True:
        command, state, side_effects = trek.forward(poc_trek, state=state, inpt=inpt)
        if command == trek.TERMINATED:
            break
        text = side_effects["renders"]["text"]
        print(text, "\n")

        for line in text.strip().splitlines():
            k = line.split(':')[0]
            v = input(f"Please enter {k} and press enter:\n").strip()
            if v.isdigit():
                v = int(v)
            inpt[k] = v

fill_poc_trek()
