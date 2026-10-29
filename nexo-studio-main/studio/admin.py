from django.contrib import admin
from .models import Business, Page, Offering, Activity
class PageInline(admin.TabularInline): model=Page; extra=0
@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin): list_display=('name','owner','sector','published','created_at'); search_fields=('name','owner__username'); prepopulated_fields={}
admin.site.register(Page)
admin.site.register(Offering)
admin.site.register(Activity)

from .models import FAQItem, ChatInteraction
admin.site.register(FAQItem)
admin.site.register(ChatInteraction)
