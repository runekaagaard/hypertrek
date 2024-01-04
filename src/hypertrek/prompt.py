import os

from hypergen.imports import dumps

from prompt_toolkit import prompt
from prompt_toolkit.completion import FuzzyWordCompleter
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.validation import ValidationError as PTValidationError, Validator
from prompt_toolkit import print_formatted_text, ANSI
from prompt_toolkit.application.current import get_app

from termcolor import colored

from django import forms
from django.forms import ValidationError

from hypertrek import hypertrek

BACKWARD, FORWARD = "BACKWARD", "FORWARD"

def cprint(txt):
    return print_formatted_text(ANSI(txt))

bindings = KeyBindings()

@bindings.add('c-f')
def forward(event):
    event.app.exit(exception=EOFError(FORWARD), style='class:aborting')

@bindings.add('c-b')
def backward(event):
    event.app.exit(exception=EOFError(BACKWARD), style='class:aborting')

def prompt_value(label, default="", value_type=str, max_length=None, multiline=False, choices=None, session=None,
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
        prmpt(ANSI(prompt_text), validator=Validate(), multiline=multiline, mouse_support=True,
              default=str(default) if default else "", completer=completer, key_bindings=bindings))

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

    for field_name in form.fields.keys():
        if form.is_bound:
            default = form[field_name].field.bound_data(form[field_name].data, form.initial.get(field_name))
        else:
            default = form.initial.get(field_name)

        print(colored(f"{field_name}: "), default)

    print()

    result = {}
    for field_name in form.fields.keys():
        result[field_name] = prompt_field(form, field_name)

    return result

def log_run_trek(state, inpt):
    msg = f"""
Input
=====

{dumps(inpt, indent=4)}
    
State
=====

{dumps(state, indent=4)}
    """.strip()

    with open("/tmp/hypertrek.log", "w") as f:
        f.write(msg)

def run_trek(trek):
    state, is_done, inpt = hypertrek.new_state(), False, None

    while not is_done:
        cmd, state, mission, (as_args, as_kwargs) = hypertrek.get(trek, state)
        log_run_trek(state, inpt)

        try:
            while cmd != hypertrek.CONTINUE:
                os.system('clear')
                progress = hypertrek.progress(trek, state)
                title = f'Mission: {state["hypertrek"]["i"]+1} of {progress[0]}-{progress[1]}'
                print(title)
                print("=" * len(title))
                print()

                inpt = mission.as_terminal(*as_args, **as_kwargs)
                cmd, state, mission, (as_args, as_kwargs) = hypertrek.post(trek, state, inpt)
                log_run_trek(state, inpt)
            if state["hypertrek"]["at_end"]:
                is_done = True
                break
            state = hypertrek.forward(trek, state)
        except EOFError as e:
            assert str(e) in (FORWARD, BACKWARD)
            inpt = None
            if str(e) == FORWARD:
                state = hypertrek.forward(trek, state)
            elif str(e) == BACKWARD:
                state = hypertrek.backward(trek, state)

    os.system('clear')
    title = f"Trek completed"
    print(title)
    print("=" * len(title))

    print()
    print(dumps(state, indent=4))
    print()
    print("thxbai!")
