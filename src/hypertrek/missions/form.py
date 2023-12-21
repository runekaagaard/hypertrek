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
    from hypertrek.prompt import prompt_form
    return lambda: prompt_form(form)

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
