d = dict
from hypergen.imports import raw, form as form_, script
from hypertrek import hypertrek
from hypertrek.prompt import prompt_form
from hypertrek.missions import templates

from django import forms

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

def form_factory(form_class, fields):
    class FormFactory(form_class):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

            self.fields = {k: v for k, v in self.fields.items() if k in fields}

    FormFactory.__name__ = form_class.__name__ + '_Factory'

    return FormFactory

class form(hypertrek.mission):
    def __init__(self, form_class, fields=None, hypergen_template=templates.form_mission, *args, **kwargs):
        self.form_class = form_class
        self.fields = fields
        self.hypergen_template = hypergen_template

        super().__init__(*args, **kwargs)

    def execute(self, state, method, first, inpt=None):
        if method == "get":
            data = {x: state.get(x) for x in self.fields}
        else:
            data = inpt

        form_class = self.form_class if self.fields is None else form_factory(self.form_class, self.fields)
        form_instance = form_class(initial=data if first else None, data=data if not first else None)

        command = hypertrek.RETRY
        if method == "post" and not first and form_instance.is_valid():
            command = hypertrek.CONTINUE
            state.update(form_instance.cleaned_data)

        return command, state, self, ((form_instance,), {})

    def as_hypergen(self, form):
        return self.hypergen_template(form, id_="hypertrek_form")

    def input_from_request(self, request):
        return {
            name: field.widget.value_from_datadict(request.POST, request.FILES, name)
            for name, field in self.form_class().fields.items() if self.fields is None or name in self.fields
        }

    def as_html(self, form):
        return str(form)

    def as_terminal(self, form):
        return prompt_form(form)
