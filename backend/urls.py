

from django.urls import path
from .views import (login_view, logout_view, fk_insights_view, amz_insights_view, platform_selector_view, 
                    d2c_insights_view, meesho_insights_view, jiomart_insights_view, flipkart_pnl_view, amz_pnl_view)

urlpatterns = [
    path('', login_view, name='login'),  # Set the root URL to point to the login view
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),

    path('platform_selector/', platform_selector_view, name='platform_selector'),

    path('api/fk_insights/', fk_insights_view, name='fk_insights'),
    path('api/fk_pnl_details/', flipkart_pnl_view, name='fk_pnl_details'),

    path('api/amz_insights/', amz_insights_view, name='amz_insights'),
    path('api/amz_pnl_details/', amz_pnl_view, name='amz_pnl_details'),

    path('api/d2c_insights/', d2c_insights_view, name='d2c_insights'),

    path('api/meesho_insights/', meesho_insights_view, name='meesho_insights'),

    path('api/jiomart_insights/', jiomart_insights_view, name='jiomart_insights'),
]