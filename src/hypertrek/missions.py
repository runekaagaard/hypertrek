d = dict

def as_html():
    return "<p></p>"

def as_text():
    return "1. "

def as_docs():
    return "### docs"

def form(side_effects=d(html=as_html, text=as_text, docs=as_docs), configurator=FormConfigurator):
    pass
