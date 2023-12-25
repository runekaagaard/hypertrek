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
        direction_change, value1 = prompt_value("date", "", value_type=int, choices=BOOKINGS[0], required=True)
        if direction_change:
            return direction_change, None
        direction_change, value2 = prompt_value("time", "", value_type=int, choices=BOOKINGS[1], required=True)
        if direction_change:
            return direction_change, None

        return None, [value1, value2]

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
    num_int = forms.IntegerField()
    num_float = forms.FloatField()

    def clean(self):
        if self.cleaned_data.get("name", None) == "jeppe":
            raise ValidationError("I don't think so!")
        if self.cleaned_data.get("options", None) == "b":
            raise ValidationError("NEVER choose b!")

def poc_trek():
    return [
        ms.form.form(PocForm, fields=["name", "description"]),
        ms.form.form(PocForm, fields=["options"]),
        booking(),
        ms.form.form(PocForm, fields=["num_int", "num_float"]),
    ]

def log(inpt, state, command, i, direction_change):
    msg = f"""
i == {i}
command = {command}
direction_change = {direction_change}
    
Input
=====

{json.dumps(inpt, indent=4)}

Command
=======

{command}
    
State
=====

{json.dumps(state, indent=4)}
    """.strip()

    with open("/tmp/hypertrek.log", "w") as f:
        f.write(msg)

def fill_poc_trek():
    state = {}
    command = trek.CONTINUE
    inpt = {}
    i = 0
    direction_change = None
    while True:
        i += 1
        if direction_change is None:
            command, state, side_effects = trek.forward(poc_trek, state=state, inpt=inpt)
        elif direction_change == trek.BACKWARD:
            command, state, side_effects = trek.backward(poc_trek, state=state)
            direction_change = None
        elif direction_change == trek.FORWARD:
            command, state, side_effects = trek.forward(poc_trek, state=state, inpt=inpt)
            direction_change = None
        else:
            raise Exception(f"TODO: {direction_change}")
        log(inpt, state, command, i, direction_change)
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

        direction_change, inpt = side_effects["renders"]["text"]()
        log(inpt, state, command, i, direction_change)

    os.system('clear')

    title = f"Trek completed"
    print(title)
    print("=" * len(title))
    print()
    print(json.dumps(state, indent=4))
    print()
    print("thxbai!")

fill_poc_trek()
