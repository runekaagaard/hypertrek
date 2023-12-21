from prompt_toolkit import Application
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.layout import Layout, HSplit, VSplit, Window
from prompt_toolkit.layout.controls import BufferControl, FormattedTextControl
from prompt_toolkit.widgets import Frame
from prompt_toolkit.key_binding import KeyBindings

# Function to return sidebar content
def get_sidebar_content():
    return [
        ('class:sidebar', 'Global State:\n'),
        ('class:sidebar', ' - State Info 1\n'),
        ('class:sidebar', ' - State Info 2\n'),
        ('class:sidebar', 'Current Input:\n'),
        ('class:sidebar', '\n')  # Placeholder for current input
    ]

# Creating the main buffer and input area
main_buffer = Buffer()
input_area = Window(BufferControl(buffer=main_buffer))

# Creating the sidebar
sidebar_content = FormattedTextControl(get_sidebar_content)
sidebar = Window(content=sidebar_content, width=30)

# Key bindings for the application
kb = KeyBindings()

@kb.add('c-c')
@kb.add('c-q')
def exit_(event):
    event.app.exit()

# Layout
layout = Layout(HSplit([VSplit([Frame(input_area), sidebar])]))

# Application
application = Application(layout=layout, key_bindings=kb, full_screen=True)

def run():
    application.run()

run()
