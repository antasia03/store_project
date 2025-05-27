from store.models import Size, Profile
from django import forms

class ChooseSizeForm(forms.Form):
    size = forms.ModelChoiceField(
        queryset=Size.objects.all(),
        empty_label="Выберите размер",
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Размер"
    )

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['name', 'surname', 'birthday', 'address', 'phone_number', 'telegram_user_id']