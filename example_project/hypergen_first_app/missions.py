d = dict

from hypergen.imports import *

import os, re, calendar

from hypertrek.missions import mission
from hypertrek import trek
from hypertrek.prompt import prompt_value

from django import forms
from django.core.exceptions import ValidationError

from termcolor import colored

### Booking mission ###

BOOKINGS = [
    [(i, calendar.month_name[i]) for i in range(1, 13)],
    [(x, str(x)) for x in range(1, 30)],
    [(x, f"{x}:00-{x+1}:00") for x in range(9, 18)],
]

def booking_text(data, errors, **configuration):
    def _():
        if errors:
            for error in errors:
                print(colored(f"- {error}", 'red'))
            print()
        if "booking" in data:
            for k, v in data["booking"].items():
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

        return None, {"booking": {"month": value1, "date": value2, "time": value3, "late_ok": value4}}

    return _

def booking_hypergen(data, errors, **configuration):
    def _():
        i = len(data)
        keys = ["month", "date", "time", "late OK?"]
        key = keys[i]

        label(key.capitalize())
        with p():
            if i < 3:
                value = select([option(label, value=pk) for pk, label in BOOKINGS[i]], id_="booking_value",
                               coerce_to=int)
            else:
                if data[-1] > 16:
                    value = input_(type_="checkbox", id_="booking_value")
                else:
                    value = None
        hprint(data=data, i=i, errors=errors)
        return value

    return _

def booking_pageno(state):
    try:
        if state["booking"]["time"] > 16:
            return (4, 4)
        else:
            return (3, 3)
    except KeyError:
        return (3, 4)

@mission(concerns=d(rendering=d(text=booking_text, hypergen=booking_hypergen)), configurator=None,
         pageno=booking_pageno)
def booking(*, state, method, first, inpt=None, **configuration):
    if "booking" not in state:
        state["booking"] = []

    errors = []

    if method == "post":
        state["booking"].append(inpt)

    l = len(state["booking"])
    command = trek.RETRY
    if l == 3 and state["booking"][-1] <= 16:
        command = trek.CONTINUE
    elif l == 4:
        if state["booking"][-1] is True:
            command = trek.CONTINUE
        else:
            errors.append("Choose an earlier time, then!")

    concerns = booking.hypertrek["concerns"].copy()
    concerns["rendering"] = {
        k: v(state["booking"], errors, **configuration) for k, v in concerns["rendering"].items()
    }

    return command, state, concerns

### Template mission ###

def template_hypergen(title, description):
    def _():
        h2(title)
        p(description)

        return True

    return _

def template_text(title, description):
    def _():
        print(colored(title, attrs=["bold"]))
        print()
        print(description)
        print()
        direction_change, _ = prompt_value("Press enter to continue", required=False)
        return direction_change, True

    return _

@mission(concerns=d(rendering=d(text=template_text, hypergen=template_hypergen)), configurator=None,
         pageno=lambda *a, **kw: (1, 1))
def template(title, description, *, state, method, first, inpt=None, **configuration):
    command = trek.RETRY
    if inpt:
        command = trek.CONTINUE

    concerns = template.hypertrek["concerns"].copy()
    concerns["rendering"] = {k: v(title, description, **configuration) for k, v in concerns["rendering"].items()}

    return command, state, concerns
