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

class booking(hypertrek.mission):
    def execute(self, *, state, method, first, inpt=None):
        initial = {"month": None, "date": None, "time": None, "late_ok": None, "done": False}
        if "booking" not in state:
            state["booking"] = initial.copy()

        errors = []

        command = hypertrek.RETRY
        if method == "post":
            if inpt.pop("cancel", None):
                state["booking"] = initial.copy()
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

        return command, state, self, ((state["booking"], errors), {})

    def progress(self, state):
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

    def as_hypergen(self, data, errors):
        def render_options(name, title, i):
            label(title)
            with div():
                value = select([option(b, value=a) for a, b in BOOKINGS[i]], name=name, id_="booking_value",
                               coerce_to=int)

            return {name: value}

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

    def as_terminal(self, data, errors):
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

class template(hypertrek.mission):
    def __init__(self, title, description, *args, **kwargs):
        self.title = title
        self.description = description

        super().__init__(*args, **kwargs)

    def execute(self, state, method, first, inpt=None):
        command = hypertrek.RETRY
        if inpt:
            command = hypertrek.CONTINUE

        return command, state, self, (tuple(), {})

    def as_hypergen(self, *args, **kwargs):
        h2(self.title)
        p(self.description)

        return True

    def as_html(self, *args, **kwargs):
        return "todo"

    def as_terminal(self, *args, **kwargs):
        # TODO.
        print(colored(self.title, attrs=["bold"]))
        print()
        print(self.description)
        print()
        direction_change, _ = prompt_value("Press enter to continue", required=False)
        return direction_change, True
