from django.urls import path, reverse
from . import views
from django.urls import path
from .views import chart_page,register_view, login_view,dashboard,logout_view,technical_indicators_view,stock_screener,candlestick_patterns_view
urlpatterns = [
    path('register/', register_view, name='register_view'),
    path('login/', login_view, name='login_view'),
    path('dashboard/', dashboard, name='stock_dashboard'),
    path('logout/', logout_view, name='logout_view'), 
    path('chart/', chart_page, name='chart_page'),  
    
    # path("technical/<str:stock_symbol>/<str:start_date>/<str:end_date>/<str:chart_type>/", stock_technical_view, name="technical_indicators"),

    # path('technical/<str:symbol>/<str:start_date>/<str:end_date>/<str:chart_type>/',views.stock_technical_view, name='technical_indicators'),
    # path('technical/<str:symbol>/<str:start_date>/<str:end_date>/<str:chart_type>/', views.stock_technical_view, name='technical_indicators'),

    path('screener/<str:symbol>/', views.stock_screener, name='stock_screener'),
    path('data/<str:stock_symbol>/<str:start_date>/<str:end_date>/<str:chart_type>/', views.data_page, name='data_page'), 

    path('data/<str:stock_symbol>/<str:start_date>/<str:end_date>/<str:chart_type>/', views.data_page, name='data_page'),
    
    
    path('news-dashboard/', views.stock_news, name='news_dashboard'),
    
    path('forecast/', views.stock_forecast, name='stock_forecast'),

    
    path('pattern-checker/', views.pattern_checker, name='pattern_checker'),
    #path('stock-details/', views.stock_details_view, name='stock_details'),
    #path('indicators/', views.technical_indicators, name='technical_indicators'),

    path('technical-indicators/<str:symbol>/<str:start_date>/<str:end_date>/<str:chart_type>/', views.technical_indicators_view, name='technical_indicators'),
]
