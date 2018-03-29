from django import forms


class BootstrapFormMixin(object):

    def __init__(self, *args, **kwargs):
        super(BootstrapFormMixin, self).__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({
                'class': 'form-control'
            })


class ContactForm1(BootstrapFormMixin, forms.Form):
    subject = forms.CharField(max_length=100)
    sender = forms.EmailField()


class ContactForm2(BootstrapFormMixin, forms.Form):
    message = forms.CharField(widget=forms.Textarea)
