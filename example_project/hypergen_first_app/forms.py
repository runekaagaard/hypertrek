from django import forms
from django.core.exceptions import ValidationError

class PocForm(forms.Form):
    name = forms.CharField(max_length=16, label="What's your name?", help_text="Please enter your name.")
    description = forms.CharField(widget=forms.Textarea, label="Write a few words about yourself ...",
                                  help_text="Dont' be shy!")
    options = forms.ChoiceField(choices=[("a", "A"), ("b", "B"), ("c", "C")], label="Which one?",
                                help_text="Choose one, god dammit!")
    num_int = forms.IntegerField()
    num_float = forms.FloatField()

    def clean(self):
        if self.cleaned_data.get("name", None) == "jeppe":
            raise ValidationError("I don't think so!")
        if self.cleaned_data.get("options", None) == "b":
            raise ValidationError("NEVER choose b!")
