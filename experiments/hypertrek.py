"""
Missions:

- take an optional namespace, otherwise it's automatic.
- takes state and an optional input. Can mutate state and return new state
- can contain more than one user-facing page, so should report progress
- supports running without side-effects like saving to DB, sending emails, etc.
- support different representation modes like HTML, strings, documentation, etc.
- are configurable from both code and UI

Treks:

- Can include other treks into a sub namespace

"""

d = dict

def stub(*a, **kwargs):
    pass

def mission(f, *a, **kw):
    return f

MyModelForm, modelform_save, include, template = [stub] * 4

from django import forms

class ModelFormConfigurator(forms.Form):
    # args
    template = TemplateField(required=True)
    fields = FieldsField(required=True)

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

@mission(side_effects=d(html=as_html, text=as_text, docs=as_docs), configurator=ModelFormConfigurator)
def modelform(form, fields, template, /, *, state, inpt, **configuration):
    return state, side_effects

def mytrek():
    return [
        modelform(MyModelForm, "myapp/myformtemplate.html", ["name", "age"], title="Super great!"),
        modelform(MyModelForm, myhypergentemplate, ["preferences", "items"]),
        modelform(MyModelForm),  # configured fully from UI
        modelform_save(MyModelForm),
        include(mysubtrek),
    ]

def mysubtrek():
    return [
        template("myapp/mytemplate.html"),
    ]
