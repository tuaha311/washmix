from django.forms.widgets import TextInput


class ButtonInput(TextInput):
    template_name = "widgets/button.html"
