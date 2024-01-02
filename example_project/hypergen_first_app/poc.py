d = dict

import os, re, calendar
from example_project.hypergen_first_app.treks import poc_trek

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
    thetrek = poc_trek()
    state = trek.new_state()
    is_done = False

    i = 0
    while is_done is False:
        inpt, direction_change = {}, None
        while True:
            os.system('clear')

            progress = trek.progress(thetrek, state)
            title = f'Mission: {state["hypertrek"]["i"]+1} of {progress[0]}-{progress[1]}'
            print(title)
            print("=" * len(title))
            print()

            i += 1
            # Display page
            cmd, state, concerns = trek.get(thetrek, state)
            log(inpt, state, cmd, i, direction_change)
            direction_change, inpt = concerns["rendering"]["text"]()

            # Validate input
            cmd, state, concerns = trek.post(thetrek, state, inpt)
            log(inpt, state, cmd, i, direction_change)

            if direction_change == trek.BACKWARD:
                direction = trek.backward
                break
            else:
                if direction_change == trek.FORWARD:
                    # When skipping forward, validate with state as input.
                    # TODO: This is wrong!
                    cmd, state, concerns = trek.post(thetrek, state, state)
                if cmd == trek.CONTINUE:
                    direction = trek.forward
                    break

        is_done, state = direction(thetrek, state)

    os.system('clear')
    title = f"Trek completed"
    print(title)
    print("=" * len(title))

    print()
    print(dumps(state, indent=4))
    print()
    print("thxbai!")

# fill_poc_trek()
