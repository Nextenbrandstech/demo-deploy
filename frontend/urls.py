from django.urls import path
from .views import fk_insights_page, amz_insights_page, platform_selector_page, d2c_insights_page, meesho_insights_page, jiomart_insights_page

urlpatterns = [
    path('fk_insights/', fk_insights_page, name='fk_insights_page'),
    path('amz_insights/', amz_insights_page, name='amz_insights_page'),
    path('d2c_insights/', d2c_insights_page, name='d2c_insights_page'),
    path('meesho_insights/', meesho_insights_page, name='meesho_insights_page'),
    path('jiomart_insights/', jiomart_insights_page, name='jiomart_insights_page'),
    path('platform_selector/', platform_selector_page, name='platform_selector_page'),
]

