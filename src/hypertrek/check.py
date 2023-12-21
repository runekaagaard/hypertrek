from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.validation import Validator, ValidationError

# Example completer
color_completer = WordCompleter(['red', 'green', 'blue', 'yellow'], ignore_case=True)

# Example validator
class ColorValidator(Validator):
    def validate(self, document):
        text = document.text
        if text not in ['red', 'green', 'blue', 'yellow']:
            raise ValidationError(message="This input is not a valid color", cursor_position=len(text))

# Using prompt with validator and completer
user_input = prompt("Enter a color: ", validator=ColorValidator(), completer=color_completer)

print("You entered:", user_input)
