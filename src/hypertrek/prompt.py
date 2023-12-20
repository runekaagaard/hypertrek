from prompt_toolkit import PromptSession, prompt
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.input.defaults import create_input
from prompt_toolkit.output.defaults import create_output
from prompt_toolkit.shortcuts import PromptSession
from prompt_toolkit.validation import Validator, ValidationError
from prompt_toolkit.completion import FuzzyWordCompleter

def prompt_value(label, default=None, value_type=str, max_length=None, multiline=False, choices=None,
                 session=None):
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

    completer = None
    if choices:
        completer = FuzzyWordCompleter([f"{k}: {v}" for k, v in choices])

    return value_type(
        prmpt(prompt_text, validator=Validate(), multiline=multiline, mouse_support=True, default=default,
              completer=completer))

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
    num_float = forms.FloatField()

    def clean(self):
        if self.cleaned_data.get("options", None) == "b":
            raise ValidationError("NEVER choose b!")

def prompt_field(form, field_name):
    field = form.fields[field_name]
    input_type = getattr(field.widget, "input_type", None)
    value_type = {"number": int, "text": str}.get(input_type, str)
    if value_type is int:
        step = field.widget.attrs.get('step', '1')
        try:
            if step == "any" or int(step) != float(step):
                value_type = float
        except ValueError:
            pass

    if form.is_bound:
        default = form[field_name].field.bound_data(form[field_name].data, form.initial.get(field_name))
    else:
        default = form.initial[field_name]

    prompt_value(
        field_name,
        str(default) if default is not None else "",
        value_type=value_type,
        max_length=getattr(field, "max_length", None),
        multiline=isinstance(field.widget, forms.Textarea),
        choices=getattr(field, "choices", None),
    )

form = PocForm(data=dict(numb=999), initial=dict(name="poop"))
# form.is_valid()
for field_name in form.fields.keys():
    prompt_field(form, field_name)

# form.is_valid()
# field_value = prompt_field(form, 'numb')
# print(field_value)

# promt_value = prompt_value("name", "Baby Boy", str, 16)
