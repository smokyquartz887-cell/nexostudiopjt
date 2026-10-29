from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from security.uploads import validate_image_upload
from .models import Business, Page, Offering, Activity, FAQItem

class SignUpForm(UserCreationForm):
    email=forms.EmailField(required=True)
    class Meta:
        model=User; fields=('username','email','password1','password2')
    def save(self,commit=True):
        user=super().save(commit=False); user.email=self.cleaned_data['email']
        if commit: user.save()
        return user
class BusinessForm(forms.ModelForm):
    class Meta:
        model=Business; fields=['name','sector','tagline','description','email','phone','address','primary_color','secondary_color','accent_color','font_style','hero_image','uploaded_hero','logo','published']
        widgets={'description':forms.Textarea(attrs={'rows':4}),'primary_color':forms.TextInput(attrs={'type':'color'}),'secondary_color':forms.TextInput(attrs={'type':'color'}),'accent_color':forms.TextInput(attrs={'type':'color'}),'published':forms.CheckboxInput()}
    def clean_uploaded_hero(self):
        return validate_image_upload(self.cleaned_data.get('uploaded_hero'), max_size=5 * 1024 * 1024, label='imagem de destaque')
    def clean_logo(self):
        return validate_image_upload(self.cleaned_data.get('logo'), max_size=2 * 1024 * 1024, label='logo')
class PageForm(forms.ModelForm):
    class Meta:
        model=Page; fields=['title','menu_label','body','is_visible','sort_order']; widgets={'body':forms.Textarea(attrs={'rows':6})}
class OfferingForm(forms.ModelForm):
    class Meta:
        model=Offering; fields=['kind','name','description','price','active']; widgets={'description':forms.Textarea(attrs={'rows':3})}
class ActivityForm(forms.ModelForm):
    class Meta:
        model=Activity; fields=['title','kind','status','amount','activity_date','notes']; widgets={'activity_date':forms.DateInput(attrs={'type':'date'}),'notes':forms.Textarea(attrs={'rows':3})}


class FAQItemForm(forms.ModelForm):
    class Meta:
        model = FAQItem
        fields = ['question', 'answer', 'keywords', 'active']
        widgets = {'answer': forms.Textarea(attrs={'rows': 5}), 'keywords': forms.TextInput(attrs={'placeholder': 'horário, entrega, pagamento'})}
