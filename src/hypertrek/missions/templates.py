from hypergen.imports import *

# Hypergen python templates
def form_mission(form, id_="hypertrek_form", *args, **kwargs):
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
