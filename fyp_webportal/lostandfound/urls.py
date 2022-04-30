from django.urls import path
from lostandfound import views

urlpatterns = [
    path('dashboard', 
         views.LostFoundTable.as_view(), 
         name='item-dashboard'),

    path('dashboard/<int:item_id>', 
         views.LostItem.as_view(),
         name='item-info'),
]