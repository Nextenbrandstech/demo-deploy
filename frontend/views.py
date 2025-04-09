from django.shortcuts import render


def fk_insights_page(request):
    return render(request, 'frontend/fk_page.html')

def amz_insights_page(request):
    return render(request, 'frontend/amz_page.html')

def d2c_insights_page(request):
    return render(request, 'frontend/d2c_page.html')

def meesho_insights_page(request):
    return render(request, 'frontend/meesho_page.html')

def jiomart_insights_page(request):
    return render(request, 'frontend/jiomart_page.html')

def platform_selector_page(request):
    return render(request, 'frontend/platform_selector.html')

