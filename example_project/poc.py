d = dict

import os, re, calendar

from hypergen.imports import dumps

from hypertrek.missions import mission
from hypertrek import missions as ms
from hypertrek import trek
from hypertrek.prompt import prompt_value

import django
from django import forms
from django.core.exceptions import ValidationError

from termcolor import colored

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'example_project.settings')
django.setup()

BOOKINGS = [
    [(i, calendar.month_name[i]) for i in range(1, 13)],
    [(x, str(x)) for x in range(0, 30)],
    [(x, f"{x}:00-{x+1}:00") for x in range(9, 18)],
]

def booking_text(data, errors, **configuration):
    def _():
        if errors:
            for error in errors:
                print(colored(f"- {error}", 'red'))
            print()
        if data:
            for k, v in data.items():
                print(f"{k}: {v}")
            print()

        direction_change, value1 = prompt_value("month", data.get("month"), value_type=int, choices=BOOKINGS[0],
                                                required=True)
        if direction_change:
            return direction_change, None
        direction_change, value2 = prompt_value("date", data.get("date"), value_type=int, choices=BOOKINGS[1],
                                                required=True)
        if direction_change:
            return direction_change, None
        direction_change, value3 = prompt_value("time", data.get("time"), value_type=int, choices=BOOKINGS[2],
                                                required=True)
        if direction_change:
            return direction_change, None
        if value3 > 16:
            direction_change, value4 = prompt_value("Is it OK it's late?", data.get("late_ok"), value_type=int,
                                                    choices=((0, "Nope!"), (1, "Yep!")), required=True)
            value4 = bool(value4)
            if direction_change:
                return direction_change, None
        else:
            value4 = None

        return None, {"month": value1, "date": value2, "time": value3, "late_ok": value4}

    return _

def booking_pageno(state):
    try:
        if state["booking"]["time"] > 16:
            return (4, 4)
        else:
            return (3, 3)
    except KeyError:
        return (3, 4)

@mission(concerns=d(rendering=d(text=booking_text)), configurator=None, pageno=booking_pageno)
def booking(*, state, inpt, first, **configuration):
    if inpt is None:
        inpt = {}

    errors = []

    command = trek.RETRY
    if not first and inpt:
        if inpt.get("late_ok", None) is False:
            errors.append("Choose an earlier time then!")
        else:
            command = trek.CONTINUE
            state["booking"] = inpt

    concerns = booking.hypertrek["concerns"].copy()
    concerns["rendering"] = {
        k: v(inpt if inpt else state.get("booking", {}), errors, **configuration)
        for k, v in concerns["rendering"].items()
    }

    return command, state, concerns

def template_text(title, description):
    def _():
        print(colored(title, attrs=["bold"]))
        print()
        print(description)
        print()
        direction_change, _ = prompt_value("Press enter to continue", required=False)
        return direction_change, True

    return _

@mission(concerns=d(rendering=d(text=template_text)), configurator=None, pageno=lambda *a, **kw: (1, 1))
def template(title, description, *, state, inpt, first, **configuration):
    command = trek.RETRY
    if inpt:
        command = trek.CONTINUE

    concerns = template.hypertrek["concerns"].copy()
    concerns["rendering"] = {k: v(title, description, **configuration) for k, v in concerns["rendering"].items()}

    return command, state, concerns

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
        template("This is the beginning", "Lets go!"),
        ms.form.form(PocForm, fields=["name", "description"]),
        ms.form.form(PocForm, fields=["options"]),
        template("This is the middle", "Super great!"),
        booking(),
        ms.form.form(PocForm, fields=["num_int", "num_float"]),
        template("This is the ending", "Finally!"),
    ]

def log(inpt, state, command, i, direction_change):
    msg = f"""
i == {i}
command = {command}
direction_change = {direction_change}
    
Input
=====

{dumps(inpt, indent=4)}

Command
=======

{command}
    
State
=====

{dumps(state, indent=4)}
    """.strip()

    with open("/tmp/hypertrek.log", "w") as f:
        f.write(msg)

def fill_poc_trek():
    thetrek, state = trek.init(poc_trek)
    is_done = False

    i = 0
    while is_done is False:
        inpt, direction_change = {}, None
        while True:
            os.system('clear')

            pageno = trek.pageno(thetrek, state)
            title = f'Mission: {state["hypertrek"]["i"]+1} of {pageno[0]}-{pageno[1]}'
            print(title)
            print("=" * len(title))
            print()

            i += 1
            # Display page
            cmd, state, concerns = trek.execute(thetrek, state, inpt)
            log(inpt, state, cmd, i, direction_change)
            direction_change, inpt = concerns["rendering"]["text"]()

            # Validate input
            cmd, state, concerns = trek.execute(thetrek, state, inpt)
            log(inpt, state, cmd, i, direction_change)

            if direction_change == trek.BACKWARD:
                direction = trek.backward
                break
            else:
                if direction_change == trek.FORWARD:
                    # When skipping forward, validate with state as input.
                    cmd, state, concerns = trek.execute(thetrek, state, state)
                if cmd == trek.CONTINUE:
                    direction = trek.forward
                    break

        is_done, state = direction(thetrek, state)

    title = f"Trek completed"
    print(title)
    print("=" * len(title))

    print()
    print(dumps(state, indent=4))
    print()
    print("thxbai!")

fill_poc_trek()
