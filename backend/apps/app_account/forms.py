import re

from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.exceptions import ValidationError

from .models import TradingAccount, User

_PERSIAN_DIGITS = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")


def normalize_digits(value: str) -> str:
    return (value or "").translate(_PERSIAN_DIGITS).strip()


def validate_phone_number(value: str) -> str:
    phone = normalize_digits(value)
    phone = re.sub(r"[\s\-]", "", phone)
    if not re.fullmatch(r"\d{11}", phone):
        raise ValidationError("شماره تلفن باید دقیقاً ۱۱ رقم باشد.")
    return phone


def validate_national_id(value: str) -> str:
    national_id = normalize_digits(value)
    national_id = re.sub(r"[\s\-]", "", national_id)
    if not national_id:
        return ""
    if not re.fullmatch(r"\d{10}", national_id):
        raise ValidationError("کد ملی باید دقیقاً ۱۰ رقم باشد.")
    return national_id


class SignupForm(UserCreationForm):
    username = forms.CharField(
        label="نام کاربری",
        max_length=150,
        widget=forms.TextInput(
            attrs={
                "placeholder": "نام کاربری خود را وارد کنید",
                "autocomplete": "username",
            }
        ),
    )
    email = forms.EmailField(
        label="ایمیل",
        widget=forms.EmailInput(
            attrs={
                "placeholder": "m@example.com",
                "autocomplete": "email",
            }
        ),
        help_text="از این ایمیل برای ارتباط با شما استفاده می‌شود.",
    )
    phone_number = forms.CharField(
        label="شماره تلفن",
        max_length=11,
        min_length=11,
        widget=forms.TextInput(
            attrs={
                "placeholder": "09121234567",
                "autocomplete": "tel",
                "inputmode": "numeric",
                "maxlength": "11",
                "pattern": r"\d{11}",
            }
        ),
        help_text="شماره تلفن باید ۱۱ رقم باشد.",
    )
    password1 = forms.CharField(
        label="رمز عبور",
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "حداقل ۸ کاراکتر",
                "autocomplete": "new-password",
            }
        ),
        help_text="رمز عبور باید حداقل ۸ کاراکتر باشد.",
    )
    password2 = forms.CharField(
        label="تأیید رمز عبور",
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "رمز عبور را تکرار کنید",
                "autocomplete": "new-password",
            }
        ),
        help_text="لطفاً رمز عبور را تأیید کنید.",
    )

    class Meta:
        model = User
        fields = ("username", "email", "phone_number")

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("این ایمیل قبلاً ثبت شده است.")
        return email

    def clean_phone_number(self):
        return validate_phone_number(self.cleaned_data["phone_number"])


class LoginForm(AuthenticationForm):
    """Accept username or email in the username field."""

    username = forms.CharField(
        label="نام کاربری یا ایمیل",
        widget=forms.TextInput(
            attrs={
                "placeholder": "نام کاربری یا ایمیل",
                "autocomplete": "username",
            }
        ),
    )
    password = forms.CharField(
        label="رمز عبور",
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "رمز عبور",
                "autocomplete": "current-password",
            }
        ),
    )
    remember_me = forms.BooleanField(
        label="مرا به خاطر بسپار",
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={"class": "remember-me-input"}),
    )

    error_messages = {
        "invalid_login": "نام کاربری/ایمیل یا رمز عبور نادرست است.",
        "inactive": "این حساب غیرفعال است.",
    }


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "national_id",
        )
        labels = {
            "first_name": "نام",
            "last_name": "نام خانوادگی",
            "email": "ایمیل",
            "phone_number": "شماره تلفن",
            "national_id": "کد ملی",
        }
        widgets = {
            "first_name": forms.TextInput(attrs={"placeholder": "نام"}),
            "last_name": forms.TextInput(attrs={"placeholder": "نام خانوادگی"}),
            "email": forms.EmailInput(attrs={"placeholder": "m@example.com"}),
            "phone_number": forms.TextInput(
                attrs={
                    "placeholder": "09121234567",
                    "inputmode": "numeric",
                    "maxlength": "11",
                    "pattern": r"\d{11}",
                }
            ),
            "national_id": forms.TextInput(
                attrs={
                    "placeholder": "0012345678",
                    "inputmode": "numeric",
                    "maxlength": "10",
                    "pattern": r"\d{10}",
                }
            ),
        }

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        qs = User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError("این ایمیل قبلاً ثبت شده است.")
        return email

    def clean_phone_number(self):
        return validate_phone_number(self.cleaned_data["phone_number"])

    def clean_national_id(self):
        return validate_national_id(self.cleaned_data.get("national_id", ""))


class TradingAccountForm(forms.ModelForm):
    class Meta:
        model = TradingAccount
        fields = ("trading_acc_username", "broker")
        labels = {
            "trading_acc_username": "شماره حساب",
            "broker": "نام کارگزاری",
        }
        widgets = {
            "trading_acc_username": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "شماره حساب ترید",
                    "autocomplete": "off",
                }
            ),
            "broker": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "نام کارگزاری",
                    "autocomplete": "organization",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.is_bound:
            for name, field in self.fields.items():
                if self.errors.get(name):
                    css = field.widget.attrs.get("class", "")
                    field.widget.attrs["class"] = f"{css} is-invalid".strip()

    def clean_trading_acc_username(self):
        value = (self.cleaned_data.get("trading_acc_username") or "").strip()
        if not value:
            raise ValidationError("شماره حساب الزامی است.")
        if not re.fullmatch(r"[A-Za-z0-9._-]+", value):
            raise ValidationError(
                "شماره حساب فقط می‌تواند شامل حروف، اعداد، نقطه، خط تیره و زیرخط باشد."
            )
        return value

    def clean_broker(self):
        value = (self.cleaned_data.get("broker") or "").strip()
        if not value:
            raise ValidationError("نام کارگزاری الزامی است.")
        return value


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
