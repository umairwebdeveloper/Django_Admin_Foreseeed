
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views


urlpatterns = [

    path('', views.index, name='index'),
    path('pricing/', views.pricing, name='pricing'),
    path('features/', views.features, name='features'),
    path('about-us/', views.about_us, name='about_us'),
    path('book-demo/', views.demo, name='demo'),
    path('login/', views.login_fn, name='login'),
    path('register/', views.register, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),  
    path('upload-file/', views.file_upload, name='file_upload'),
    path('forecastings/', views.forecastings, name='forecastings'),
    path('budget_allocator/', views.budgetallocator, name="budget_allocator"),
    path('budget_allocator/results', views.budgetallocatorresults, name="budget_allocator_results"),
    path('faqs/', views.faqs, name='faqs'),
    path('logout/', views.logout_user, name='logout'),
    # path('new_login/', views.new_login, name='new_login'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
