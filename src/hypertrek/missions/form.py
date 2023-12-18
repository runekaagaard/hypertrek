import io
from termcolor import colored

from django import forms

from hypertrek.missions import mission
from hypertrek import trek

d = dict

class FormConfigurator(forms.Form):
    # args
    html_template = forms.CharField(required=True, max_length=80)
    fields = forms.Textarea()

    # kwargs
    title = forms.CharField(max_length=16)
    subtitle = forms.CharField(max_length=32)
    description = forms.Textarea()
    help_text = forms.Textarea()

    def mission_args(self):
        return [self.cleaned_data[x] for x in ("template", "fields")]

    def mission_kwargs(self):
        return {
            x: self.cleaned_data[x]
            for x in ("title", "subtitle", "description", "help_text", "template", "fields")
        }

def text(form, **configuration):
    def choices(field):
        if not hasattr(field, "choices"):
            return ""

        choices = ", ".join(f"{a}={b}" for a, b in field.choices)

        return f" ({choices})"

    with io.StringIO() as buffer:
        for field in form:
            # Header: Field label in yellow
            buffer.write(colored(f"{field.label}\n", 'yellow', attrs=['bold']))

            # Print field errors in red
            if field.errors:
                for error in field.errors:
                    buffer.write(colored(f"Error: {error}\n", 'red'))

            # Representation of the field type
            field_type = field.field.__class__.__name__
            buffer.write(f"Type: {field_type}\n")

            # Display current value of the field
            current_value = field.value()
            if current_value is not None:
                if hasattr(field.field, 'choices'):
                    # For fields with choices, display the readable choice
                    readable_value = dict(field.field.choices).get(current_value, current_value)
                    buffer.write(f"Current Value: {readable_value} (raw: {current_value})\n")
                else:
                    buffer.write(f"Current Value: {current_value}\n")

            # Display choices for fields like ChoiceField
            if hasattr(field.field, 'choices'):
                choices = field.field.choices
                buffer.write("Options:\n")
                for value, label in choices:
                    buffer.write(f"  {value}: {label}\n")

            # Print help text in grey
            if field.help_text:
                buffer.write(colored(f"Help: {field.help_text}\n", 'grey'))

            buffer.write("\n")  # Add a newline for separation between fields

        return buffer.getvalue()

def html(*t, **tt):
    return "<p></p>"

def docs(*t, **tt):
    return "### docs"

@mission(renderers=d(html=html, text=text, docs=docs), configurator=FormConfigurator)
def form(form_class, /, *, state, inpt, fields="__all__", renderers=("html", "text", "docs"), **configuration):
    form_ = form_class(data=inpt if inpt else None)
    if inpt and form_.is_valid():
        print("vALIDININIENIGNIENG")
        command = trek.CONTINUE
        state.update(form_.cleaned_data)
    else:
        command = trek.RETRY

    return command, state, d(
        renders={x: form.hypertrek["renderers"][x](form_, **configuration) for x in renderers})
