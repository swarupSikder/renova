from django import forms
from events.models import Event


# - - - - - - - - - - - - - - - #
#      Form Styling Mixin       #
# - - - - - - - - - - - - - - - #
class StyledFormMixin:
    default_input_classes = "bg-white border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full px-4 py-2 mb-4"
    default_textarea_classes = "bg-white border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full px-4 py-2 h-32 resize-none mb-4"
    default_select_classes = "bg-white border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full px-4 py-2 mb-4"
    default_date_time_classes = "bg-white border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full px-4 py-2 mb-4"

    def apply_styled_widgets(self):
        for field_name, field in self.fields.items():
            widget = field.widget

            if isinstance(widget, forms.Textarea):
                widget.attrs.update({
                    'class': self.default_textarea_classes,
                    'placeholder': f"Enter {field.label.lower()}",
                })
            elif isinstance(widget, forms.Select):
                widget.attrs.update({
                    'class': self.default_select_classes,
                })
            elif isinstance(widget, (forms.DateInput, forms.TimeInput)):
                widget.attrs.update({
                    'class': self.default_date_time_classes,
                    'type': 'date' if isinstance(widget, forms.DateInput) else 'time'
                })
            else:
                widget.attrs.update({
                    'class': self.default_input_classes,
                    'placeholder': f"Enter {field.label.lower()}",
                })


# - - - - - - - - - - - #
#    Add Event Form     #
# - - - - - - - - - - - #
class EventModelForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Event
        fields = ['name', 'description', 'date', 'time', 'location', 'category']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_styled_widgets()
