from django import forms


class ContactMessageForm(forms.Form):
    email = forms.EmailField(
        label="ایمیل",
        widget=forms.EmailInput(
            attrs={"placeholder": "یک ایمیل معتبر وارد کنید"}
        ),
    )
    name = forms.CharField(
        label="نام",
        max_length=100,
        widget=forms.TextInput(attrs={"placeholder": "نام خود را وارد کنید"}),
    )
    message = forms.CharField(
        label="پیام",
        required=False,
        widget=forms.Textarea(
            attrs={"placeholder": "پیام شما (اختیاری)", "rows": 4}
        ),
    )
