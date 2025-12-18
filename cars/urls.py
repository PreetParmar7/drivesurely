from django.urls import path
from . import views
from .views import CustomLoginView
urlpatterns = [
    path('', views.home, name='home'),
    path('cars/', views.car_list, name='car_list'),
    path('cars/<int:id>/', views.car_detail, name='car_detail'),
    path('dashboard/', views.dealer_dashboard, name='dealer_dashboard'),
    path('cars/add/', views.add_car, name='add_car'),
    path('cars/edit/<int:id>/', views.edit_car, name='edit_car'),
    path('cars/delete/<int:id>/', views.delete_car, name='delete_car'),
    path('cars/<int:id>/enquire/', views.send_enquiry, name='send_enquiry'),
    path('dealer/enquiries/', views.dealer_enquiries, name='dealer_enquiries'),
    path('register/', views.register, name='register'),
    path('dealer/enquiry/<int:id>/status/', views.update_enquiry_status, name='update_enquiry_status'),
    path('dealer/enquiry/<int:id>/reply/', views.reply_enquiry, name='reply_enquiry'),
    path('my-enquiries/', views.my_enquiries, name='my_enquiries'),
    path('login/', CustomLoginView.as_view(template_name='login.html'), name='login'),
    path('compare/add/<int:id>/', views.add_to_compare, name='add_to_compare'),
    path('compare/', views.compare_cars, name='compare'),
    path('wishlist/add/<int:id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/', views.wishlist, name='wishlist'),
    path('wishlist/remove/<int:id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('compare/', views.compare_cars, name='compare'),
    path('compare/add/<int:id>/', views.add_to_compare, name='add_to_compare'),
    path('compare/clear/', views.clear_compare, name='clear_compare'),
    path('contact/', views.contact, name='contact'),
    path('dealer/status/', views.dealer_status, name='dealer_status'),
    path(
    'dealer/<str:username>/',
    views.dealer_public_profile,
    name='dealer_public_profile'
),
    path('dealer/<str:username>/review/', views.add_dealer_review, name='add_dealer_review'),
    path('dealer/profile/edit/', views.edit_dealer_profile, name='edit_dealer_profile'),
    path(
    'dealer/<str:username>/review/',
    views.add_dealer_review,
    name='add_dealer_review'
),
    path(
    'dealer/review/<int:review_id>/reply/',
    views.reply_to_review,
    name='reply_to_review'
),
    path('review/<int:review_id>/edit/', views.edit_review, name='edit_review'),
    path('review/<int:review_id>/delete/', views.delete_review, name='delete_review'),
    #path('dealer/status/', views.dealer_status, name='dealer_status'),
   
]