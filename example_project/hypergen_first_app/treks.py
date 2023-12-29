d = dict

from hypergen_first_app.missions import template, booking
from hypergen_first_app.forms import PocForm
from hypertrek import missions as ms

def poc_trek():
    return [
        # template("This is the beginning", "Lets go!"),
        # ms.form.form(PocForm, fields=["name", "description"]),
        # ms.form.form(PocForm, fields=["options"]),
        # template("This is the middle", "Super great!"),
        booking(),
        ms.form.form(PocForm, fields=["num_int", "num_float"]),
        template("This is the ending", "Finally!"),
    ]
