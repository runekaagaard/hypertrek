d = dict

from enum import CONFORM
import os, re, json

from django.test.testcases import ValidationError
from hypertrek.missions import mission

from hypertrek import missions as ms
from hypertrek import trek
from hypertrek.prompt import prompt_value

import django
from django import forms

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'example_project.settings')
django.setup()

BOOKINGS = [
    [(x, str(x)) for x in [1, 2, 3, 4, 5, 7, 7]],
    [(x, str(x)) for x in [9, 10, 11, 12, 13, 14, 15, 18]],
]

def render_booking(**configuration):
    def _():
        result = []
        result.append(prompt_value("date", "", value_type=int, choices=BOOKINGS[0], required=True))
        result.append(prompt_value("time", "", value_type=int, choices=BOOKINGS[1], required=True))

        return result

    return _

@mission(renderers=d(text=render_booking), configurator=None)
def booking(*, state, inpt, renderers=("text",), **configuration):
    if inpt:
        command = trek.CONTINUE
        state["booking"] = inpt
    else:
        command = trek.RETRY

    return command, state, d(renders={x: booking.hypertrek["renderers"][x](**configuration) for x in renderers})

class PocForm(forms.Form):
    name = forms.CharField(max_length=16, label="What's your name?", help_text="Please enter your name.")
    description = forms.CharField(widget=forms.Textarea, label="Write a few words about yourself ...",
                                  help_text="Dont' be shy!")
    options = forms.ChoiceField(choices=[("a", "A"), ("b", "B"), ("c", "C")], label="Which one?",
                                help_text="Choose one, god dammit!")

    def clean(self):
        if self.cleaned_data.get("options", None) == "b":
            raise ValidationError("NEVER choose b!")

def poc_trek():
    return [
        ms.form.form(PocForm, fields=["name", "description"]),
        ms.form.form(PocForm, fields=["options"]),
        booking(),
    ]

def fill_poc_trek():
    state = {"name": "ok", "description": "hmm"}
    command = trek.CONTINUE
    inpt = {}
    while True:
        command, state, side_effects = trek.forward(poc_trek, state=state, inpt=inpt)
        if command == trek.TERMINATED:
            break
        elif command == trek.CONTINUE:
            inpt = {}
            continue

        os.system('clear')

        title = f"Mission: {state['mission_index']}"
        print(title)
        print("=" * len(title))
        print()

        inpt = side_effects["renders"]["text"]()

    os.system('clear')

    title = f"Trek completed"
    print(title)
    print("=" * len(title))
    print()
    print(json.dumps(state, indent=4))
    print()
    print("thxbai!")

fill_poc_trek()
