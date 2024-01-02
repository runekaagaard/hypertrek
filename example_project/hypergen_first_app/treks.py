d = dict

from hypergen_first_app.missions import template, booking
from hypergen_first_app.forms import ExampleForm
from hypertrek import missions as ms

def example_trek():
    return [
        template("This is the beginning", "Lets go!"),
        ms.form.form(ExampleForm, fields=["name", "description"]),
        ms.form.form(ExampleForm, fields=["options"]),
        template("This is the middle", "Super great!"),
        booking(),
        ms.form.form(ExampleForm, fields=["num_int", "num_float"]),
        template("This is the ending", "Finally!"),
    ]
