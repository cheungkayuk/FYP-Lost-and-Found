from django.shortcuts import render
from django.views.generic import TemplateView
from lostandfound.models import *

class LostFoundTable(TemplateView):
    template_name = "landf_table.html"

    def get_context_data(self, **kwargs): 
        context = super().get_context_data(**kwargs)
        context['Unhandled_item_list'] = LostFoundItem.objects.filter(status="Unhandled")
        context['Processing_item_list'] = LostFoundItem.objects.filter(status="Processing")
        context['Handled_item_list'] = LostFoundItem.objects.filter(status="Handled")
        context['unhandled_number'] = len(context['Unhandled_item_list'])
        return context

class LostItem(TemplateView):
    template_name = "landf_item_info.html"

    def get_context_data(self, **kwargs):
        item_id = self.kwargs['item_id']

        context = super().get_context_data(**kwargs)
        context['item'] = LostFoundItem.objects.get(pk = item_id)
        return context