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

def text(form):
    with io.StringIO() as buffer:
        # Display non-field errors at the top
        if form.non_field_errors():
            buffer.write(colored("Form errors:\n", 'white', attrs=['bold']))
            for error in form.non_field_errors():
                buffer.write(colored(f"  - {error}\n", 'red'))

            buffer.write("\n")

        # Summarize field errors at the top
        field_errors = [colored(field.name, 'red') for field in form if field.errors]
        if field_errors:
            buffer.write(colored("Field errors: ", 'white', attrs=['bold']) + ', '.join(field_errors) + "\n")
            buffer.write("\n")

        for i, field in enumerate(form, start=1):
            # Field header (label) in bold yellow
            buffer.write(colored(f"{i}. {field.label}\n", 'yellow', attrs=['bold']))

            # Field details
            field_details = [
                colored("key=", 'white') + colored(f"{field.name}", 'cyan'),
                colored("type=", 'white') + colored(f"{field.field.__class__.__name__}", 'cyan'),
                colored("widget=", 'white') + colored(f"{field.field.widget.__class__.__name__}", 'cyan'),
                colored("name=", 'white') + colored(f"{field.html_name}", 'cyan'),
                colored('placeholder="', 'white') +
                colored(f"{field.field.widget.attrs.get('placeholder', '')}", 'cyan') + colored('"', 'white'),
                colored('id="', 'white') + colored(f"{field.auto_id}", 'cyan') + colored('"', 'white'),
                colored('class="', 'white') + colored(f"{field.field.widget.attrs.get('class', '')}", 'cyan') +
                colored('"', 'white')
            ]
            buffer.write("details: " + ' | '.join(field_details) + "\n")

            # "help_text" key in white, help text in grey
            if field.help_text:
                buffer.write(colored("help_text: ", 'white') + colored(f"{field.help_text}\n", 'grey'))

            # Choices for ChoiceField
            if hasattr(field.field, 'choices'):
                choices = field.field.choices
                buffer.write("choices:\n")
                for idx, (value, label) in enumerate(choices, start=1):
                    if idx == 7:  # Limit display to 8 choices
                        buffer.write(f"  ... [{len(choices) - 7} more choices]\n")
                        break
                    buffer.write(f"  {value}: {label}\n")
                if len(choices) > 505:
                    buffer.write(f"  {choices[-1][0]}: {choices[-1][1]}\n")

            # Errors in red
            if field.errors:
                buffer.write(colored("errors:\n", 'white'))
                for error in field.errors:
                    buffer.write(colored(f"  - {error}\n", 'red'))

            # Current value
            current_value = field.value() if field.value() is not None else ""
            buffer.write(f"current value: \"{current_value}\"\n")
            buffer.write("---\n")

            # Only a single empty line between fields
            if i < len(form.fields):
                buffer.write("\n")

        return buffer.getvalue()

def html(*t, **tt):
    return "<p></p>"

def docs(*t, **tt):
    return "### docs"

def form_factory(form_class, fields):
    class FormFactory(form_class):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

            self.fields = {k: v for k, v in self.fields.items() if k in fields}

    return FormFactory  # Todo: rename to fit form_class

@mission(renderers=d(html=html, text=text, docs=docs), configurator=FormConfigurator)
def form(form_class, /, *, state, inpt, fields=None, renderers=("html", "text", "docs"), **configuration):
    form_class = form_class if fields is None else form_factory(form_class, fields)
    form_ = form_class(data=inpt if inpt else None)
    if inpt and form_.is_valid():
        command = trek.CONTINUE
        state.update(form_.cleaned_data)
    else:
        command = trek.RETRY

    return command, state, d(
        renders={x: form.hypertrek["renderers"][x](form_, **configuration) for x in renderers})
