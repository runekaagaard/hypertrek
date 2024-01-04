from django import forms
from django.core.exceptions import ValidationError

class ExampleForm(forms.Form):
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

class WHO5Form(forms.Form):
    q1 = forms.ChoiceField(
        label="I have felt cheerful and in good spirits", choices=[(0, "At no time"), (1, "Some of the time"),
                                                                   (2, "Less than half of the time"),
                                                                   (3, "More than half of the time"),
                                                                   (4, "Most of the time"),
                                                                   (5, "All of the time")],
        widget=forms.RadioSelect)
    q2 = forms.ChoiceField(
        label="I have felt calm and relaxed", choices=[(0, "At no time"), (1, "Some of the time"),
                                                       (2, "Less than half of the time"),
                                                       (3, "More than half of the time"), (4, "Most of the time"),
                                                       (5, "All of the time")], widget=forms.RadioSelect)
    q3 = forms.ChoiceField(
        label="I have felt active and vigorous", choices=[(0, "At no time"), (1, "Some of the time"),
                                                          (2, "Less than half of the time"),
                                                          (3, "More than half of the time"),
                                                          (4, "Most of the time"), (5, "All of the time")],
        widget=forms.RadioSelect)
    q4 = forms.ChoiceField(
        label="I woke up feeling fresh and rested", choices=[(0, "At no time"), (1, "Some of the time"),
                                                             (2, "Less than half of the time"),
                                                             (3, "More than half of the time"),
                                                             (4, "Most of the time"), (5, "All of the time")],
        widget=forms.RadioSelect)
    q5 = forms.ChoiceField(
        label="My daily life has been filled with things that interest me",
        choices=[(0, "At no time"), (1, "Some of the time"), (2, "Less than half of the time"),
                 (3, "More than half of the time"), (4, "Most of the time"),
                 (5, "All of the time")], widget=forms.RadioSelect)
