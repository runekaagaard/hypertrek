d = dict

from hypertrek import hypertrek
from hypertrek import missions as ms

from hypergen_first_app.missions import template, booking
from hypergen_first_app.forms import ExampleForm, WHO5Form

@hypertrek.trek(title="Example Trek")
def example_trek():
    return [
        template("This is the beginning", "Lets go!"),
        ms.form.form(ExampleForm, fields=["name", "description"]),
        ms.form.form(ExampleForm, fields=["options"]),
        template("This is the middle", "Super great!"),
        booking(),
        ms.form.form(ExampleForm, fields=["num_int", "num_float"]),
        *sub_trek(),
        template("This is the ending", "Finally!"),
    ]

@hypertrek.trek(title="Sub Trek")
def sub_trek():
    return [
        template("Easy Peasy", "Lets go!"),
        ms.form.form(WHO5Form, fields=["q1"]),
        ms.form.form(WHO5Form, fields=["q2"], when=lambda state: state.get("q1") == 5),
        ms.form.form(WHO5Form, fields=["q3"]),
        ms.form.form(WHO5Form, fields=["q4"]),
        ms.form.form(WHO5Form, fields=["q5"]),
        template("Not great!", "Sorry ..."),
    ]
