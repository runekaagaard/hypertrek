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

def hypergen(form):
    from hypergen.imports import raw, form as form_, script
    def _(id_="hypertrek_form"):
        script("""
                function formValues(formId) {
                    const form = document.getElementById(formId);
                    const data = {};

                    Array.from(form.elements).forEach(element => {
                        if (element.name && !element.disabled) {
                            switch (element.type) {
                                case 'checkbox':
                                    data[element.name] = element.checked;
                                    break;
                                case 'number':
                                    data[element.name] = element.step && element.step === '1'
                                        ? parseInt(element.value)
                                        : parseFloat(element.value);
                                    break;
                                case 'radio':
                                    if (element.checked) {
                                        data[element.name] = isNaN(parseInt(element.value))
                                            ? element.value
                                            : parseInt(element.value);
                                    }
                                    break;
                                case 'select-one':
                                case 'select-multiple':
                                    const selectedValue = element.options[element.selectedIndex].value;
                                    data[element.name] = isNaN(parseInt(selectedValue))
                                        ? selectedValue
                                        : parseInt(selectedValue);
                                    break;
                                default:
                                    data[element.name] = element.value;
                            }
                        }
                    });

                    return data;
                }
            """)
        with form_(id_=id_, js_value_func="formValues") as form_values:
            raw(form.as_div())

        return form_values

    return _

def docs(*t, **tt):
    return "### docs"

def form_factory(form_class, fields):
    class FormFactory(form_class):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

            self.fields = {k: v for k, v in self.fields.items() if k in fields}

    FormFactory.__name__ = form_class.__name__ + '_Factory'

    return FormFactory

@mission(concerns=d(rendering=d(hypergen=hypergen, text=text, docs=docs)), configurator=FormConfigurator,
         pageno=lambda state: (1, 1))
def form(form_class, /, *, state, method, first, fields, inpt=None, **configuration):
    if method == "get":
        data = {x: state.get(x) for x in fields}
    elif method == "post":
        data = {x: inpt.get(x, state.get(x)) for x in fields}

    form_class = form_class if fields is None else form_factory(form_class, fields)
    form_instance = form_class(initial=data if first else None, data=data if not first else None)

    if not first and form_instance.is_valid():
        command = trek.CONTINUE
        state.update(form_instance.cleaned_data)
    else:
        command = trek.RETRY

    concerns = form.hypertrek["concerns"].copy()
    concerns["rendering"] = {k: v(form_instance, **configuration) for k, v in concerns["rendering"].items()}

    return command, state, concerns
