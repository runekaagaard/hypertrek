from prompt_toolkit import PromptSession, prompt
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.input.defaults import create_input
from prompt_toolkit.output.defaults import create_output
from prompt_toolkit.shortcuts import PromptSession
from prompt_toolkit.validation import Validator, ValidationError

class DjangoFieldValidator(Validator):
    def __init__(self, django_field):
        self.django_field = django_field

    def validate(self, document):
        text = document.text
        # Perform type-specific validation
        if isinstance(self.django_field, forms.IntegerField):
            if text and not text.isdigit():
                raise ValidationError(message="This field requires a valid integer.", cursor_position=len(text))

def prompt_field(form, field_name, session=None):
    field = form.fields[field_name]
    current_value = form.cleaned_data.get(field_name, field.initial) if form.is_bound else field.initial
    prompt_text = f"{field.label if field.label else field_name} (current: {current_value}): "

    # Create a validator for the field
    validator = DjangoFieldValidator(field)

    # Multiline for Textarea
    multiline = isinstance(field.widget, forms.Textarea)

    if session:
        # Use provided session for history
        return session.prompt(prompt_text, multiline=multiline, validator=validator)
    else:
        # Prompt without a session
        return prompt(prompt_text, multiline=multiline, validator=validator, mouse_support=True)

def prompt_value(label, value_current, value_type=str, max_length=None, multiline=False, session=None):
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
    prompt_text = f"{label} ({value_current}): "
    return value_type(prmpt(prompt_text, validator=Validate(), multiline=multiline, mouse_support=True))

test_cases = [
    ["Enter your name", "John Doe", str, 8, False],
    ["Enter a description", "This is line 1.\nThis is line 2.", str, None, True],
    ["Enter your age", "30", int, None, False],
    ["Enter a float value", "3.14", float, None, False],
]

# Iterate over the test cases and call prompt_value for each
for label, current_value, value_type, max_length, multiline in test_cases:
    result = prompt_value(label, current_value, value_type, max_length, multiline)
    print(f"Result for '{label}': {result}")

import django
from django.conf import settings

settings.configure(DEBUG=True, SECRET_KEY='ssh', ROOT_URLCONF=__name__)
django.setup()

from django import forms

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

# form = PocForm(data=dict(numb=999))
# form.is_valid()
# field_value = prompt_field(form, 'numb')
# print(field_value)
