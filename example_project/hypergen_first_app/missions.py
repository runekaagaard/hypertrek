d = dict

from hypergen.imports import *

import os, re, calendar

from hypertrek import hypertrek
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
    def render_options(name, title, i):
        label(title)
        with div():
            value = select([option(b, value=a) for a, b in BOOKINGS[i]], name=name, id_="booking_value",
                           coerce_to=int)

        return {name: value}

    def _():
        if data["done"]:
            p("You booked: ", data["date"], " / ", data["month"], " at ",
              [b for a, b in BOOKINGS[2] if a == data["time"]][0])
            label("Cancel?")
            with div():
                value = input_(type_="checkbox", id_="booking_value")

                return {"cancel": value}

        with ul(class_="errorlist"):
            for error in errors:
                li(error)

        if not data["month"]:
            return render_options("month", "Select month", 0)
        elif not data["date"]:
            return render_options("date", "Select date", 1)
        elif not data["time"]:
            return render_options("time", "Select time for appointment", 2)
        else:
            if data["time"] > 16:
                label("Are you OK with a late booking?")
                with div():
                    value = input_(type_="checkbox", id_="booking_value")

                return {"late_ok": value}

            return {"late_ok": None}

    return _

def booking_progress(state):
    if "booking" not in state:
        return (3, 4, None)

    if not state["booking"]["month"]:
        return (3, 4, 1)
    elif not state["booking"]["date"]:
        return (3, 4, 2)
    elif not state["booking"]["time"]:
        return (3, 4, 3)

    if state["booking"]["time"] < 17:
        return (3, 3, 3)
    else:
        return (4, 4, 4)

@hypertrek.mission(concerns=d(rendering=d(text=booking_text, hypergen=booking_hypergen)), configurator=None,
                   progress=booking_progress)
def booking(*, state, method, first, inpt=None, **configuration):
    initial = {"month": None, "date": None, "time": None, "late_ok": None, "done": False}
    if "booking" not in state:
        state["booking"] = initial.copy()

    errors = []

    command = hypertrek.RETRY
    if method == "post":
        if inpt.pop("cancel", None):
            state["booking"] = initial.copy()
            print("FOO", state["booking"])
        else:
            state["booking"].update(inpt)

        if state["booking"]["time"]:
            if state["booking"]["time"] < 17:
                state["booking"]["done"] = True
                command = hypertrek.CONTINUE
            else:
                if state["booking"]["late_ok"] is True:
                    state["booking"]["done"] = True
                    command = hypertrek.CONTINUE
                elif state["booking"]["late_ok"] is False:
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

@hypertrek.mission(concerns=d(rendering=d(text=template_text, hypergen=template_hypergen)), configurator=None,
                   progress=lambda *a, **kw: (1, 1, 1))
def template(title, description, *, state, method, first, inpt=None, **configuration):
    command = hypertrek.RETRY
    if inpt:
        command = hypertrek.CONTINUE

    concerns = template.hypertrek["concerns"].copy()
    concerns["rendering"] = {k: v(title, description, **configuration) for k, v in concerns["rendering"].items()}

    return command, state, concerns
