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
            x: self.cleaned_data[x] for x in ("title", "subtitle", "description", "help_text", "template", "fields")
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

    FormFactory.__name__ = form_class.__name__ + '_Factory'

    return FormFactory

@mission(concerns=d(rendering=d(html=html, text=text, docs=docs)), configurator=FormConfigurator,
         pageno=lambda state: (1, 1))
def form(form_class, /, *, state, inpt, first, fields, **configuration):
    form_class = form_class if fields is None else form_factory(form_class, fields)
    data = {x: inpt.get(x, state.get(x)) for x in fields}

    form_ = form_class(initial=data if first else None, data=data if not first else None)

    if not first and form_.is_valid():
        command = trek.CONTINUE
        state.update(form_.cleaned_data)
    else:
        command = trek.RETRY

    concerns = form.hypertrek["concerns"].copy()
    concerns["rendering"] = {k: v(form_, **configuration) for k, v in concerns["rendering"].items()}

    return command, state, concerns
