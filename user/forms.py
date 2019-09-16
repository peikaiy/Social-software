from django import forms

from user.models import Profile


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['location', 'min_distance', 'max_distance', 'min_dating_age',
                  'max_dating_age', 'dating_sex', 'vibration', 'only_matche',
                  'auto_play']

    def clean_max_distance(self):
        '''检查交友距离'''
        cleaned_data = super().clean()
        min_distance = cleaned_data['min_distance']
        max_distance = cleaned_data['max_distance']

        if min_distance > max_distance:
            raise forms.ValidationError('min_distance > max_distance')
        return max_distance

    def clean_max_dating_age(self):
        '''检查交友年龄'''
        cleaned_data = super().clean()
        min_dating_age = cleaned_data['min_dating_age']
        max_dating_age = cleaned_data['max_dating_age']

        if min_dating_age > max_dating_age:
            raise forms.ValidationError('min_dating_age > max_dating_age')
        return max_dating_age
