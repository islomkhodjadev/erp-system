from django.urls import path
from . import views

urlpatterns = [
    path('order/<str:language>', views.order_view, name='order_form'), 
    path("get_plintus_component/<int:plintus_code>/", views.get_components_by_plintus_code, name='getplintus_component'),
    
]
