from django.shortcuts import render
from datetime import datetime
from backend.models import (First_step_AdsData_FK, First_step_InvoiceData_FK, First_step_SalesData_FK, First_step_cogs_vertical, First_step_FK_Return_data,
                            First_step_Master_SKU, Jr_Sr_AdsData_FK_MP, Jr_Sr_cogs, Jr_Sr_cogs_master_sku, Jr_Sr_InvoiceData_FK, Jr_Sr_FK_Return_data,
                            Jr_Sr_SalesData_FK, First_step_SB_Ads_AMZ, First_step_CODBFeesData_AMZ, First_step_SalesData_AMZ, First_step_SD_Ads_AMZ,
                            First_step_SP_Ads_AMZ, First_step_ReturnData_AMZ, NexTen_AdsData_FK_MP, NexTen_COGS_Master_SKU, NexTen_InvoiceData_FK, NexTen_SalesData_FK, NexTen_Return_data)

from django.http import JsonResponse
import json
from backend.services.data_analysis import (get_fk_insights, get_dynamic_plot_flipkart, demographic_plot_flipkart, pie_chart_flipkart,
                                            all_brand_Flipkart, all_brand_map_Flipkart, all_brand_pie_Flipkart, all_brand_dynamic_plot_Flipkart,
                                            Flipkart_PnL_calculator, get_fk_insights_multi_brand, Flipkart_PnL_calculator_multi_brand)

from backend.services.data_analysis_amz import (get_AMZ_insights, get_dynamic_plot_AMZ, demographic_plot_AMZ, pie_chart_AMZ, Amazon_PnL_calculator,
                                                all_brand_dynamic_plot_AMZ, all_brand_AMZ, all_brand_map_AMZ, all_brand_pie_AMZ)


import logging
import base64
from io import BytesIO
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/frontend/platform_selector/')
            
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'frontend/login.html')


def logout_view(request):
    logout(request)
    return redirect('/backend/login/')


# for the platform selector page
@login_required(login_url='/backend/login/')
def platform_selector_view(request):
    if request.method == 'POST':
        platform = request.POST.get('platform')
        if platform == 'flipkart':
            print('Flipkart selected')
            return redirect('/frontend/fk_insights/')  # Redirect to Flipkart insights page
        elif platform == 'amazon':
            print('Amazon selected')
            return redirect('/frontend/amz_insights/')  # Redirect to Amazon insights page
        elif platform == 'd2c':
            print('D2C selected')
            return redirect('/frontend/d2c_insights/')
    return render(request, 'frontend/platform_selector.html')  # Render platform selector template



# Flipkart Insights
@login_required(login_url='/backend/login/')
def fk_insights_view(request):

    print("fk_insights_view has been summoned")

    # 1) Read existing params
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    seller = request.GET.get('seller')
    brand = request.GET.get('brand')
    
    print(f"the seller is {seller}")
    print(f"the brand is {brand}")

    # 3) Convert string dates (start_date_str, end_date_str) to datetime
    if start_date_str and end_date_str:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
    else:
        start_date = None
        end_date = None


    # 5) Use your existing brand lookups
    brand_models = {
        "TRI": {
            "sales": First_step_SalesData_FK,
            "ads": First_step_AdsData_FK,
            "invoices": First_step_InvoiceData_FK,
            "master_sku": First_step_Master_SKU,
            "cogs": First_step_cogs_vertical,
            "returns": First_step_FK_Return_data
        },
        "Amour Hygiene": {
            "sales": Jr_Sr_SalesData_FK,
            "ads": Jr_Sr_AdsData_FK_MP,
            "invoices": Jr_Sr_InvoiceData_FK,
            "master_sku": Jr_Sr_cogs_master_sku,
            "cogs": Jr_Sr_cogs,
            "returns": Jr_Sr_FK_Return_data
        },
        "NexTen Brands": {
            "sales": NexTen_SalesData_FK,
            "ads": NexTen_AdsData_FK_MP,
            "invoices": NexTen_InvoiceData_FK,
            "master_sku": NexTen_COGS_Master_SKU,
            "cogs": NexTen_COGS_Master_SKU,
            "returns": NexTen_Return_data
        }
    }

    if seller == "All Seller":
        print(f"all seller case is triggered!!!")
        insights = all_brand_Flipkart(start_date, end_date)
        
        demographic_figure = all_brand_map_Flipkart(start_date, end_date)
        insights['demographic_plot'] = demographic_figure
        
        pie_chart = all_brand_pie_Flipkart(start_date, end_date)
        insights['pie_chart'] = pie_chart
        
        plot_figure = all_brand_dynamic_plot_Flipkart(start_date, end_date)
        insights['dynamic_plot'] = plot_figure

        print(f"Fetching of the general data is complete.........")
        
        return JsonResponse(insights)
    
    elif brand != "":

        print(f"brand case has been triggered!!!")

        models = brand_models[seller]
        insights = {}

        insights = get_fk_insights_multi_brand(
            models["sales"],
            models["ads"],
            models["invoices"],
            models["master_sku"],
            models["cogs"],
            models["returns"],
            brand,
            start_date,
            end_date
        )

        demographic_figure = demographic_plot_flipkart(
            models["sales"],
            brand,
            start_date,
            end_date
        )

        plot_figure = get_dynamic_plot_flipkart(
            models["sales"],
            models["ads"],
            brand,
            start_date,
            end_date,
            seller
        )

        pie_chart = pie_chart_flipkart(
            models["sales"],
            models["master_sku"],
            brand,
            start_date,
            end_date
        )

        insights['demographic_plot'] = demographic_figure
        insights['dynamic_plot'] = plot_figure
        insights['pie_chart'] = pie_chart

        print(f"Fetching of the general data is complete.........")

        return JsonResponse(insights)
    
    else:

        print(f"only seller case is triggered!!!")

        models = brand_models[seller]
        insights = {}

        insights = get_fk_insights(
            models["sales"],
            models["ads"],
            models["invoices"],
            models["master_sku"],
            models["cogs"],
            models["returns"],
            seller,
            start_date,
            end_date
        )

        # Why there is "brand" in the below three plots instead of "seller"?, check for that
        
        plot_figure = get_dynamic_plot_flipkart(
            models["sales"],
            models["ads"],
            brand,
            start_date,
            end_date,
            seller
        )

        demographic_figure = demographic_plot_flipkart(
            models["sales"],
            brand,
            start_date,
            end_date
        )

        pie_chart = pie_chart_flipkart(
            models["sales"],
            models["master_sku"],
            brand,
            start_date,
            end_date
        )

        # 8) Attach plot data to insights
        insights['dynamic_plot'] = plot_figure
        insights['demographic_plot'] = demographic_figure
        insights['pie_chart'] = pie_chart

        print(f"Fetching of the general data is complete.........")

        # 9) Return everything as JSON
        return JsonResponse(insights)



# This is for fetching the pnl details
@login_required(login_url='/backend/login/')
def flipkart_pnl_view(request):

    print(f"Flipkart PnL is loading......")

    start_date = request.GET.get('pnl_start_date')
    end_date = request.GET.get('pnl_end_date')
    time_format = request.GET.get('time_stamp')
    seller = request.GET.get('seller')
    brand = request.GET.get('brand')

    if start_date and end_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
    else:
        start_date = None
        end_date = None

    print(f"the start date in the pnl table is {start_date} and the end date is {end_date}")

    if brand != "":
        print(f"brand case is triggered!!!")
        pnl_details = Flipkart_PnL_calculator_multi_brand(start_date, end_date, time_format, seller, brand)
    
    else:
        print(f"all seller or only seller case is triggered!!!")
        pnl_details = Flipkart_PnL_calculator(start_date, end_date, time_format, seller)

    print(f"Fetching of the PnL data is complete......")

    return JsonResponse(pnl_details)


# Amazon Insights
@login_required(login_url='/backend/login/')
def amz_insights_view(request):

    print("amz_insights_view has been summoned")

    # 1) Read existing params
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    seller = request.GET.get('seller')
    brand = request.GET.get('brand')
    
    print(f"the seller is {seller}")
    print(f"the brand is {brand}")

    # 3) Convert string dates (start_date_str, end_date_str) to datetime
    if start_date_str and end_date_str:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
    else:
        start_date = None
        end_date = None

    print(f"Start date: {start_date} End date: {end_date}")
    
    # 5) Use your existing brand lookups
    brand_models = {
        "TRI": {
            "sales": First_step_SalesData_AMZ,
            "sb_ads": First_step_SB_Ads_AMZ,
            "sd_ads": First_step_SD_Ads_AMZ,
            "sp_ads": First_step_SP_Ads_AMZ,
            "codb_fees": First_step_CODBFeesData_AMZ,
            "master_sku": First_step_Master_SKU,
            "cogs": First_step_cogs_vertical,
            "returns": First_step_ReturnData_AMZ
        },
    }

    # if seller not in brand_models:
    #     return JsonResponse({"error": "Invalid brand selected"}, status=400)

    
    insights = {}

    if seller == "All Seller":
        print(f"all seller case is triggered!!!")
        
        insights = all_brand_AMZ(start_date, end_date)
        print(f"Checking the cards and table data {insights}")
        
        demographic_figure = all_brand_map_AMZ(start_date, end_date)
        insights['demographic_plot'] = demographic_figure
        
        pie_chart = all_brand_pie_AMZ(start_date, end_date)
        insights['pie_chart'] = pie_chart
        
        plot_figure = all_brand_dynamic_plot_AMZ(start_date, end_date)
        insights['dynamic_plot'] = plot_figure

        print(f"Fetching of the general data is complete.........")
        
        return JsonResponse(insights)

    
    else:
        models = brand_models[seller]

        insights = get_AMZ_insights(
            models["sales"],
            models["codb_fees"],
            models["sb_ads"],
            models["sd_ads"],
            models["sp_ads"],
            models["master_sku"],
            models["cogs"],
            models["returns"],
            brand,
            start_date,
            end_date
        )

        demographic_figure = demographic_plot_AMZ(
                models["sales"],
                brand,
                start_date,
                end_date
            )
        
        pie_chart = pie_chart_AMZ(
                models["sales"],
                models["master_sku"],
                brand,
                start_date,
                end_date
            )
        
        plot_figure = get_dynamic_plot_AMZ(
                models["sales"],
                models['sb_ads'],
                models['sd_ads'],
                models['sp_ads'],
                brand,
                start_date,
                end_date
            )
        
        insights['demographic_plot'] = demographic_figure
        insights['pie_chart'] = pie_chart
        insights['dynamic_plot'] = plot_figure

        print(f"Fetching of the general data is complete.........")


        return JsonResponse(insights)

# PnL Details of Amazon Platform
@login_required(login_url='/backend/login/')
def amz_pnl_view(request):

    print(f"Amazon PnL is loading......")

    start_date = request.GET.get('pnl_start_date')
    end_date = request.GET.get('pnl_end_date')
    time_format = request.GET.get('time_stamp')
    seller = request.GET.get('seller')
    brand = request.GET.get('brand')

    if start_date and end_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
    else:
        start_date = None
        end_date = None

    print(f"the start date in the pnl table is {start_date} and the end date is {end_date}")
    
    # print(f"all seller or only seller case is triggered!!!")
    pnl_details = Amazon_PnL_calculator(start_date, end_date, time_format, seller, brand)

    print(f"Fetching of the PnL data is complete......")

    return JsonResponse(pnl_details)



# D2C Insights
@login_required(login_url='/backend/login/')
def d2c_insights_view(request):
    
    insights = {}
    insights['message'] = 'D2C Insights coming soon!'
    return JsonResponse(insights)



# Meesho Insights
@login_required(login_url='/backend/login/')
def meesho_insights_view(request):
    
    insights = {}
    insights['message'] = 'Meesho Insights coming soon!'
    return JsonResponse(insights)



# Jiomart Insights
@login_required(login_url='/backend/login/')
def jiomart_insights_view(request):
    
    insights = {}
    insights['message'] = 'JioMart Insights coming soon!'
    return JsonResponse(insights)

    