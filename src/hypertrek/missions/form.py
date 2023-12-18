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

    # TODO: Think about passing errors over to for instance text mode. Should that be out-of-band?
    print("errors: ", repr(form.errors), repr(form.non_field_errors()))

    return "\n".join(f"{name}: {form[name].label}{choices(form.fields[name])}" for name in form.fields)

def html(*t, **tt):
    return "<p></p>"

def docs(*t, **tt):
    return "### docs"

@mission(renderers=d(html=html, text=text, docs=docs), configurator=FormConfigurator)
def form(form_class, /, *, state, inpt, fields="__all__", renderers=("html", "text", "docs"), **configuration):
    form_ = form_class(data=inpt)
    if form_.is_valid():
        command = trek.CONTINUE
        state.update(form_.cleaned_data)
    else:
        command = trek.RETRY

    return command, state, d(
        renders={x: form.hypertrek["renderers"][x](form_, **configuration) for x in renderers})
