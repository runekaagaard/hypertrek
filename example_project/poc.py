from enum import CONFORM
import os, re, json

from django.test.testcases import ValidationError

from hypertrek import missions as ms
from hypertrek import trek

import django
from django import forms

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'example_project.settings')
django.setup()

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
    ]

def fill_poc_trek():
    state = None
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

        text = side_effects["renders"]["text"]
        for section in text.strip().split("\n---\n\n"):
            ansi_escape = re.compile(r'\x1b\[.*?m')
            clean_text = ansi_escape.sub('', section)
            pattern = r"details:.*?\bname=([^\s]+)"
            k = re.search(pattern, clean_text, re.MULTILINE).group(1)

            print(section)
            v = input(f"new value (or - for current): ").strip()
            if v != "-":
                inpt[k] = int(v) if v.isdigit() else v
            print()

    os.system('clear')

    title = f"Trek completed"
    print(title)
    print("=" * len(title))
    print()
    print(json.dumps(state, indent=4))
    print()
    print("thxbai!")

fill_poc_trek()
