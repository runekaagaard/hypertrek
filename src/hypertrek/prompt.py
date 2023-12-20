from prompt_toolkit import PromptSession, prompt
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.input.defaults import create_input
from prompt_toolkit.output.defaults import create_output
from prompt_toolkit.shortcuts import PromptSession
from prompt_toolkit.validation import Validator, ValidationError

def prompt_value(label, value_type=str, max_length=None, multiline=False, session=None):
    class Validate(Validator):
        def validate(self, document):
            try:
                if document.text:
                    value_type(document.text)
            except ValueError:
                raise ValidationError(message=f"Value type must be {value_type.__name__}")
            if max_length:
                assert value_type is str
                if len(document.text) > max_length:
                    raise ValidationError(message=f"Value must be {max_length} characters or less")

    prmpt = session.prompt if session else prompt
    prompt_text = f"{label}: "
    return value_type(prmpt(prompt_text, validator=Validate(), multiline=multiline, mouse_support=True))

test_cases = [
    ["name", str, 8, False],
    ["description", str, None, True],
    ["age", int, None, False],
    ["temperatur", float, None, False],
]

# data = {}
# for name, value_type, max_length, multiline in test_cases:
#     data[name] = prompt_value(name, value_type, max_length, multiline)

# print()
# print(data)

import django
from django import forms

from django.conf import settings

settings.configure(DEBUG=True, SECRET_KEY='ssh', ROOT_URLCONF=__name__)
django.setup()

class PocForm(forms.Form):
    name = forms.CharField(max_length=16, label="What's your name?", help_text="Please enter your name.")
    description = forms.CharField(widget=forms.Textarea, label="Write a few words about yourself ...",
                                  help_text="Dont' be shy!")
    options = forms.ChoiceField(choices=[("a", "A"), ("b", "B"), ("c", "C")], label="Which one?",
                                help_text="Choose one, god dammit!")
    numb = forms.IntegerField()

    def clean(self):
        if self.cleaned_data.get("options", None) == "b":
            raise ValidationError("NEVER choose b!")

def prompt_field(field):
    input_type = getattr(field.widget, "input_type", None)
    print(input_type)

form = PocForm(data=dict(numb=999))
for field in form.fields.values():
    prompt_field(field)

# form.is_valid()
# field_value = prompt_field(form, 'numb')
# print(field_value)
