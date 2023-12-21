from prompt_toolkit import PromptSession, prompt
from prompt_toolkit.completion import FuzzyWordCompleter
from prompt_toolkit.input.defaults import create_input
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.output.defaults import create_output
from prompt_toolkit.shortcuts import PromptSession
from prompt_toolkit.validation import ValidationError as PTValidationError, Validator
from termcolor import colored
from prompt_toolkit import print_formatted_text, ANSI

from django import forms
from django.forms import ValidationError

def cprint(txt):
    return print_formatted_text(ANSI(txt))

def prompt_value(label, default=None, value_type=str, max_length=None, multiline=False, choices=None, session=None,
                 errors=None, required=False):
    class Validate(Validator):
        def validate(self, document):
            if required and not document.text.strip():
                raise PTValidationError(message=f"Value required")
            try:
                if document.text:
                    value_type(document.text)
            except ValueError:
                raise PTValidationError(message=f"Value type must be {value_type.__name__}")
            if max_length:
                assert value_type is str
                if len(document.text) > max_length:
                    raise PTValidationError(message=f"Value must be {max_length} characters or less")

            if valid_choices and document.text not in valid_choices:
                raise PTValidationError(message=f"Not a valid choice, try again!")

    valid_choices = None
    if choices:
        valid_choices = set([str(x[0]) for x in choices])

    prmpt = session.prompt if session else prompt
    prompt_text = colored(label, "yellow")
    if errors:
        prompt_text += "\n"
        for error in errors:
            prompt_text += colored(f"  - {error}\n", "red")
    prompt_text += colored(": ", "yellow")

    completer = None
    if choices:
        completer = FuzzyWordCompleter([f"{k}: {v}" for k, v in choices])

    return value_type(
        prmpt(ANSI(prompt_text), validator=Validate(), multiline=multiline, mouse_support=True, default=default,
              completer=completer))

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
        default = form.initial.get(field_name)

    return prompt_value(
        field_name,
        str(default) if default is not None else "",
        value_type=value_type,
        max_length=getattr(field, "max_length", None),
        multiline=isinstance(field.widget, forms.Textarea),
        choices=getattr(field, "choices", None),
        errors=form[field_name].errors,
        required=field.required,
    )

def prompt_form(form):
    if form.non_field_errors():
        for error in form.non_field_errors():
            print(colored(f"- {error}", 'red'))

        print()

    result = {}
    for field_name in form.fields.keys():
        result[field_name] = prompt_field(form, field_name)

    return result

# import django
# from django import forms
# from django.conf import settings

# settings.configure(DEBUG=True, SECRET_KEY='ssh', ROOT_URLCONF=__name__)
# django.setup()
