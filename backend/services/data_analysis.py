'''
This file is for defining the logic to do the analysis on the uploaded data
'''

# first import the required database
from backend.models import (First_step_AdsData_FK, First_step_InvoiceData_FK, First_step_SalesData_FK, First_step_FK_Return_data,
                            First_step_cogs_vertical, First_step_Master_SKU, First_step_CODBFeesData_AMZ, First_step_SalesData_AMZ,
                            First_step_SB_Ads_AMZ, First_step_SD_Ads_AMZ, First_step_SP_Ads_AMZ,
                            Jr_Sr_AdsData_FK_MP, Jr_Sr_cogs, Jr_Sr_cogs_master_sku, Jr_Sr_InvoiceData_FK, Jr_Sr_SalesData_FK, Jr_Sr_FK_Return_data,
                            NexTen_AdsData_FK_MP, NexTen_COGS_Master_SKU, NexTen_InvoiceData_FK, NexTen_SalesData_FK, NexTen_Return_data)

from django.db.models import OuterRef, Subquery, F, Value, DecimalField, CharField, DateField
from django.db.models.functions import Coalesce, TruncDate, Abs, Cast, ExtractMonth
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from django.db.models import Q, Sum, F, FloatField, ExpressionWrapper, Count, Case, When, Value, Prefetch
import matplotlib.pyplot as plt
import pandas as pd
import base64
from django.http import JsonResponse
from io import BytesIO
from matplotlib.ticker import FuncFormatter
import plotly.graph_objects as go
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from datetime import date 
import json
import plotly.express as px
import geopandas as gpd
from decimal import Decimal
from django.contrib.postgres.aggregates import ArrayAgg


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


amazon_brand_models = {
    "TRI": {
        "sales": First_step_SalesData_AMZ,
        "sb_ads": First_step_SB_Ads_AMZ,
        "sd_ads": First_step_SD_Ads_AMZ,
        "sp_ads": First_step_SP_Ads_AMZ,
        "codb_fees": First_step_CODBFeesData_AMZ,
        "master_sku": First_step_Master_SKU,
        "cogs": First_step_cogs_vertical
    }
}





'''
1. aggregate(total_gmv=Sum(Abs(F('invoice_amount')))) computes the sum of absolute values of invoice_amount and assigns it the key total_gmv.
2. The aggregate function returns a dictionary like: {'total_gmv': <calculated_value>}.
3. ['total_gmv'] extracts the calculated value from the dictionary, which is then assigned to the gmv variable.


filter(invoice_amount__gt=0): This filters the rows to include only those where invoice_amount is greater than 0.
if you put "invoice__gt=1", this will include only those rows that are greater than 1.
if you put "invoice__lt=0", this will include only those rows that are less than 0.
'''

def demo_function(sales_data_model, return_data_model, start_date=None, end_date=None):
    
    sales_order_item_ids = sales_data_model.objects.filter(
            event_sub_type="Sale",
            order_date__range=[start_date, end_date]
        ).values_list('order_item_id', flat=True)
    
    extended_date = end_date + timedelta(days=45)

    return_order_item_ids = sales_data_model.objects.filter(
            order_item_id__in=sales_order_item_ids,
            event_sub_type="Return",
            order_date__range=[start_date, extended_date]
        ).values_list('order_item_id', flat=True)
    
    print("length of sales ", len(sales_order_item_ids))
    print("length of return ", len(return_order_item_ids))
    

    return_classification_subquery = return_data_model.objects.filter(
        order_item_id=OuterRef('order_item_id')
    ).annotate(
        classified_return=Case(
            When(return_type='courier_return', then=Value('courier_return')),
            When(return_type='customer_return', then=Value('customer_return')),
            default=Value('miscellaneous returns'),
            output_field=CharField(),
        )
    ).values('classified_return')[:1]

    sales_returns = sales_data_model.objects.filter(
        order_item_id__in=return_order_item_ids,
        event_sub_type="Return"
    ).annotate(
        classified_return=Coalesce(
            Subquery(return_classification_subquery),
            Value('miscellaneous returns')
        )
    )

    # 4. Group by classification and sum up the quantity column
    result = sales_returns.values('classified_return').annotate(total_quantity=Sum('item_quantity'))
    courier_return = result[0]['total_quantity'] if result[0]['classified_return'] == 'courier_return' else 0
    customer_return = result[1]['total_quantity'] if result[1]['classified_return'] == 'customer_return' else 0
    miscellaneous_returns = result[2]['total_quantity'] if result[2]['classified_return'] == 'miscellaneous returns' else 0

    print(f"courier return: {courier_return}")
    print(f"customer return: {customer_return}")
    print(f"miscellaneous return: {miscellaneous_returns}")

    # Example: Print the results
    # for entry in result:
    #     print(f"{entry['classified_return']}: {entry['total_quantity']}")


    display_return_qty = sales_data_model.objects.filter(order_item_id__in=return_order_item_ids, order_date__range=[start_date, extended_date], event_sub_type="Return").aggregate(return_qty=Sum(F('item_quantity')))['return_qty'] or 0
    print(f"Total return quantity: {display_return_qty}")

    

def demo_AMZ(sales_data_model, return_data_model, start_date, end_date):

    data_model = sales_data_model.objects.filter(invoice_date__range=[start_date, end_date])
    start_date_i = start_date
    end_date_i = end_date

    extended_date = end_date + timedelta(days=45)

    sales_order_ids = data_model.filter(
        transaction_type="Shipment",
        invoice_date__range=[start_date_i, end_date_i]
    ).values_list('order_id', flat=True)

    return_order_ids = data_model.filter(
        order_id__in=sales_order_ids,
        transaction_type="Refund",
        invoice_date__range=[start_date_i, extended_date]
    ).values_list('order_id', flat=True)

        # Till here the code is fine for the simple and multi-brand account

        # Not applying the brand filter because the "Return Data" is very small so searching in the entire return data
    return_classification = return_data_model.objects.filter(
            order_id__in=OuterRef('order_id')
        ).annotate(
            classified_return=Case(
                When(return_type='Amazon CS', then=Value('courier_return')),
                When(return_type='C-Returns', then=Value('customer_return')),
                When(return_type='Rejected', then=Value('courier_return')),
                When(return_type='Undelivered', then=Value('courier_return')),
                default=Value('miscellaneous returns'),
                output_field=CharField(),
            )
        ).values('classified_return')

    return_quantity_subquery = return_data_model.objects.filter(
        order_id=OuterRef('order_id')
    ).values('order_id').annotate(
        total_return_qty=Sum('return_quantity'),
    ).values('total_return_qty')[:1]

    # 3. Use both in your main query
    sales_returns = sales_data_model.objects.filter(
        order_date__range=[start_date, extended_date],
        order_id__in=return_order_ids,
        transaction_type="Refund"
    ).annotate(
        classified_return=Coalesce(
            Subquery(return_classification),
            Value('miscellaneous returns')
        ),
        return_quantity=Coalesce(
            Subquery(return_quantity_subquery),
            Value(0),
            output_field=DecimalField()
        )
    )

    # 4. Final aggregation by classified_return
    return_result = sales_returns.values('classified_return').annotate(
        total_quantity=Sum('return_quantity')
    )
            
    print(f"return results {return_result}")

        # Build a dictionary mapping classification to its total quantity.
    return_totals = {entry['classified_return']: entry['total_quantity'] for entry in return_result}

        # Get each total; if missing, default to 0.
    courier_return = return_totals.get('courier_return', 0)
    customer_return = return_totals.get('customer_return', 0)
    miscellaneous_return = return_totals.get('miscellaneous returns', 0)   

        # print(f"Actual return qty: {display_return_qty}")
    print(f"start_date {start_date} and end_date {end_date}")
    print(f"courier return: {courier_return}")
    print(f"customer return: {customer_return}")
    print(f"miscellaneous return: {miscellaneous_return}")






# Call this function two-times one for the current date and one for the previous date, use undersore for the unused variable
def Flipkart_sales_parameters(sales_data_model, return_data_model, start_date=None, end_date=None):
    
    current_par = []
    prev_par = []
    percent_change = []

    for i in range(2):

        if i == 0:

            start_date_i = start_date
            end_date_i = end_date

            data_model = sales_data_model.objects.filter(order_date__range=[start_date_i, end_date_i])
            extended_date = end_date_i + timedelta(days=45)

        else:

            delta = end_date_i - start_date_i
            end_date_i = start_date_i - timedelta(days=1)
            start_date_i = end_date_i - delta

            data_model = sales_data_model.objects.filter(order_date__range=[start_date_i, end_date_i])
            extended_date = end_date_i + timedelta(days=45)

        # Now Gross GMV and Quantity is not considering the "Return Cancellation"
        display_gmv = data_model.filter(Q(event_sub_type='Sale')).aggregate(gmv=Sum(F('final_invoice_amount')))['gmv'] or 0
        display_qty = data_model.filter(Q(event_sub_type='Sale')).aggregate(qty=Sum(F('item_quantity')))['qty'] or 0
        
        return_cancellation_qty = sales_data_model.objects.filter(order_date__range=[start_date_i, end_date_i], event_sub_type="Return Cancellation").aggregate(return_cancellation_qty=Sum(F('item_quantity')))['return_cancellation_qty'] or 0
        return_cancellation_qmv = sales_data_model.objects.filter(order_date__range=[start_date_i, end_date_i], event_sub_type="Return Cancellation").aggregate(return_cancellation_qmv=Sum(F('final_invoice_amount')))['return_cancellation_qmv'] or 0



        # print(f"Start date {start_date_i} and end date: {end_date_i}")

        sales_order_item_ids = sales_data_model.objects.filter(
            event_sub_type="Sale",
            order_date__range=[start_date_i, end_date_i]
        ).values_list('order_item_id', flat=True).distinct()


        # print(f"length of unique sales order item id: {len(sales_order_item_ids)}")

        return_order_item_ids = sales_data_model.objects.filter(
            order_item_id__in=sales_order_item_ids,
            event_sub_type="Return",
            order_date__range=[start_date_i, extended_date]
        ).values_list('order_item_id', flat=True).distinct()


        # print(f"length of unique return order item id: {len(return_order_item_ids)}")

        # print(f"The no. of Return Order Item IDs: {len(return_order_item_ids)}")

        cancellation_ids = sales_data_model.objects.filter(order_item_id__in=sales_order_item_ids, order_date__range=[start_date_i, extended_date], event_sub_type="Cancellation").values_list('order_item_id', flat=True)

        display_return_rev = sales_data_model.objects.filter(order_item_id__in=return_order_item_ids, order_date__range=[start_date_i, extended_date], event_sub_type="Return").aggregate(return_rev=Sum(F('final_invoice_amount')))['return_rev'] or 0
        display_return_qty = sales_data_model.objects.filter(order_item_id__in=return_order_item_ids, order_date__range=[start_date_i, extended_date], event_sub_type="Return").aggregate(return_qty=Sum(F('item_quantity')))['return_qty'] or 0
        

        # 1. Subquery to classify the return type
        return_classification_subquery = return_data_model.objects.filter(
            order_item_id=OuterRef('order_item_id')
        ).annotate(
            classified_return=Case(
                When(return_type='courier_return', then=Value('courier_return')),
                When(return_type='customer_return', then=Value('customer_return')),
                default=Value('miscellaneous returns'),
                output_field=CharField(),
            )
        ).values('classified_return')[:1]

        # 2. Subquery to get total return_quantity for each order_item_id
        return_quantity_subquery = return_data_model.objects.filter(
            order_item_id=OuterRef('order_item_id')
        ).values('order_item_id').annotate(
            total_return_qty=Sum('quantity'),
        ).values('total_return_qty')[:1]

        # 3. Use both in your main query
        sales_returns = sales_data_model.objects.filter(
            order_date__range=[start_date_i, extended_date],
            order_item_id__in=return_order_item_ids,
            event_sub_type="Return"
        ).annotate(
            classified_return=Coalesce(
                Subquery(return_classification_subquery),
                Value('miscellaneous returns')
            ),
            return_quantity=Coalesce(
                Subquery(return_quantity_subquery),
                Value(0),
                output_field=DecimalField()
            )
        )

        # 4. Final aggregation by classified_return
        return_result = sales_returns.values('classified_return').annotate(
            total_quantity=Sum('return_quantity')
        )
        
        # print(f"return results {return_result}")

        # Build a dictionary mapping classification to its total quantity.
        return_totals = {entry['classified_return']: entry['total_quantity'] for entry in return_result}

        # Get each total; if missing, default to 0.
        courier_return = return_totals.get('courier_return', 0)
        customer_return = return_totals.get('customer_return', 0)
        miscellaneous_return = return_totals.get('miscellaneous returns', 0)   

        # print(f"Actual return qty: {display_return_qty}")
        # print(f"start_date {start_date_i} and end_date {end_date_i}")
        # print(f"courier return: {courier_return}")
        # print(f"customer return: {customer_return}")
        # print(f"miscellaneous return: {miscellaneous_return}")

        display_cancellation_qty = sales_data_model.objects.filter(order_item_id__in=cancellation_ids, order_date__range=[start_date, extended_date], event_sub_type="Cancellation").aggregate(cancellation_qty=Sum(F('item_quantity')))['cancellation_qty'] or 0
        display_cancellation_rev = sales_data_model.objects.filter(order_item_id__in=cancellation_ids, order_date__range=[start_date, extended_date], event_sub_type="Cancellation").aggregate(cancellation_rev=Sum(F('final_invoice_amount')))['cancellation_rev'] or 0
        

        # Calculate percentages.
        rto_percent = 0 if (display_qty == 0 and miscellaneous_return == 0) else round(courier_return * 100/(display_qty - miscellaneous_return), 2)
        rtv_percent = 0 if (display_qty == 0 and display_cancellation_qty == 0 and courier_return == 0) else round((customer_return - return_cancellation_qty) * 100/(display_qty - display_cancellation_qty - courier_return), 2)
        miscellaneous_return_percent = 0 if display_qty == 0 else round(miscellaneous_return * 100 / display_qty, 2)


        display_net_gmv = display_gmv - display_return_rev - display_cancellation_rev
        display_net_qty = display_qty - display_return_qty - display_cancellation_qty

        # Calculating Sale's contribution from Shopsy
        shopsy_gmv = data_model.filter(Q(is_shopsy_order="True") & (Q(event_sub_type='Sale') | Q(event_sub_type='Return Cancellation'))).aggregate(shopsy_gmv=Sum(F('final_invoice_amount')))['shopsy_gmv'] or 0
        shopsy_return_rev = sales_data_model.objects.filter(Q(is_shopsy_order="True") & Q(event_sub_type='Return'), order_item_id__in=return_order_item_ids).aggregate(shopsy_return_rev=Sum(F('final_invoice_amount')))['shopsy_return_rev'] or 0
        shopsy_cancellation_rev = sales_data_model.objects.filter(Q(is_shopsy_order="True") & Q(event_sub_type='Cancellation'), order_item_id__in=cancellation_ids).aggregate(shopsy_cancellation_rev=Sum(F('final_invoice_amount')))['shopsy_cancellation_rev'] or 0
        shopsy_net_gmv = shopsy_gmv - shopsy_return_rev - shopsy_cancellation_rev
        
        display_shopsy_contribution = 0 if display_net_gmv == 0 else round(shopsy_net_gmv*100/display_net_gmv, 2)

        # Calculating Sale's contribution from FBF (fulfillment by Flipkart)
        fbf_gmv = data_model.filter(Q(fulfilment_type="FBF") & (Q(event_sub_type='Sale') | Q(event_sub_type='Return Cancellation'))).aggregate(fbf_gmv=Sum(F('final_invoice_amount')))['fbf_gmv'] or 0
        fbf_return_rev = sales_data_model.objects.filter(Q(fulfilment_type="FBF") & Q(event_sub_type='Return'), order_item_id__in=return_order_item_ids).aggregate(fbf_return_rev=Sum(F('final_invoice_amount')))['fbf_return_rev'] or 0
        fbf_cancellation_rev = sales_data_model.objects.filter(Q(fulfilment_type="FBF") & Q(event_sub_type='Cancellation'), order_item_id__in=cancellation_ids).aggregate(fbf_cancellation_rev=Sum(F('final_invoice_amount')))['fbf_cancellation_rev'] or 0
        fbf_net_gmv = fbf_gmv - fbf_return_rev - fbf_cancellation_rev

        display_fbf_contribution = 0 if display_net_gmv == 0 else round(fbf_net_gmv*100/display_net_gmv, 2)

        if i == 0: current_par.extend([display_gmv, display_qty, display_return_rev, display_return_qty, display_cancellation_rev, display_cancellation_qty, display_net_gmv, display_net_qty, display_shopsy_contribution, display_fbf_contribution, rto_percent, rtv_percent, miscellaneous_return_percent, courier_return, customer_return, miscellaneous_return])
        else: prev_par.extend([display_gmv, display_qty, display_return_rev, display_return_qty, display_cancellation_rev, display_cancellation_qty, display_net_gmv, display_net_qty, display_shopsy_contribution, display_fbf_contribution, rto_percent, rtv_percent, miscellaneous_return_percent, courier_return, customer_return, miscellaneous_return])

    # calculating the percentage change
    for i, j in zip(current_par, prev_par):
        percentage_change = 0 if j == 0 else (i - j)*100/j
        percent_change.append(percentage_change)

    # For PnL calculation and display in the PnL table
    data_model = sales_data_model.objects.filter(order_date__range=[start_date, end_date])

    # Not considering the "Return Cancellation" in the GMV and Quantity
    gmv = data_model.filter(Q(event_sub_type='Sale')).aggregate(gmv=Sum(F('final_invoice_amount')))['gmv'] or 0
    qty = data_model.filter(Q(event_sub_type='Sale')).aggregate(qty=Sum(F('item_quantity')))['qty'] or 0


    # this tracks all the returns and cancellation that were came in that date range  basically its the summary of the sales tax report (irrespective of the order date)
    return_rev = data_model.filter(event_sub_type='Return').aggregate(return_rev=Sum(F('final_invoice_amount')))['return_rev'] or 0
    return_qty = data_model.filter(event_sub_type='Return').aggregate(return_qty=Sum(F('item_quantity')))['return_qty'] or 0

    cancellation_qty = data_model.filter(event_sub_type='Cancellation').aggregate(cancellation_qty=Sum(F('item_quantity')))['cancellation_qty'] or 0
    cancellation_rev = data_model.filter(event_sub_type='Cancellation').aggregate(cancellation_rev=Sum(F('final_invoice_amount')))['cancellation_rev'] or 0

    bank_discount_sales = data_model.filter(Q(event_sub_type='Sale') | Q(event_sub_type='Return Cancellation')).aggregate(sale_dis=Sum(F('bank_offer_share')))['sale_dis'] or 0
    bank_discount_return = data_model.filter(event_sub_type='Return').aggregate(return_dis=Sum(F('bank_offer_share')))['return_dis'] or 0
    bank_discount_cancellation = data_model.filter(event_sub_type='Cancellation').aggregate(cancellation_dis=Sum(F('bank_offer_share')))['cancellation_dis'] or 0

    total_bank_dis = -(bank_discount_sales - bank_discount_cancellation - bank_discount_return)

    net_gmv = gmv - return_rev - cancellation_rev
    net_qty = qty - return_qty - cancellation_qty

    net_gmv_without_tax = data_model.aggregate(net_gmv_wtax=Sum(F('taxable_value')))['net_gmv_wtax'] or 0

    tax = net_gmv - net_gmv_without_tax


    return (current_par[0], current_par[1], current_par[2], current_par[3], current_par[4], current_par[5], current_par[6], current_par[7], current_par[8], current_par[9], current_par[10], current_par[11], current_par[12], current_par[13], current_par[14], current_par[15],
            percent_change[0], percent_change[1], percent_change[2], percent_change[3], percent_change[4], percent_change[5], percent_change[6], percent_change[7], percent_change[8], percent_change[9], gmv,
            qty, return_rev, return_qty, cancellation_rev, cancellation_qty, net_gmv, net_qty, net_gmv_without_tax, tax, total_bank_dis, prev_par[6])



"""-------------------------Sales Parameter for multi-brand account like NexTen Brands------------------------------------"""

def Flipkart_multi_brand_sales(sales_data_model, return_data_model, brand, start_date=None, end_date=None):

    current_par = []
    prev_par = []
    percent_change = []

    for i in range(2):

        if i == 0:

            start_date_i = start_date
            end_date_i = end_date

            data_model = sales_data_model.objects.filter(order_date__range=[start_date_i, end_date_i], product_title__icontains=brand.lower())
            extended_date = end_date + timedelta(days=45)

        else:

            delta = end_date_i - start_date_i
            end_date_i = start_date_i - timedelta(days=1)
            start_date_i = end_date_i - delta
            data_model = sales_data_model.objects.filter(order_date__range=[start_date_i, end_date_i], product_title__icontains=brand.lower())
            extended_date = end_date_i + timedelta(days=45)

            # This is for the display in cards
        display_gmv = data_model.filter(Q(event_sub_type='Sale')).aggregate(gmv=Sum(F('final_invoice_amount')))['gmv'] or 0
        display_qty = data_model.filter(Q(event_sub_type='Sale')).aggregate(qty=Sum(F('item_quantity')))['qty'] or 0
        
        return_cancellation_qty = sales_data_model.objects.filter(order_date__range=[start_date_i, end_date_i], event_sub_type="Return Cancellation").aggregate(return_cancellation_qty=Sum(F('item_quantity')))['return_cancellation_qty'] or 0
        return_cancellation_qmv = sales_data_model.objects.filter(order_date__range=[start_date_i, end_date_i], event_sub_type="Return Cancellation").aggregate(return_cancellation_qmv=Sum(F('final_invoice_amount')))['return_cancellation_qmv'] or 0

        # this tracks only those returns which came from the orders that were made in that date range
        sales_order_item_ids = sales_data_model.objects.filter(
            event_sub_type="Sale", product_title__icontains=brand.lower(),
            order_date__range=[start_date, end_date]
        ).values_list('order_item_id', flat=True).distinct()

        # here we need to consider order_item_id instead of order_id because the return and cancellation are made on the item level and return report is also on the item level
        return_order_item_ids = sales_data_model.objects.filter(
            order_item_id__in=sales_order_item_ids,
            event_sub_type="Return",
            order_date__range=[start_date, extended_date]
        ).values_list('order_item_id', flat=True).distinct()

        cancellation_ids = sales_data_model.objects.filter(order_item_id__in=sales_order_item_ids, order_date__range=[start_date, extended_date], event_sub_type="Cancellation").values_list('order_item_id', flat=True)

        display_return_rev = sales_data_model.objects.filter(order_item_id__in=return_order_item_ids, order_date__range=[start_date, extended_date], event_sub_type="Return").aggregate(return_rev=Sum(F('final_invoice_amount')))['return_rev'] or 0
        display_return_qty = sales_data_model.objects.filter(order_item_id__in=return_order_item_ids, order_date__range=[start_date, extended_date], event_sub_type="Return").aggregate(return_qty=Sum(F('item_quantity')))['return_qty'] or 0
        
        # Here we are finding the RTO, RTV and Miscellaneous return percentage
        return_classification_subquery = return_data_model.objects.filter(
            order_item_id=OuterRef('order_item_id')
        ).annotate(
            classified_return=Case(
                When(return_type='courier_return', then=Value('courier_return')),
                When(return_type='customer_return', then=Value('customer_return')),
                default=Value('miscellaneous returns'),
                output_field=CharField(),
            )
        ).values('classified_return')[:1]

        sales_returns = sales_data_model.objects.filter(
            order_item_id__in=return_order_item_ids,
            event_sub_type="Return"
        ).annotate(
            classified_return=Coalesce(
                Subquery(return_classification_subquery),
                Value('miscellaneous returns')
            )
        )

        display_cancellation_qty = sales_data_model.objects.filter(order_item_id__in=cancellation_ids, order_date__range=[start_date, extended_date], event_sub_type="Cancellation").aggregate(cancellation_qty=Sum(F('item_quantity')))['cancellation_qty'] or 0
        display_cancellation_rev = sales_data_model.objects.filter(order_item_id__in=cancellation_ids, order_date__range=[start_date, extended_date], event_sub_type="Cancellation").aggregate(cancellation_rev=Sum(F('final_invoice_amount')))['cancellation_rev'] or 0

        return_result = sales_returns.values('classified_return').annotate(total_quantity=Sum('item_quantity'))

        # Build a dictionary mapping classification to its total quantity.
        return_totals = {entry['classified_return']: entry['total_quantity'] for entry in return_result}

        # Get each total; if missing, default to 0.
        courier_return = return_totals.get('courier_return', 0)
        customer_return = return_totals.get('customer_return', 0)
        miscellaneous_return = return_totals.get('miscellaneous returns', 0)

        # Calculate percentages.
        rto_percent = 0 if (display_qty == 0 and miscellaneous_return == 0) else round(courier_return * 100/(display_qty - miscellaneous_return), 2)
        rtv_percent = 0 if (display_qty == 0 and display_cancellation_qty == 0 and courier_return == 0) else round((customer_return - return_cancellation_qty) * 100/(display_qty - display_cancellation_qty - courier_return), 2)
        miscellaneous_return_percent = 0 if display_qty == 0 else round(miscellaneous_return * 100 / display_qty, 2)

        # rto_percent = 0 if display_qty == 0 else round(courier_total * 100 / display_qty, 2)
        # rtv_percent = 0 if display_qty == 0 else round(customer_total * 100 / display_qty, 2)
        # miscellaneous_return_percent = 0 if display_qty == 0 else round(miscellaneous_total * 100 / display_qty, 2)


        display_net_gmv = display_gmv - display_return_rev - display_cancellation_rev
        display_net_qty = display_qty - display_return_qty - display_cancellation_qty
        
        # This is showing the contribution of Shopsy in the sales
        shopsy_gmv = data_model.filter(Q(is_shopsy_order="True") & (Q(event_sub_type='Sale') | Q(event_sub_type='Return Cancellation'))).aggregate(shopsy_gmv=Sum(F('final_invoice_amount')))['shopsy_gmv'] or 0
        shopsy_return_rev = sales_data_model.objects.filter(Q(is_shopsy_order="True") & Q(event_sub_type='Return'), order_item_id__in=return_order_item_ids).aggregate(shopsy_return_rev=Sum(F('final_invoice_amount')))['shopsy_return_rev'] or 0
        shopsy_cancellation_rev = sales_data_model.objects.filter(Q(is_shopsy_order="True") & Q(event_sub_type='Cancellation'), order_item_id__in=cancellation_ids).aggregate(shopsy_cancellation_rev=Sum(F('final_invoice_amount')))['shopsy_cancellation_rev'] or 0
        shopsy_net_gmv = shopsy_gmv - shopsy_return_rev - shopsy_cancellation_rev

        display_shopsy_contribution = 0 if display_net_gmv == 0 else round(shopsy_net_gmv*100/display_net_gmv, 2)

        # Calculating Sale's contribution from FBF (fulfillment by Flipkart)
        fbf_gmv = data_model.filter(Q(fulfilment_type="FBF") & (Q(event_sub_type='Sale') | Q(event_sub_type='Return Cancellation'))).aggregate(fbf_gmv=Sum(F('final_invoice_amount')))['fbf_gmv'] or 0
        fbf_return_rev = sales_data_model.objects.filter(Q(fulfilment_type="FBF") & Q(event_sub_type='Return'), order_item_id__in=return_order_item_ids).aggregate(fbf_return_rev=Sum(F('final_invoice_amount')))['fbf_return_rev'] or 0
        fbf_cancellation_rev = sales_data_model.objects.filter(Q(fulfilment_type="FBF") & Q(event_sub_type='Cancellation'), order_item_id__in=cancellation_ids).aggregate(fbf_cancellation_rev=Sum(F('final_invoice_amount')))['fbf_cancellation_rev'] or 0
        fbf_net_gmv = fbf_gmv - fbf_return_rev - fbf_cancellation_rev

        display_fbf_contribution = 0 if display_net_gmv == 0 else round(fbf_net_gmv*100/display_net_gmv, 2)



        if i == 0: current_par.extend([display_gmv, display_qty, display_return_rev, display_return_qty, display_cancellation_rev, display_cancellation_qty, display_net_gmv, display_net_qty, display_shopsy_contribution, display_fbf_contribution, rto_percent, rtv_percent, miscellaneous_return_percent, courier_return, customer_return, miscellaneous_return])
        else: prev_par.extend([display_gmv, display_qty, display_return_rev, display_return_qty, display_cancellation_qty, display_cancellation_rev, display_net_gmv, display_net_qty, display_shopsy_contribution, display_fbf_contribution, rto_percent, rtv_percent, miscellaneous_return_percent, courier_return, customer_return, miscellaneous_return])

    # calculating the percentage change
    for i, j in zip(current_par, prev_par):
        percentage_change = 0 if j == 0 else (i - j)*100/j
        percent_change.append(percentage_change)

    # For PnL calculation and display in the PnL table
    data_model = sales_data_model.objects.filter(order_date__range=[start_date, end_date], product_title__icontains=brand.lower())

    gmv = data_model.filter(Q(event_sub_type='Sale')).aggregate(gmv=Sum(F('final_invoice_amount')))['gmv'] or 0
    qty = data_model.filter(Q(event_sub_type='Sale')).aggregate(qty=Sum(F('item_quantity')))['qty'] or 0


    # this tracks all the returns and cancellation that were came in that date range  basically its the summary of the sales tax report (irrespective of the order date)
    return_rev = data_model.filter(event_sub_type='Return').aggregate(return_rev=Sum(F('final_invoice_amount')))['return_rev'] or 0
    return_qty = data_model.filter(event_sub_type='Return').aggregate(return_qty=Sum(F('item_quantity')))['return_qty'] or 0

    cancellation_qty = data_model.filter(event_sub_type='Cancellation').aggregate(cancellation_qty=Sum(F('item_quantity')))['cancellation_qty'] or 0
    cancellation_rev = data_model.filter(event_sub_type='Cancellation').aggregate(cancellation_rev=Sum(F('final_invoice_amount')))['cancellation_rev'] or 0

    bank_discount_sales = data_model.filter(Q(event_sub_type='Sale') | Q(event_sub_type='Return Cancellation')).aggregate(sale_dis=Sum(F('bank_offer_share')))['sale_dis'] or 0
    bank_discount_return = data_model.filter(event_sub_type='Return').aggregate(return_dis=Sum(F('bank_offer_share')))['return_dis'] or 0
    bank_discount_cancellation = data_model.filter(event_sub_type='Cancellation').aggregate(cancellation_dis=Sum(F('bank_offer_share')))['cancellation_dis'] or 0

    total_bank_dis = -(bank_discount_sales - bank_discount_cancellation - bank_discount_return)

    net_gmv = gmv - return_rev - cancellation_rev
    net_qty = qty - return_qty - cancellation_qty

    net_gmv_without_tax = data_model.aggregate(net_gmv_wtax=Sum(F('taxable_value')))['net_gmv_wtax'] or 0

    tax = net_gmv - net_gmv_without_tax


    return (current_par[0], current_par[1], current_par[2], current_par[3], current_par[4], current_par[5], current_par[6], current_par[7], current_par[8], current_par[9], current_par[10], current_par[11], current_par[12], current_par[13], current_par[14], current_par[15],            percent_change[0], percent_change[1], percent_change[2], percent_change[3], percent_change[4], percent_change[5], percent_change[6], percent_change[7], percent_change[8], percent_change[9], gmv,
            qty, return_rev, return_qty, cancellation_rev, cancellation_qty, net_gmv, net_qty, net_gmv_without_tax, tax, total_bank_dis, prev_par[6])



# Call this function two-times one for the current date and one for the previous date, use undersore for the unused variable
def Flipkart_ads_parameters(ads_data_model, start_date=None, end_date=None):

    current_par = []
    prev_par = []
    percent_change = []

    for i in range(2):

        if i == 0:

            start_date_i = start_date
            end_date_i = end_date

            data_model = ads_data_model.objects.filter(date__range=[start_date_i, end_date_i])

        else:
            delta = end_date_i - start_date_i
            end_date_i = start_date_i - timedelta(days=1)
            start_date_i = end_date_i - delta

            data_model = ads_data_model.objects.filter(date__range=[start_date_i, end_date_i])

        display_ads_spend = data_model.aggregate(total_spend=Sum(F('ad_spend')))['total_spend'] or 0
        views = data_model.aggregate(total_views=Sum(F('views')))['total_views'] or 0
        clicks = data_model.aggregate(total_clicks=Sum(F('clicks')))['total_clicks'] or 0

        units_sold_direct = data_model.aggregate(total_units_sold_direct=Sum(F('units_sold_direct')))['total_units_sold_direct'] or 0
        units_sold_indirect = data_model.aggregate(total_units_sold_indirect=Sum(F('units_sold_indirect')))['total_units_sold_indirect'] or 0
        total_units_sold = units_sold_direct + units_sold_indirect

        direct_revenue = data_model.aggregate(total_direct_revenue=Sum(F('direct_revenue')))['total_direct_revenue'] or 0
        indirect_revenue = data_model.aggregate(total_indirect_revenue=Sum(F('indirect_revenue')))['total_indirect_revenue'] or 0
        total_revenue = direct_revenue + indirect_revenue

        display_ctr = 0 if views == 0 else clicks/views
        display_cpc = 0 if clicks == 0 else display_ads_spend/clicks
        display_cvr = 0 if clicks == 0 else total_units_sold/clicks
        display_roi = 0 if display_ads_spend == 0 else total_revenue/display_ads_spend

        if i == 0: current_par.extend([display_ads_spend, views, clicks, total_units_sold, total_revenue, display_ctr, display_cpc, display_cvr, display_roi])
        else: prev_par.extend([display_ads_spend, views, clicks, total_units_sold, total_revenue, display_ctr, display_cpc, display_cvr, display_roi])

    for i, j in zip(current_par, prev_par):
        percentage_change = 0 if j == 0 else (i - j)*100/j
        percent_change.append(percentage_change)

    return (current_par[0], current_par[5], current_par[6], current_par[7], current_par[8], percent_change[0], percent_change[5], 
            percent_change[6], percent_change[7], percent_change[8], prev_par[0])




# Call this function two-times one for the current date and one for the previous date, use undersore for the unused variable
def Flipkart_MP_ads_parameters(ads_data_model, start_date, end_date):

    current_par = []
    prev_par = []
    percent_change = []

    for i in range(2):

        if i == 0:
            start_date_i = start_date
            end_date_i = end_date

            data_model = ads_data_model.objects.filter(date__range=[start_date_i, end_date_i])
        
        else:
            delta = end_date_i - start_date_i
            end_date_i = start_date_i - timedelta(days=1)
            start_date_i = end_date_i - delta

            data_model = ads_data_model.objects.filter(date__range=[start_date_i, end_date_i])

        display_ads_spend = data_model.aggregate(total_spend=Sum(F('ad_spend')))['total_spend'] or 0
        views = data_model.aggregate(total_views=Sum(F('views')))['total_views'] or 0
        clicks = data_model.aggregate(total_clicks=Sum(F('clicks')))['total_clicks'] or 0
        units = data_model.aggregate(total_units=Sum(F('total_converted_units')))['total_units'] or 0
        revenue = data_model.aggregate(total_revenue=Sum(F('total_revenue')))['total_revenue'] or 0

        display_ctr = 0 if views == 0 else clicks/views
        display_cpc = 0 if clicks == 0 else display_ads_spend/clicks
        display_cvr = 0 if clicks == 0 else units/clicks
        display_roi = 0 if display_ads_spend == 0 else revenue/display_ads_spend

        if i == 0: current_par.extend([display_ads_spend, views, clicks, units, revenue, display_ctr, display_cpc, display_cvr, display_roi])
        else: prev_par.extend([display_ads_spend, views, clicks, units, revenue, display_ctr, display_cpc, display_cvr, display_roi])

    for i, j in zip(current_par, prev_par):
        percentage_change = 0 if j == 0 else (j - i)*100/j
        percent_change.append(percentage_change)

    return (current_par[0], current_par[5], current_par[6], current_par[7], current_par[8], percent_change[0], percent_change[5], 
            percent_change[6], percent_change[7], percent_change[8], prev_par[0])            
        


"""------------------------------------Flipkart MP multi-brand account Ads parameters----------------------------------------"""

def Flipkart_MP_ads_multi_brand(ads_data_model, brand, start_date, end_date):

    current_par = []
    prev_par = []
    percent_change = []

    for i in range(2):

        if i == 0:
            start_date_i = start_date
            end_date_i = end_date

            data_model = ads_data_model.objects.filter(date__range=[start_date_i, end_date_i])

        else:

            delta = end_date_i - start_date_i
            end_date_i = start_date_i - timedelta(days=1)
            start_date_i = end_date_i - delta

            data_model = ads_data_model.objects.filter(date__range=[start_date_i, end_date_i])

        display_ads_spend = data_model.filter(campaign_name__icontains=brand.lower()).aggregate(total_spend=Sum(F('ad_spend')))['total_spend'] or 0
        views = data_model.filter(campaign_name__icontains=brand.lower()).aggregate(total_views=Sum(F('views')))['total_views'] or 0
        clicks = data_model.filter(campaign_name__icontains=brand.lower()).aggregate(total_clicks=Sum(F('clicks')))['total_clicks'] or 0
        units = data_model.filter(campaign_name__icontains=brand.lower()).aggregate(total_units=Sum(F('total_converted_units')))['total_units'] or 0
        revenue = data_model.filter(campaign_name__icontains=brand.lower()).aggregate(total_revenue=Sum(F('total_revenue')))['total_revenue'] or 0

        display_ctr = 0 if views == 0 else clicks/views
        display_cpc = 0 if clicks == 0 else display_ads_spend/clicks
        display_cvr = 0 if clicks == 0 else units/clicks
        display_roi = 0 if display_ads_spend == 0 else revenue/display_ads_spend

        if i == 0: current_par.extend([display_ads_spend, views, clicks, units, revenue, display_ctr, display_cpc, display_cvr, display_roi])
        else: prev_par.extend([display_ads_spend, views, clicks, units, revenue, display_ctr, display_cpc, display_cvr, display_roi])

    for i, j in zip(current_par, prev_par):
        percentage_change = 0 if j == 0 else (i - j)*100/j
        percent_change.append(percentage_change)
    
    return (current_par[0], current_par[5], current_par[6], current_par[7], current_par[8], percent_change[0], percent_change[5], 
            percent_change[6], percent_change[7], percent_change[8], prev_par[0])            
     
"""Till here the above functions are optimized"""

# This is good-to-go
def Flipkart_invoice_parameters(invoice_data_model, start_date=None, end_date=None):

    if start_date and end_date:
        data_model = invoice_data_model.objects.filter(date__range=[start_date, end_date])
    
    else:
        data_model = invoice_data_model.objects.all()
    
    shipping_fee = data_model.filter(fee_name='Shipping Fee').aggregate(shipping=Sum(F('total_fee_amount')))['shipping'] or 0
    reverse_shipping_fee = data_model.filter(fee_name='Reverse Shipping Fee').aggregate(reverse_shipping=Sum(F('total_fee_amount')))['reverse_shipping'] or 0
    sdd_fee = data_model.filter(fee_name='Sdd Fee').aggregate(sdd=Sum(F('total_fee_amount')))['sdd'] or 0
    fixed_fee = data_model.filter(fee_name='Fixed Fee').aggregate(fixed_fee=Sum(F('total_fee_amount')))['fixed_fee'] or 0
    commission_fee = data_model.filter(fee_name='Commission').aggregate(commission=Sum(F('total_fee_amount')))['commission'] or 0
    pick_pack_fee = data_model.filter(fee_name='Pick & Pack Fee').aggregate(pick_pack=Sum(F('total_fee_amount')))['pick_pack'] or 0
    recall_fee = data_model.filter(fee_name='Recall Fee').aggregate(recall=Sum(F('total_fee_amount')))['recall'] or 0
    sellable_fee = data_model.filter(fee_name='Sellable Regular').aggregate(sellable=Sum(F('total_fee_amount')))['sellable'] or 0
    unsellable_fee = data_model.filter(fee_name='Unsellable Regular').aggregate(unsellable=Sum(F('total_fee_amount')))['unsellable'] or 0
    wallet_redeem = data_model.filter(fee_name='Wallet Redeem').aggregate(wallet=Sum(F('total_fee_amount')))['wallet'] or 0
    collection_fee = data_model.filter(fee_name='Collection Fee').aggregate(collection=Sum(F('total_fee_amount')))['collection'] or 0
    cancellation_fee = data_model.filter(fee_name='Cancellation Fee').aggregate(cancellation=Sum(F('total_fee_amount')))['cancellation'] or 0


    return (shipping_fee, reverse_shipping_fee, sdd_fee, fixed_fee, commission_fee, pick_pack_fee, recall_fee, 
            sellable_fee, unsellable_fee, wallet_redeem, collection_fee, cancellation_fee)

"""-------------------------------Flipkart multi-brand Invoice parameters------------------------------------------------"""

def Flipkart_multi_brand_invoice(invoice_data_model, sales_data_model, sub_brand, start_date, end_date):
    
    sales_data_model = sales_data_model.objects.filter(order_date__range=[start_date, end_date], product_title__icontains=sub_brand.lower())
    fees = ['Shipping Fee', 'Reverse Shipping Fee', 'Sdd Fee', 'Fixed Fee', 'Commission', 'Pick & Pack Fee', 'Recall Fee', 'Sellable Fee', 'Unsellable Fee', 'Wallet Redeem', 'Collection Fee', 'Cancellation Fee']
    current_fees = []

    for fee in fees:
        fee_data = invoice_data_model.objects.filter(fee_name=fee, date__range=[start_date, end_date])
        fee_data = fee_data.filter(order_item_id__in=sales_data_model.values_list('order_item_id', flat=True))
        total_fee = fee_data.aggregate(total=Sum('total_fee_amount'))['total'] or 0
        current_fees.append(total_fee)

    return (*current_fees,)


    
        
# This is good-to-go
def calculate_cogs_with_date_filter(sales_data, cogs_vertical, start_date=None, end_date=None):
    
    # ------approach------
    # This functions looks up for every "SKU" that is present in Sales data, into "COGS and Vertical" data
    # for COGS related to that "SKU" and then multiplies it with the item_quantity and that's how cogs is taken into account 


    # Apply date filter to sales data
    if start_date and end_date:
        sales = sales_data.objects.filter(order_date__range=[start_date, end_date])
    else:
        sales = sales_data.objects.all()

    # Subquery for COGS and Vertical data from the 'cogs_vertical' model
    cogs_vertical_subquery = cogs_vertical.objects.filter(sku=OuterRef('sku')).values('cogs')[:1]

    # Annotate sales data with Vertical and COGS values, and calculate total COGS for each item
    sales_with_data = sales.annotate(
        COGS=Coalesce(Subquery(cogs_vertical_subquery), Value(0), output_field=DecimalField(max_digits=10, decimal_places=2))
    ).annotate(
        total_cogs=F('COGS') * F('item_quantity')  # Multiply COGS by quantity
    )

    # Calculate COGS for different event types
    sales_cogs = sales_with_data.filter(event_sub_type='Sale').aggregate(sales_cogs=Sum('total_cogs'))['sales_cogs'] or 0
    return_cancellation_cogs = sales_with_data.filter(event_sub_type='Return Cancellation').aggregate(return_can_cogs=Sum('total_cogs'))['return_can_cogs'] or 0
    return_cogs = sales_with_data.filter(event_sub_type='Return').aggregate(total_cogs=Sum('total_cogs'))['total_cogs'] or 0
    cancellation_cogs = sales_with_data.filter(event_sub_type='Cancellation').aggregate(total_cogs=Sum('total_cogs'))['total_cogs'] or 0

    # Calculate the total COGS
    cogs = sales_cogs + return_cancellation_cogs - return_cogs - cancellation_cogs

    return cogs

""""-------------------------------------Flipkart multi-brand COGS calculator function for NexTen Brands------------------"""

def calculate_cogs_multi_brand(sales_data, cogs_vertical, brand, start_date, end_date):

    # Apply date filter to sales data
    if start_date and end_date:
        sales = sales_data.objects.filter(order_date__range=[start_date, end_date], product_title__icontains=brand.lower())
    else:
        sales = sales_data.objects.all()

    # Subquery for COGS and Vertical data from the 'cogs_vertical' model
    cogs_vertical_subquery = cogs_vertical.objects.filter(sku=OuterRef('sku')).values('cogs')[:1]

    # Annotate sales data with Vertical and COGS values, and calculate total COGS for each item
    sales_with_data = sales.annotate(
        COGS=Coalesce(Subquery(cogs_vertical_subquery), Value(0), output_field=DecimalField(max_digits=10, decimal_places=2))
    ).annotate(
        total_cogs=F('COGS') * F('item_quantity')  # Multiply COGS by quantity
    )

    # Calculate COGS for different event types
    sales_cogs = sales_with_data.filter(event_sub_type='Sale').aggregate(sales_cogs=Sum('total_cogs'))['sales_cogs'] or 0
    return_cancellation_cogs = sales_with_data.filter(event_sub_type='Return Cancellation').aggregate(return_can_cogs=Sum('total_cogs'))['return_can_cogs'] or 0
    return_cogs = sales_with_data.filter(event_sub_type='Return').aggregate(total_cogs=Sum('total_cogs'))['total_cogs'] or 0
    cancellation_cogs = sales_with_data.filter(event_sub_type='Cancellation').aggregate(total_cogs=Sum('total_cogs'))['total_cogs'] or 0

    # Calculate the total COGS
    cogs = sales_cogs + return_cancellation_cogs - return_cogs - cancellation_cogs

    return cogs


# For the upcoming new version
def Flipkart_PnL_parameters_new(sales_data, ads_data, cogs_vertical, invoice_data, return_data, seller, start_date, end_date):

    
    """COGS details"""
    # current cogs
    cogs = calculate_cogs_with_date_filter(sales_data, cogs_vertical, start_date, end_date)
    
    """Invoice details"""
    # current invoice details
    (shipping_fee, reverse_shipping_fee, sdd_fee, fixed_fee, commission_fee, pick_pack_fee, recall_fee, 
        sellable_fee, unsellable_fee, wallet_redeem, collection_fee, cancellation_fee) = Flipkart_invoice_parameters(invoice_data, start_date, end_date)    

    """Ads details"""
    # current ads details
    if (seller == 'TRI'):
        (ads_spend, _, _, _, _, _, _, _, _, _, _) = Flipkart_ads_parameters(ads_data, start_date, end_date)
    else:
        (ads_spend, _, _, _, _, _, _, _, _, _, _) = Flipkart_MP_ads_parameters(ads_data, start_date, end_date)
        

    """Sales details"""
    # current sales details
    (_, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, gmv, qty, return_rev, return_qty, cancellation_rev, cancellation_qty, 
     net_gmv, net_qty, net_gmv_without_tax, tax, total_bank_dis, _) = Flipkart_sales_parameters(sales_data, return_data, start_date, end_date)
    
    # Below here only are the new changes, so if you want to go back to normal, you can simply erase the below code
    warehouse_cost = 0
    
    if (seller == 'TRI'):
        warehouse_cost = 1000249
        days_count = (end_date - start_date).days  # This gets the number of days as an integer.
        if days_count > 0:
            warehouse_cost = float(warehouse_cost*days_count / 30)
        else:
            warehouse_cost = warehouse_cost/30  # Handle division by zero case.
    else:
        warehouse_cost = 0

    codb = float(shipping_fee) + float(reverse_shipping_fee) + float(sdd_fee) + float(fixed_fee) + float(commission_fee) + float(pick_pack_fee) + float(recall_fee) + float(sellable_fee) + float(unsellable_fee) + float(collection_fee) + float(cancellation_fee)
    net_revenue_with_tax = float(net_gmv) + float(total_bank_dis)
    net_revenue_without_tax = float(net_revenue_with_tax) - float(tax)
    product_margin = float(net_revenue_without_tax) - float(cogs)
    cm1 = float(product_margin) + float(codb)
    cm2 = float(cm1) - float(warehouse_cost)
    cm3 = float(cm2) - float((ads_spend - wallet_redeem))
    profit_percentage = 0 if net_revenue_with_tax == 0 else float(cm3)*100/float(net_revenue_without_tax)
    
    results = [round(float(value), 2) for value in [
        gmv, qty, cancellation_rev, cancellation_qty, return_rev, return_qty, total_bank_dis,
        net_revenue_with_tax, net_qty, tax, net_gmv_without_tax, cogs, product_margin, codb,
        shipping_fee, reverse_shipping_fee, sdd_fee, fixed_fee, commission_fee, pick_pack_fee,
        recall_fee, sellable_fee, unsellable_fee, wallet_redeem, collection_fee, cancellation_fee,
        cm1, warehouse_cost, cm2, ads_spend, cm3, profit_percentage
    ]]
    
    return results


def Flipkart_PnL_calculator(start_date, end_date, time_format, seller):
    
    no_of_days = (end_date - start_date).days + 1
    no_of_weeks = no_of_days//7 + 1
    no_of_months = no_of_days//30 + 1

    results = [0] * 32

    pnl_details = {}

    # For seeing the Pnl day-wise
    if time_format == 'day':
        
        start_date_i = start_date
        end_date_i = start_date

        for i in range(1, no_of_days+1):
            
            if end_date_i > end_date:
                break
            
            sub_final = []

            if seller != 'All Seller':
                data_model = brand_models[seller]
                results = Flipkart_PnL_parameters_new(
                    data_model["sales"],
                    data_model["ads"],
                    data_model["cogs"],
                    data_model["invoices"],
                    data_model["returns"],
                    seller,
                    start_date_i,
                    end_date_i
                )
            else:
                # This is for calculating "All Seller"
                for data_model in brand_models:
                    sub_final = Flipkart_PnL_parameters_new(
                        brand_models[data_model]["sales"],
                        brand_models[data_model]["ads"],
                        brand_models[data_model]["cogs"],
                        brand_models[data_model]["invoices"],
                        brand_models[data_model]["returns"],
                        data_model,
                        start_date_i,
                        end_date_i
                    )

                    results = [a + b for a,b in zip(sub_final, results)]
            
            # Convert string to datetime object
            # start_i = start_date_i
            start_i = start_date_i.date()

            pnl_details[f"{start_i}"] = results
            
            results = [0] * 32

            start_date_i = end_date_i + timedelta(1)
            end_date_i = start_date_i
            
        return pnl_details

    # For seeing the PnL week-wise
    elif time_format == 'week':
        
        if no_of_weeks == 1:
            start_date_i = start_date
            end_date_i = end_date

        else:
            start_date_i = start_date
            end_date_i = start_date + timedelta(6)

        for i in range(1, no_of_weeks+1):

            if end_date_i > end_date or start_date_i > end_date_i:
                break

            sub_final = []

            if seller != 'All Seller':
                data_model = brand_models[seller]
                results = Flipkart_PnL_parameters_new(
                    data_model["sales"],
                    data_model["ads"],
                    data_model["cogs"],
                    data_model["invoices"],
                    data_model["returns"],
                    seller,
                    start_date_i,
                    end_date_i
                )
            else:
                # This for calculating "All Seller"
                for data_model in brand_models:
                    sub_final = Flipkart_PnL_parameters_new(
                        brand_models[data_model]["sales"],
                        brand_models[data_model]["ads"],
                        brand_models[data_model]["cogs"],
                        brand_models[data_model]["invoices"],
                        brand_models[data_model]["returns"],
                        data_model,
                        start_date_i,
                        end_date_i
                    )

                    results = [a + b for a,b in zip(sub_final, results)]
            
            start_i = start_date_i.date()
            end_i = end_date_i.date()


            pnl_details[f"{start_i}_to_{end_i}"] = results
            
            results = [0] * 32

            start_date_i = end_date_i + timedelta(1)

            if ((no_of_days - i*7) >= 7):
                end_date_i = start_date_i + timedelta(6)
            elif (no_of_days - i*7 > 0):
                end_date_i = start_date_i + timedelta(no_of_days - i*7 - 1)
            
        return pnl_details

    # For seeing the PnL month-wise
    elif time_format == "month":

        if no_of_months == 1:
            start_date_i = start_date
            end_date_i = end_date

        else:
            start_date_i = start_date
            end_date_i = start_date + timedelta(29)
        
        for i in range(1, no_of_months+1):

            if end_date_i > end_date or start_date_i > end_date_i:
                break

            sub_final = []

            if seller != 'All Seller':
                data_model = brand_models[seller]
                results = Flipkart_PnL_parameters_new(
                    data_model["sales"],
                    data_model["ads"],
                    data_model["cogs"],
                    data_model["invoices"],
                    data_model["returns"],
                    seller,
                    start_date_i,
                    end_date_i
                )
            else:
                for data_model in brand_models:
                    sub_final = Flipkart_PnL_parameters_new(
                        brand_models[data_model]["sales"],
                        brand_models[data_model]["ads"],
                        brand_models[data_model]["cogs"],
                        brand_models[data_model]["invoices"],
                        brand_models[data_model]["returns"],
                        data_model,
                        start_date_i,
                        end_date_i
                    )

                    results = [a + b for a,b in zip(sub_final, results)]

            # Convert string to datetime object
            start_i = start_date_i.date()
            end_i = end_date_i.date()
            

            pnl_details[f"{start_i}_to_{end_i}"] = results

            results = [0] * 32

            start_date_i = end_date_i + timedelta(1)

            if ((no_of_days - i*30) >= 30):
                end_date_i = start_date_i + timedelta(29)
            elif (no_of_days - i*30 > 0):
                end_date_i = start_date_i + timedelta(no_of_days - i*30 - 1)

        return pnl_details
        
    else:

        start_date_i = start_date
        end_date_i = end_date

        if seller != 'All Seller':
                data_model = brand_models[seller]
                results = Flipkart_PnL_parameters_new(
                    data_model["sales"],
                    data_model["ads"],
                    data_model["cogs"],
                    data_model["invoices"],
                    data_model["returns"],
                    seller,
                    start_date_i,
                    end_date_i
                )
        else:
            for data_model in brand_models:
                sub_final = Flipkart_PnL_parameters_new(
                    brand_models[data_model]["sales"],
                    brand_models[data_model]["ads"],
                    brand_models[data_model]["cogs"],
                    brand_models[data_model]["invoices"],
                    brand_models[data_model]["returns"],
                    data_model,
                    start_date_i,
                    end_date_i
                )

                results = [a + b for a,b in zip(sub_final, results)]

        # Convert string to datetime object
        start_i = start_date_i.date()
        end_i = end_date_i.date()
            

        pnl_details[f"{start_i}_to_{end_i}"] = results

        return pnl_details
    
"""---------------------------------------Flipkart multi-brand PnL parameter calculation----------------------------------"""

def Flipkart_PnL_parameters_multi_brand(sales_data, ads_data, cogs_vertical, invoice_data, return_data, brand, start_date, end_date):

    """COGS details"""
    # current cogs
    cogs = calculate_cogs_multi_brand(sales_data, cogs_vertical, brand, start_date, end_date)
    
    """Invoice details"""
    # current invoice details
    (shipping_fee, reverse_shipping_fee, sdd_fee, fixed_fee, commission_fee, pick_pack_fee, recall_fee, 
        sellable_fee, unsellable_fee, wallet_redeem, collection_fee, cancellation_fee) = Flipkart_multi_brand_invoice(invoice_data, sales_data, brand, start_date, end_date)    

    """Ads details"""
    # current ads details
    (ads_spend, _, _, _, _, _, _, _, _, _, _) = Flipkart_MP_ads_multi_brand(ads_data, brand, start_date, end_date)
        

    """Sales details"""
    # current sales details
    (_, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, gmv, qty, return_rev, return_qty, cancellation_rev, cancellation_qty, 
     net_gmv, net_qty, net_gmv_without_tax, tax, total_bank_dis, _) = Flipkart_multi_brand_sales(sales_data, return_data, brand, start_date, end_date)
    
    # Below here only are the new changes, so if you want to go back to normal, you can simply erase the below code
    warehouse_cost = 0

    codb = float(shipping_fee) + float(reverse_shipping_fee) + float(sdd_fee) + float(fixed_fee) + float(commission_fee) + float(pick_pack_fee) + float(recall_fee) + float(sellable_fee) + float(unsellable_fee) + float(collection_fee) + float(cancellation_fee)
    net_revenue_with_tax = float(net_gmv) + float(total_bank_dis)
    net_revenue_without_tax = float(net_revenue_with_tax) - float(tax)
    product_margin = float(net_revenue_without_tax) - float(cogs)
    cm1 = float(product_margin) + float(codb)
    cm2 = float(cm1) - float(warehouse_cost)
    cm3 = float(cm2) - float((ads_spend - wallet_redeem))
    profit_percentage = 0 if net_revenue_with_tax == 0 else float(cm3)*100/float(net_revenue_without_tax)
    
    results = [round(float(value), 2) for value in [
        gmv, qty, cancellation_rev, cancellation_qty, return_rev, return_qty, total_bank_dis,
        net_revenue_with_tax, net_qty, tax, net_gmv_without_tax, cogs, product_margin, codb,
        shipping_fee, reverse_shipping_fee, sdd_fee, fixed_fee, commission_fee, pick_pack_fee,
        recall_fee, sellable_fee, unsellable_fee, wallet_redeem, collection_fee, cancellation_fee,
        cm1, warehouse_cost, cm2, ads_spend, cm3, profit_percentage
    ]]
    
    return results


def Flipkart_PnL_calculator_multi_brand(start_date, end_date, time_format, seller, brand):
    
    no_of_days = (end_date - start_date).days + 1
    no_of_weeks = no_of_days//7 + 1
    no_of_months = no_of_days//30 + 1

    results = []

    model = brand_models[seller]

    pnl_details = {}

    # For seeing the Pnl day-wise
    if time_format == 'day':
        
        start_date_i = start_date
        end_date_i = start_date

        for i in range(1, no_of_days+1):
            
            if end_date_i > end_date:
                break

            
            results = Flipkart_PnL_parameters_multi_brand(
                model["sales"],
                model["ads"],
                model["cogs"],
                model["invoices"],
                model["returns"],
                brand,
                start_date_i,
                end_date_i
            )

            
            # Convert string to datetime object
            start_i = start_date_i.date()

            pnl_details[f"{start_i}"] = results

            start_date_i = end_date_i + timedelta(1)
            end_date_i = start_date_i
            
        return pnl_details

    # For seeing the PnL week-wise
    elif time_format == 'week':
        
        if no_of_weeks == 1:
            start_date_i = start_date
            end_date_i = end_date

        else:
            start_date_i = start_date
            end_date_i = start_date + timedelta(6)

        for i in range(1, no_of_weeks+1):

            if end_date_i > end_date or start_date_i > end_date_i:
                break

            results = Flipkart_PnL_parameters_multi_brand(
                model["sales"],
                model["ads"],
                model["cogs"],
                model["invoices"],
                model["returns"],
                brand,
                start_date_i,
                end_date_i
            )

            start_i = start_date_i.date()
            end_i = end_date_i.date()


            pnl_details[f"{start_i}_to_{end_i}"] = results

            start_date_i = end_date_i + timedelta(1)

            if ((no_of_days - i*7) >= 7):
                end_date_i = start_date_i + timedelta(6)
            elif (no_of_days - i*7 > 0):
                end_date_i = start_date_i + timedelta(no_of_days - i*7 - 1)
            
        return pnl_details

    # For seeing the PnL month-wise
    elif time_format == "month":

        if no_of_months == 1:
            start_date_i = start_date
            end_date_i = end_date

        else:
            start_date_i = start_date
            end_date_i = start_date + timedelta(29)
        
        for i in range(1, no_of_months+1):

            if end_date_i > end_date or start_date_i > end_date_i:
                break

            results = Flipkart_PnL_parameters_multi_brand(
                model["sales"],
                model["ads"],
                model["cogs"],
                model["invoices"],
                model["returns"],
                brand,
                start_date_i,
                end_date_i
            )
            # Convert string to datetime object
            start_i = start_date_i.date()
            end_i = end_date_i.date()
            

            pnl_details[f"{start_i}_to_{end_i}"] = results

            results = [0] * 32

            start_date_i = end_date_i + timedelta(1)

            if ((no_of_days - i*30) >= 30):
                end_date_i = start_date_i + timedelta(29)
            elif (no_of_days - i*30 > 0):
                end_date_i = start_date_i + timedelta(no_of_days - i*30 - 1)

        return pnl_details
        
    else:

        start_date_i = start_date
        end_date_i = end_date

        results = Flipkart_PnL_parameters_multi_brand(
                model["sales"],
                model["ads"],
                model["cogs"],
                model["invoices"],
                model["returns"],
                brand,
                start_date_i,
                end_date_i
            )
        # Convert string to datetime object
        start_i = start_date_i.date()
        end_i = end_date_i.date()
            

        pnl_details[f"{start_i}_to_{end_i}"] = results

        return pnl_details


# This works for both the sub_brand and only brand case
def get_dynamic_plot_flipkart(sales, ads, brand, start_date, end_date, seller):
    
    import pandas as pd
    from plotly.subplots import make_subplots
    import plotly.graph_objects as go
    from django.db.models import Sum, F, Q
    from django.db.models.functions import Cast
    from django.db.models import FloatField, ExpressionWrapper

    if brand == "":
        # Query sales and ads data within the date range
        sales_data = sales.objects.filter(order_date__range=[start_date, end_date])
        ads_data = ads.objects.filter(date__range=[start_date, end_date])
    
    else:
        # Query sales and ads data within the date range
        sales_data = sales.objects.filter(order_date__range=[start_date, end_date], product_title__icontains=brand.lower())
        ads_data = ads.objects.filter(date__range=[start_date, end_date], campaign_name__icontains=brand.lower())
    
    # Define data aggregations
    data_aggregation_sales = {
        'gmv': Sum('final_invoice_amount', filter=(Q(event_sub_type='Sale') | Q(event_sub_type='Return Cancellation'))),
        'qty': Sum('item_quantity', filter=(Q(event_sub_type='Sale') | Q(event_sub_type='Return Cancellation'))),
    }
    data_aggregation_ads = {
        'views': Sum('views'),
        'adsSpend': Sum('ad_spend'),
    }

    figures = {}

    # Helper function to create a Plotly figure
    def create_figure(df, metric):
        fig = make_subplots(rows=1, cols=1)
        fig.add_trace(go.Scatter(
            x=df['date'],
            y=df['total_metric'],
            mode='lines+markers',
            marker=dict(size=8),
            line=dict(width=2),
            hoverinfo='x+y',
            name=metric.upper()
        ))
        fig.update_layout(
            title=f'{metric.upper()} vs Date',
            xaxis=dict(title='Date', tickangle=45),
            yaxis=dict(title=metric.upper(), tickformat=".2f"),
            template='plotly_white',
            autosize=True,
            margin=dict(l=40, r=40, t=40, b=40)
        )
        return fig.to_json()

    # Generate plots for all metrics
    for graph_type, aggregation in {**data_aggregation_sales, **data_aggregation_ads}.items():
        if graph_type in data_aggregation_sales:
            aggregated_data = (
                sales_data.values('order_date')
                .annotate(total_metric=Cast(aggregation, FloatField()))
                .order_by('order_date')
            )
        elif graph_type in data_aggregation_ads:
            aggregated_data = (
                ads_data.values('date')
                .annotate(total_metric=Cast(aggregation, FloatField()))
                .order_by('date')
            )

        # Convert to DataFrame
        df = pd.DataFrame(list(aggregated_data))
        df.rename(columns={'order_date': 'date'} if graph_type in data_aggregation_sales else {'date': 'date'}, inplace=True)

        if df.empty:
            df = pd.DataFrame({'date': [start_date], 'total_metric': [0]})

        figures[graph_type] = create_figure(df, graph_type)

    # Add ROI calculations
    if seller == 'TRI':
        roi_data = (
            ads_data.values('date')
            .annotate(
                total_indirect_revenue=Sum('indirect_revenue'),
                total_direct_revenue=Sum('direct_revenue'),
                total_ad_spend=Sum('ad_spend'),
                roi=ExpressionWrapper(
                    (Sum('indirect_revenue') + Sum('direct_revenue')) / Sum('ad_spend'),
                    output_field=FloatField()
                )
            )
            .annotate(total_metric=F('roi'))
            .order_by('date')
        )

    else:
        roi_data = (
            ads_data.values('date')
            .annotate(
                total_ad_revenue=Sum('total_revenue'),
                total_ad_spend=Sum('ad_spend'),
                roi=ExpressionWrapper(Sum('total_revenue') / Sum('ad_spend'), output_field=FloatField())
            )
            .annotate(total_metric=F('roi'))
            .order_by('date')
        )

    df = pd.DataFrame(list(roi_data))
    df.rename(columns={'date': 'date'}, inplace=True)

    if df.empty:
        df = pd.DataFrame({'date': [start_date], 'total_metric': [0]})

    figures['roi'] = create_figure(df, 'roi')

    return {"dynamic_plot": figures}



# This works in both the cases, for sub-brands and for only brand case as well
def demographic_plot_flipkart(sales, brand, start_date, end_date):
    
    if brand == "":

        state_order_data = (
            sales.objects
            .filter(order_date__range=[start_date, end_date])
            .values('customer_delivery_state')
            .annotate(total_quantity=Sum('item_quantity'))
            .order_by('total_quantity')
        )

    else:
        state_order_data = (
            sales.objects
            .filter(order_date__range=[start_date, end_date], product_title__icontains=brand.lower())
            .values('customer_delivery_state')
            .annotate(total_quantity=Sum('item_quantity'))
            .order_by('total_quantity')
        )

    all_states = [
        "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh", "Goa", "Gujarat", 
        "Haryana", "Himachal Pradesh", "Jammu and Kashmir", "Jharkhand", "Karnataka", "Kerala", 
        "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram", "Nagaland", "Odisha", 
        "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana", "Tripura", "Uttar Pradesh", 
        "Uttarakhand", "West Bengal", "Andaman and Nicobar Islands", "Chandigarh", 
        "Dadra and Nagar Haveli and Daman and Diu", "Delhi", "Ladakh", "Lakshadweep", "Puducherry"
    ]

    df = pd.DataFrame(list(state_order_data))

    if df.empty:
        # Create a new DataFrame with all_states and total_quantity set to 0
        df = pd.DataFrame({
            'customer_delivery_state': all_states,
            'total_quantity': [0] * len(all_states)
        })

    # Fix naming issues and standardize
    state_replacements = {
        "Dadra & Nagar Haveli & Daman & Diu": "Dadra and Nagar Haveli and Daman and Diu",
        "Jammu & Kashmir": "Jammu and Kashmir",
        "Pondicherry": "Puducherry",
    }
    df["customer_delivery_state"] = df["customer_delivery_state"].replace(state_replacements)
    df = df[df["customer_delivery_state"] != "-"]

    # Get current states in the data
    current_states = set(df['customer_delivery_state'].unique())
    
    # Find missing states
    missing_states = set(all_states) - current_states
    
    # Add missing states with zero values
    if missing_states:
        missing_df = pd.DataFrame({
            'customer_delivery_state': list(missing_states),
            'total_quantity': [0] * len(missing_states)
        })
        df = pd.concat([df, missing_df], ignore_index=True)

    # Load the India GeoJSON
    with open("india.geojson", "r", encoding="utf-8") as f:
        india_geojson = json.load(f)

    # Convert to GeoDataFrame
    gdf = gpd.GeoDataFrame.from_features(india_geojson)
    
    # Dissolve districts into states
    gdf_dissolved = gdf.dissolve(by='st_nm', as_index=False)
    
    # Convert back to GeoJSON
    simplified_geojson = json.loads(gdf_dissolved.to_json())

    # Create the choropleth figure with simplified GeoJSON
    fig = go.Figure(data=go.Choropleth(
        geojson=simplified_geojson,
        locations=df['customer_delivery_state'],
        z=df['total_quantity'],
        locationmode='geojson-id',
        featureidkey='properties.st_nm',
        colorscale='Greens',
        colorbar=dict(
            title="Order Quantity",
            x=0.85,  # Shift color scale closer to the map
            y=0.5,   # Center color scale vertically
            ticks="outside"
        ),
        hovertemplate="<b>State: %{location}</b><br>" +
                      "Orders: %{z}<br><extra></extra>",
        showscale=True
    ))

    # Update the layout for better visualization
    fig.update_geos(
        visible=False,
        center=dict(lat=23.5937, lon=78.9629),  # Center of India
        projection_scale=5.5,  # Zoom into the map for a tighter fit
        showcoastlines=False,
        showframe=False,
        fitbounds="locations"  # Ensures the map tightly fits the data
    )

    fig.update_layout(
        title=dict(
            text='Order Distribution Across India',
            x=0.5,
            y=0.95
        ),
        geo=dict(
            scope='asia',
            showlakes=False,
            showcountries=False,
            subunitcolor='black',
            subunitwidth=1,
            showland=True,
            landcolor='white'
        ),
        margin=dict(r=0, t=0, l=0, b=0),  # Remove unnecessary margins
        height=500,  # Chart height
        width=600   # Chart width for a compact layout
    )

    return fig.to_json()


# This works for both the cases, for sub-brands and for only brand case as well
def pie_chart_flipkart(sales_data, master_sku, brand, start_date, end_date):

    if brand == "":
        sales_data = sales_data.objects.filter(order_date__range=[start_date, end_date])
    else:
        sales_data = sales_data.objects.filter(product_title__icontains=brand.lower(), order_date__range=[start_date, end_date])

    # Subqueries for product title and vertical
    product_title_subquery = master_sku.objects.filter(sku=OuterRef('sku')).values('product_title')[:1]
    product_vertical_subquery = master_sku.objects.filter(sku=OuterRef('sku')).values('product_vertical')[:1]

    # Annotate sales data with product title and vertical
    sales_with_title = sales_data.annotate(
        consolidated_product_title=Coalesce(Subquery(product_title_subquery), Value("Unknown"), output_field=CharField()),
        product_sku=F('sku'),
        vertical=Coalesce(Subquery(product_vertical_subquery), Value("Unknown"), output_field=CharField())
    )

    # Aggregate GMV by vertical
    sales_aggregation_by_vertical = sales_with_title.values('vertical').annotate(
        gmv=Cast(Sum('final_invoice_amount', filter=(Q(event_sub_type='Sale') | Q(event_sub_type='Return Cancellation'))), FloatField())
    ).order_by('vertical')

    # Calculate total GMV
    total_gmv = sum(item['gmv'] for item in sales_aggregation_by_vertical if item['gmv'])

    # Add GMV proportions for each vertical
    sales_aggregation_with_proportions = [
        {
            'vertical': item['vertical'],
            'gmv': item['gmv'],
            'gmv_proportion': round((item['gmv'] * 100 / total_gmv), 2) if total_gmv else 0  # Avoid division by zero
        }
        for item in sales_aggregation_by_vertical
    ]

    # Prepare data for the Plotly pie chart
    labels = [
        f"{item['vertical']} ({item['gmv_proportion']}%)"
        for item in sales_aggregation_with_proportions
    ]
    sizes = [item['gmv'] for item in sales_aggregation_with_proportions]

    # Create a Plotly pie chart without annotations inside the chart
    fig = go.Figure(
        data=[
            go.Pie(
                labels=labels,
                values=sizes,
                textinfo='none',  # Disable text on the pie chart
                hoverinfo='label+percent',  # Display label and percentage on hover
                # marker=dict(line=dict(color='black', width=1))  # Outline the slices
            )
        ]
    )

    # Update layout for the pie chart with extra top margin for title spacing
    fig.update_layout(
        title="GMV Distribution by Vertical",
        title_y=0.95,  # Adjust title position slightly down
        showlegend=True,
        legend_title="Verticals",
        legend=dict(
            itemsizing="constant",
            orientation="v",  # Vertical orientation for the legend
            x=1.1,  # Adjust this to move the legend closer to the pie chart
            y=0.5,  # Center the legend vertically
            xanchor="left",  # Anchor the legend closer to the pie chart
            bgcolor="rgba(255, 255, 255, 0)",  # Transparent background
        ),
        margin=dict(
            l=10,  # Left margin
            r=10,  # Right margin
            t=60,  # Increased top margin for title spacing
            b=10   # Bottom margin
        ),
        height=500,  # Adjust chart height
        width=600    # Adjust chart width
    )

    # Convert the Plotly figure to JSON
    return fig.to_json()



def return_product_flipkart(sales, master_sku, start_date, end_date):

    """This for accounting the sales that happend in the selected date range"""
    if (start_date and end_date):
        sales_data = sales.objects.filter(order_date__range=[start_date, end_date])

    else:
        sales_data = sales.objects.all()


    product_title_subquery = master_sku.objects.filter(sku=OuterRef('sku')).values('product_title')[:1]
    product_vertical_subquery = master_sku.objects.filter(sku=OuterRef('sku')).values('product_vertical')[:1]


    """Calculation for sales"""
    sales_with_title = sales_data.annotate(
        consolidated_product_title=Coalesce(Subquery(product_title_subquery), Value("Unknown"), output_field=CharField()),
        product_sku=F('sku'),
        vertical=Coalesce(Subquery(product_vertical_subquery), Value("Unknown"), output_field=CharField())
    )

    # Aggregation based on consolidated_product_title
    sales_aggregation_by_title = sales_with_title.values('sku','consolidated_product_title').annotate(
        gmv=Cast(Sum('final_invoice_amount', filter=(Q(event_sub_type='Sale') | Q(event_sub_type='Return Cancellation'))), FloatField()),
        qty=Cast(Sum('item_quantity', filter=(Q(event_sub_type='Sale') | Q(event_sub_type='Return Cancellation'))), FloatField()),
    ).order_by('sku')

    # Aggregation based on vertical
    sales_aggregation_by_vertical = sales_with_title.values('vertical').annotate(
        vertical_gmv=Cast(Sum('final_invoice_amount', filter=(Q(event_sub_type='Sale') | Q(event_sub_type='Return Cancellation'))), FloatField()),
        vertical_qty=Cast(Sum('item_quantity', filter=(Q(event_sub_type='Sale') | Q(event_sub_type='Return Cancellation'))), FloatField()),
    ).order_by('vertical')

    
    """This is for account the returns that will be made in the coming 20 days from the end date"""

    # Extend the date range by 20 days
    extended_end_date = end_date + timedelta(days=45)

    # Get the OrderIDs where event_sub_type = "Sale" within the selected date range
    sale_order_ids = sales.objects.filter(
        event_sub_type="Sale",
        order_date__range=[start_date, end_date]
    ).values_list('order_id', flat=True)

    """Calculation for returns"""
    # Check for 'Return' event_sub_type for these OrderIDs within the extended range
    returned_orders = sales.objects.filter(
        order_id__in=sale_order_ids,
        event_sub_type="Return",
        order_date__range=[start_date, extended_end_date]
    ).values_list('order_id', flat=True)

    # Annotate sales data with product title, SKU
    returned_with_title = returned_orders.annotate(
        consolidated_product_title=Coalesce(Subquery(product_title_subquery), Value("Unknown"), output_field=CharField()),
        product_sku=F('sku')
    )

    # Annotate sales data with product title, SKU
    returned_with_vertical = returned_orders.annotate(
        vertical=Coalesce(Subquery(product_vertical_subquery), Value("Unknown"), output_field=CharField()),
        product_sku=F('sku')
    )

    # Aggregate details for returned SKUs
    return_aggregation_by_title = returned_with_title.values('sku', 'consolidated_product_title').annotate(
        returned_gmv=Cast(Sum('final_invoice_amount'), FloatField()),  # Sum of GMV
        returned_qty=Cast(Sum('item_quantity'), FloatField())  # Sum of quantities
    ).order_by('sku')  # Optional: Order by SKU for better readability
    
    # Aggregate details for returned SKUs
    return_aggregation_by_vertical = returned_with_vertical.values('vertical').annotate(
        returned_vertical_gmv=Cast(Sum('final_invoice_amount'), FloatField()),  # Sum of GMV
        returned_vertical_qty=Cast(Sum('item_quantity'), FloatField())  # Sum of quantities
    ).order_by('vertical')  # Optional: Order by SKU for better readability

    """This accounts for the cancellations that happened in the next 20 days from the end date"""

    cancellation_orders = sales.objects.filter(
        order_id__in=sale_order_ids,
        event_sub_type="Cancellation",
        order_date__range=[start_date, extended_end_date]
    ).values_list('order_id', flat=True)
    

    """Calculation for cancellations"""
    # Annotate sales data with product title, SKU
    cancellation_with_title = cancellation_orders.annotate(
        consolidated_product_title=Coalesce(Subquery(product_title_subquery), Value("Unknown"), output_field=CharField()),
        product_sku=F('sku')
    )

    # Annotate sales data with product title, SKU
    cancellation_with_vertical = cancellation_orders.annotate(
        vertical=Coalesce(Subquery(product_vertical_subquery), Value("Unknown"), output_field=CharField()),
        product_sku=F('sku')
    )

    # Aggregate details for returned SKUs
    cancelled_aggregation_by_title = cancellation_with_title.values('sku', 'consolidated_product_title').annotate(
        cancelled_gmv=Cast(Sum('final_invoice_amount'), FloatField()),  # Sum of GMV
        cancelled_qty=Cast(Sum('item_quantity'), FloatField())  # Sum of quantities
    ).order_by('sku')  # Optional: Order by SKU for better readability
    
    # Aggregate details for returned SKUs
    cancelled_aggregation_by_vertical = cancellation_with_vertical.values('vertical').annotate(
        cancelled_vertical_gmv=Cast(Sum('final_invoice_amount'), FloatField()),  # Sum of GMV
        cancelled_vertical_qty=Cast(Sum('item_quantity'), FloatField())  # Sum of quantities
    ).order_by('vertical')  # Optional: Order by SKU for better readability

    """For calculating the net gmv and qty both by vertical and by title"""

    # Convert QuerySets into dictionaries keyed by sku (for title-level) and vertical (for vertical-level)
    sales_title_dict = {record['sku']: record for record in sales_aggregation_by_title}
    sales_vertical_dict = {record['vertical']: record for record in sales_aggregation_by_vertical}

    return_title_dict = {record['sku']: record for record in return_aggregation_by_title}
    return_vertical_dict = {record['vertical']: record for record in return_aggregation_by_vertical}

    cancellation_title_dict = {record['sku']: record for record in cancelled_aggregation_by_title}
    cancellation_vertical_dict = {record['vertical']: record for record in cancelled_aggregation_by_vertical}

    # Get union of all SKUs and verticals
    all_title = set(sales_title_dict.keys()) | set(return_title_dict.keys()) | set(cancellation_title_dict.keys())
    all_vertical = set(sales_vertical_dict.keys()) | set(return_vertical_dict.keys()) | set(cancellation_vertical_dict.keys())

    # Calculate net sales by title (using SKU as key)
    net_sale_by_title = {}
    for sku in all_title:
        sales_record = sales_title_dict.get(sku, {})
        return_record = return_title_dict.get(sku, {})
        cancellation_record = cancellation_title_dict.get(sku, {})

        net_sale_by_title[sku] = {
            'net_gmv': (sales_record.get('gmv') or 0) - (return_record.get('returned_gmv') or 0) - (cancellation_record.get('cancelled_gmv') or 0),
            'net_qty': (sales_record.get('qty') or 0) - (return_record.get('returned_qty') or 0) - (cancellation_record.get('cancelled_qty') or 0),
            'consolidated_product_title': sales_record.get('consolidated_product_title', "Unknown")
        }

    # Calculate net sales by vertical
    net_sales_by_vertical = {}
    for vertical in all_vertical:
        sales_record = sales_vertical_dict.get(vertical, {})
        return_record = return_vertical_dict.get(vertical, {})
        cancellation_record = cancellation_vertical_dict.get(vertical, {})

        net_sales_by_vertical[vertical] = {
            'net_vertical_gmv': (sales_record.get('vertical_gmv') or 0) - (return_record.get('returned_vertical_gmv') or 0) - (cancellation_record.get('cancelled_vertical_gmv') or 0),
            'net_vertical_qty': (sales_record.get('vertical_qty') or 0) - (return_record.get('returned_vertical_qty') or 0) - (cancellation_record.get('cancelled_vertical_qty') or 0),
            'vertical': sales_record.get('vertical', vertical)
        }


    return {
        "sales_by_title":sales_aggregation_by_title,
        "sales_by_vertical":sales_aggregation_by_vertical,

        "return_by_title":return_aggregation_by_title,
        "return_by_vertical":return_aggregation_by_vertical,

        "cancellation_by_title":cancelled_aggregation_by_title,
        "cancellation_by_vertical":cancelled_aggregation_by_vertical,

        "net_sales_by_title":net_sale_by_title,
        "net_sales_by_vertical":net_sales_by_vertical
    }


"""------------------------------------Flipkart multi-brand return product details--------------------------------------"""

def return_product_flipkart_multi_brand(sales, master_sku, brand, start_date, end_date):

    sales_data = sales.objects.filter(order_date__range=[start_date, end_date], product_title__icontains=brand.lower())

    product_title_subquery = master_sku.objects.filter(sku=OuterRef('sku')).values('product_title')[:1]
    product_vertical_subquery = master_sku.objects.filter(sku=OuterRef('sku')).values('product_vertical')[:1]

    sales_with_title = sales_data.annotate(
        consolidated_product_title=Coalesce(Subquery(product_title_subquery), Value("Unknown"), output_field=CharField()),
        product_sku=F('sku'),
        vertical=Coalesce(Subquery(product_vertical_subquery), Value("Unknown"), output_field=CharField())
    )

    # Aggregation based on consolidated_product_title
    sales_aggregation_by_title = sales_with_title.values('sku','consolidated_product_title').annotate(
        gmv=Cast(Sum('final_invoice_amount', filter=(Q(event_sub_type='Sale') | Q(event_sub_type='Return Cancellation'))), FloatField()),
        qty=Cast(Sum('item_quantity', filter=(Q(event_sub_type='Sale') | Q(event_sub_type='Return Cancellation'))), FloatField()),
    ).order_by('sku')

    # Aggregation based on vertical
    sales_aggregation_by_vertical = sales_with_title.values('vertical').annotate(
        vertical_gmv=Cast(Sum('final_invoice_amount', filter=(Q(event_sub_type='Sale') | Q(event_sub_type='Return Cancellation'))), FloatField()),
        vertical_qty=Cast(Sum('item_quantity', filter=(Q(event_sub_type='Sale') | Q(event_sub_type='Return Cancellation'))), FloatField()),
    ).order_by('vertical')

    
    """This is for account the returns that will be made in the coming 20 days from the end date"""

    # Extend the date range by 20 days
    extended_end_date = end_date + timedelta(days=45)

    # Get the OrderIDs where event_sub_type = "Sale" within the selected date range
    sale_order_ids = sales.objects.filter(
        event_sub_type="Sale",
        order_date__range=[start_date, end_date],
        product_title__icontains=brand.lower()
    ).values_list('order_id', flat=True)
    

    """Calculation for returns"""
    # Check for 'Return' event_sub_type for these OrderIDs within the extended range
    returned_orders = sales.objects.filter(
        order_id__in=sale_order_ids,
        event_sub_type="Return",
        order_date__range=[start_date, extended_end_date]
    ).values_list('order_id', flat=True)

    # Annotate sales data with product title, SKU
    returned_with_title = returned_orders.annotate(
        consolidated_product_title=Coalesce(Subquery(product_title_subquery), Value("Unknown"), output_field=CharField()),
        product_sku=F('sku')
    )

    # Annotate sales data with product title, SKU
    returned_with_vertical = returned_orders.annotate(
        vertical=Coalesce(Subquery(product_vertical_subquery), Value("Unknown"), output_field=CharField()),
        product_sku=F('sku')
    )

    # Aggregate details for returned SKUs
    return_aggregation_by_title = returned_with_title.values('sku', 'consolidated_product_title').annotate(
        returned_gmv=Cast(Sum('final_invoice_amount'), FloatField()),  # Sum of GMV
        returned_qty=Cast(Sum('item_quantity'), FloatField())  # Sum of quantities
    ).order_by('sku')  # Optional: Order by SKU for better readability
    
    # Aggregate details for returned SKUs
    return_aggregation_by_vertical = returned_with_vertical.values('vertical').annotate(
        returned_vertical_gmv=Cast(Sum('final_invoice_amount'), FloatField()),  # Sum of GMV
        returned_vertical_qty=Cast(Sum('item_quantity'), FloatField())  # Sum of quantities
    ).order_by('vertical')  # Optional: Order by SKU for better readability

    """This accounts for the cancellations that happened in the next 20 days from the end date"""
    """Calculation for cancellations"""
    cancellation_orders = sales.objects.filter(
        order_id__in=sale_order_ids,
        event_sub_type="Cancellation",
        order_date__range=[start_date, extended_end_date]
    ).values_list('order_id', flat=True)

    # Annotate sales data with product title, SKU
    cancellation_with_title = cancellation_orders.annotate(
        consolidated_product_title=Coalesce(Subquery(product_title_subquery), Value("Unknown"), output_field=CharField()),
        product_sku=F('sku')
    )

    # Annotate sales data with product title, SKU
    cancellation_with_vertical = cancellation_orders.annotate(
        vertical=Coalesce(Subquery(product_vertical_subquery), Value("Unknown"), output_field=CharField()),
        product_sku=F('sku')
    )

    # Aggregate details for returned SKUs
    cancelled_aggregation_by_title = cancellation_with_title.values('sku', 'consolidated_product_title').annotate(
        cancelled_gmv=Cast(Sum('final_invoice_amount'), FloatField()),  # Sum of GMV
        cancelled_qty=Cast(Sum('item_quantity'), FloatField())  # Sum of quantities
    ).order_by('sku')  # Optional: Order by SKU for better readability
    
    # Aggregate details for returned SKUs
    cancelled_aggregation_by_vertical = cancellation_with_vertical.values('vertical').annotate(
        cancelled_vertical_gmv=Cast(Sum('final_invoice_amount'), FloatField()),  # Sum of GMV
        cancelled_vertical_qty=Cast(Sum('item_quantity'), FloatField())  # Sum of quantities
    ).order_by('vertical')  # Optional: Order by SKU for better readability


    """For calculating the net gmv and qty both by vertical and by title"""

    # Convert QuerySets into dictionaries keyed by sku (for title-level) and vertical (for vertical-level)
    sales_title_dict = {record['sku']: record for record in sales_aggregation_by_title}
    sales_vertical_dict = {record['vertical']: record for record in sales_aggregation_by_vertical}

    return_title_dict = {record['sku']: record for record in return_aggregation_by_title}
    return_vertical_dict = {record['vertical']: record for record in return_aggregation_by_vertical}

    cancellation_title_dict = {record['sku']: record for record in cancelled_aggregation_by_title}
    cancellation_vertical_dict = {record['vertical']: record for record in cancelled_aggregation_by_vertical}

    # Get union of all SKUs and verticals
    all_title = set(sales_title_dict.keys()) | set(return_title_dict.keys()) | set(cancellation_title_dict.keys())
    all_vertical = set(sales_vertical_dict.keys()) | set(return_vertical_dict.keys()) | set(cancellation_vertical_dict.keys())

    # Calculate net sales by title (using SKU as key)
    net_sale_by_title = {}
    for sku in all_title:
        sales_record = sales_title_dict.get(sku, {})
        return_record = return_title_dict.get(sku, {})
        cancellation_record = cancellation_title_dict.get(sku, {})

        net_sale_by_title[sku] = {
            'net_gmv': (sales_record.get('gmv') or 0) - (return_record.get('returned_gmv') or 0) - (cancellation_record.get('cancelled_gmv') or 0),
            'net_qty': (sales_record.get('qty') or 0)- (return_record.get('returned_qty') or 0) - (cancellation_record.get('cancelled_qty') or 0),
            'consolidated_product_title': sales_record.get('consolidated_product_title', "Unknown")
        }

    # Calculate net sales by vertical
    net_sales_by_vertical = {}

    for vertical in all_vertical:
        sales_record = sales_vertical_dict.get(vertical, {})
        return_record = return_vertical_dict.get(vertical, {})
        cancellation_record = cancellation_vertical_dict.get(vertical, {})

        net_sales_by_vertical[vertical] = {
            'net_vertical_gmv': (sales_record.get('vertical_gmv') or 0) - (return_record.get('returned_vertical_gmv') or 0) - (cancellation_record.get('cancelled_vertical_gmv') or 0),
            'net_vertical_qty': (sales_record.get('vertical_qty') or 0) - (return_record.get('returned_vertical_qty') or 0) - (cancellation_record.get('cancelled_vertical_qty') or 0),
            'vertical': sales_record.get('vertical', vertical)
        }

    return {
        "sales_by_title":sales_aggregation_by_title,
        "sales_by_vertical":sales_aggregation_by_vertical,

        "return_by_title":return_aggregation_by_title,
        "return_by_vertical":return_aggregation_by_vertical,

        "cancellation_by_title":cancelled_aggregation_by_title,
        "cancellation_by_vertical":cancelled_aggregation_by_vertical,

        "net_sales_by_title":net_sale_by_title,
        "net_sales_by_vertical":net_sales_by_vertical
    }



def get_fk_insights(sales, ads, invoice, master_sku, cogs_vertical, return_data, seller, start_date, end_date):

    fk_insights = {}


    (display_gmv, display_qty, display_return_rev, display_return_qty, display_cancellation_rev, display_cancellation_qty, display_net_gmv, display_net_qty, display_shopsy_contribution, display_fbf_contribution, rto_percent, rtv_percent, miscellaneous_return_percent, courier_return, customer_return, miscellaneous_return,
    percent_change_gmv, percent_change_qty, percent_change_return_rev, percent_change_return_qty, percent_change_cancellation_rev, percent_change_cancellation_qty, percent_change_net_gmv, percent_change_net_qty, percent_change_shopsy_contribution, percent_change_fbf_contribution, _,
    _, _, _, _, _, _, _, _, _, _, prev_display_net_gmv) = Flipkart_sales_parameters(sales, return_data, start_date, end_date)

    # It depends upon brand to brand
    if (seller == 'TRI'):
        # it takes the report of FK Alpha
        (display_ads_spend, display_ctr, display_cpc, display_cvr, display_roi, percent_change_ads_spend, percent_change_ctr, 
            percent_change_cpc, percent_change_cvr, percent_change_roi, prev_display_ads_spend) = Flipkart_ads_parameters(ads, start_date, end_date)
        
        # display_ads_spend = display_ads_spend - wallet_redeem
        # prev_display_ads_spend = prev_display_ads_spend - prev_wallet_redeem
        display_ads_spend = display_ads_spend
    
    else:
        # it takes Ads report from FK Marketplace
        (display_ads_spend, display_ctr, display_cpc, display_cvr, display_roi, percent_change_ads_spend, percent_change_ctr, 
            percent_change_cpc, percent_change_cvr, percent_change_roi, prev_display_ads_spend) = Flipkart_MP_ads_parameters(ads, start_date, end_date)


    product_data = return_product_flipkart(sales, master_sku, start_date, end_date)

    sales_details_title = list(product_data['sales_by_title'].values(
        'sku', 'consolidated_product_title', 'gmv', 'qty'
    ))

    sales_details_vertical = list(product_data['sales_by_vertical'].values(
        'vertical', 'vertical_gmv', 'vertical_qty'
    ))

    return_details_title = list(product_data['return_by_title'].values(
        'sku', 'consolidated_product_title', 'returned_gmv', 'returned_qty'
    ))

    return_details_vertical = list(product_data['return_by_vertical'].values(
        'vertical', 'returned_vertical_gmv', 'returned_vertical_qty'
    ))

    cancelled_details_title = list(product_data['cancellation_by_title'].values(
        'sku', 'consolidated_product_title', 'cancelled_gmv', 'cancelled_qty'
    ))

    cancelled_details_vertical = list(product_data['cancellation_by_vertical'].values(
        'vertical', 'cancelled_vertical_gmv', 'cancelled_vertical_qty'
    ))

    net_sales_details_title = [
        {
            'sku': sku,
            'consolidated_product_title': details.get('consolidated_product_title'),
            'net_gmv': details.get('net_gmv'),
            'net_qty': details.get('net_qty')
        }
        for sku, details in product_data['net_sales_by_title'].items()
    ]

    net_sales_details_vertical = [
        {
            'vertical': vertical,
            'net_vertical_gmv': details.get('net_vertical_gmv'),
            'net_vertical_qty': details.get('net_vertical_qty')
        }
        for vertical, details in product_data['net_sales_by_vertical'].items()
    ]


    fk_insights = {

        # Metrics for the display
        "display_gross_revenue": round(display_gmv, 2), 
        "display_gross_units": round(display_qty, 2),
        "display_returned_amt": round(display_return_rev, 2),
        "display_returned_units": round(display_return_qty, 2),
        "display_net_revenue": round(display_net_gmv, 2),
        "display_net_units": round(display_net_qty, 2),
        "display_ads_spend": round(display_ads_spend, 2),
        "display_rto_return": round(courier_return, 2),
        "display_rtv_return": round(customer_return, 2),
        "display_misc_return": round(miscellaneous_return, 2),
        "display_cancellation_amt": round(display_cancellation_rev, 2),
        "display_cancellation_units": round(display_cancellation_qty, 2),
        
        
        "display_cvr": round(display_cvr, 2),
        "display_cpc": round(display_cpc, 2),
        "display_roas": round(display_roi, 2),
        "display_shopsy_contribution": round(display_shopsy_contribution, 2),
        "display_fbf_contribution": round(display_fbf_contribution, 2),
        "prev_display_net_revenue": round(prev_display_net_gmv, 2),
        "prev_display_ads_spend": round(prev_display_ads_spend, 2),
        "display_rto_percent": round(rto_percent, 2),
        "display_rtv_percent": round(rtv_percent, 2),
        "display_misc_return_percent": round(miscellaneous_return_percent, 2),
        

        # mentioning the percentage change of the metrices
        "percent_change_gross_revenue": percent_change_gmv,
        "percent_change_gross_units": percent_change_qty,
        "percent_change_returned_amt": percent_change_return_rev,
        "percent_change_returned_units": percent_change_return_qty,
        "percent_change_net_revenue": percent_change_net_gmv,
        "percent_change_net_units": percent_change_net_qty,
        "percent_change_ads_spend": percent_change_ads_spend,
        "percent_change_cpc": percent_change_cpc,
        "percent_change_roas": percent_change_roi,
        "percent_change_shopsy_contribution": percent_change_shopsy_contribution,
        "percent_change_fbf_contribution": percent_change_fbf_contribution,
        "percent_change_cancellation_amt": percent_change_cancellation_rev,
        "percent_change_cancellation_units": percent_change_cancellation_qty,
        "percent_change_cvr": percent_change_cvr,


        "sales_details_title": sales_details_title,
        "sales_details_vertical": sales_details_vertical,
        "return_details_title": return_details_title,
        "return_details_vertical": return_details_vertical,
        "cancelled_details_title": cancelled_details_title,
        "cancelled_details_vertical": cancelled_details_vertical,
        "net_sales_details_title": net_sales_details_title,
        "net_sales_details_vertical": net_sales_details_vertical

    }

    return fk_insights

"""------------------------------------------------This is for multi-brand feature----------------------------------------"""

def get_fk_insights_multi_brand(sales, ads, invoice, master_sku, cogs, return_data, brand, start_date, end_date):
    
    fk_insights = {}

    (display_gmv, display_qty, display_return_rev, display_return_qty, display_cancellation_rev, display_cancellation_qty, display_net_gmv, display_net_qty, display_shopsy_contribution, display_fbf_contribution, rto_percent, rtv_percent, miscellaneous_return_percent, courier_return, customer_return, miscellaneous_return,
    percent_change_gmv, percent_change_qty, percent_change_return_rev, percent_change_return_qty, percent_change_cancellation_rev, percent_change_cancellation_qty, percent_change_net_gmv, percent_change_net_qty, percent_change_shopsy_contribution, percent_change_fbf_contribution, _,
    _, _, _, _, _, _, _, _, _, _, display_prev_net_gmv) = Flipkart_multi_brand_sales(sales, return_data, brand, start_date, end_date)
    

    (display_ads_spend, display_ctr, display_cpc, display_cvr, display_roi,
                percent_change_ads_spend, percent_change_ctr, percent_change_cpc, percent_change_cvr, percent_change_roi, prev_display_ads_spend) = Flipkart_MP_ads_multi_brand(ads, brand, start_date, end_date)
    

    product_data = return_product_flipkart_multi_brand(sales, master_sku, brand, start_date, end_date)
    

    sales_details_title = list(product_data['sales_by_title'].values(
        'sku', 'consolidated_product_title', 'gmv', 'qty'
    ))

    sales_details_vertical = list(product_data['sales_by_vertical'].values(
        'vertical', 'vertical_gmv', 'vertical_qty'
    ))

    return_details_title = list(product_data['return_by_title'].values(
        'sku', 'consolidated_product_title', 'returned_gmv', 'returned_qty'
    ))

    return_details_vertical = list(product_data['return_by_vertical'].values(
        'vertical', 'returned_vertical_gmv', 'returned_vertical_qty'
    ))

    cancelled_details_title = list(product_data['cancellation_by_title'].values(
        'sku', 'consolidated_product_title', 'cancelled_gmv', 'cancelled_qty'
    ))

    cancelled_details_vertical = list(product_data['cancellation_by_vertical'].values(
        'vertical', 'cancelled_vertical_gmv', 'cancelled_vertical_qty'
    ))

    net_sales_details_title = [
        {
            'sku': sku,
            'consolidated_product_title': details.get('consolidated_product_title'),
            'net_gmv': details.get('net_gmv'),
            'net_qty': details.get('net_qty')
        }
        for sku, details in product_data['net_sales_by_title'].items()
    ]

    net_sales_details_vertical = [
        {
            'vertical': vertical,
            'net_vertical_gmv': details.get('net_vertical_gmv'),
            'net_vertical_qty': details.get('net_vertical_qty')
        }
        for vertical, details in product_data['net_sales_by_vertical'].items()
    ]


    fk_insights = {

        # Metrics for the display
        "display_gross_revenue": round(display_gmv, 2), # Just add while calculating overall_sales
        "display_gross_units": round(display_qty, 2), # Just add while calculating overall_sales
        "display_returned_amt": round(display_return_rev, 2), # Just add while calculating overall_sales
        "display_returned_units": round(display_return_qty, 2), # Just add while calculating overall_sales
        "display_net_revenue": round(display_net_gmv, 2), # Just add while calculating overall_sales
        "display_net_units": round(display_net_qty, 2), # Just add while calculating overall_sales
        "display_ads_spend": round(display_ads_spend, 2), # Just add while calculating overall_sales
        "display_rto_return": round(courier_return, 2), # Just add while calculating overall_sales
        "display_rtv_return": round(customer_return, 2), # Just add while calculating overall_sales
        "display_misc_return": round(miscellaneous_return, 2), # Just add while calculating overall_sales
        "display_cancellation_amt": round(display_cancellation_rev, 2), # Just add while calculating overall_sales
        "display_cancellation_units": round(display_cancellation_qty, 2), # Just add while calculating overall_sales
        
        
        "display_cvr": round(display_cvr, 2), 
        "display_cpc": round(display_cpc, 2),
        "display_roas": round(display_roi, 2),
        "display_shopsy_contribution": round(display_shopsy_contribution, 2),
        "display_fbf_contribution": round(display_fbf_contribution, 2),
        "prev_display_net_revenue": round(display_prev_net_gmv, 2), # Just add while calculating overall_sales
        "prev_display_ads_spend": round(prev_display_ads_spend, 2), # Just add while calculating overall_sales
        "display_rto_percent": round(rto_percent, 2),
        "display_rtv_percent": round(rtv_percent, 2),
        "display_misc_return_percent": round(miscellaneous_return_percent, 2),
        

        # mentioning the percentage change of the metrices
        "percent_change_gross_revenue": percent_change_gmv,
        "percent_change_gross_units": percent_change_qty,
        "percent_change_returned_amt": percent_change_return_rev,
        "percent_change_returned_units": percent_change_return_qty,
        "percent_change_net_revenue": percent_change_net_gmv,
        "percent_change_net_units": percent_change_net_qty,
        "percent_change_ads_spend": percent_change_ads_spend,
        "percent_change_cpc": percent_change_cpc,
        "percent_change_roas": percent_change_roi,
        "percent_change_shopsy_contribution": percent_change_shopsy_contribution,
        "percent_change_fbf_contribution": percent_change_fbf_contribution,
        "percent_change_cancellation_amt": percent_change_cancellation_rev,
        "percent_change_cancellation_units": percent_change_cancellation_qty,
        "percent_change_cvr": percent_change_cvr,

        "sales_details_title": sales_details_title,
        "sales_details_vertical": sales_details_vertical,
        "return_details_title": return_details_title,
        "return_details_vertical": return_details_vertical,
        "cancelled_details_title": cancelled_details_title,
        "cancelled_details_vertical": cancelled_details_vertical,
        "net_sales_details_title": net_sales_details_title,
        "net_sales_details_vertical": net_sales_details_vertical
        
    }

    return fk_insights





# This function is for a detailed summary of all the brands that are present on the Flipakrt platform
# This function is complete and works for all sorts of brands like 1st Step, Jr Sr and NexTen
def all_brand_Flipkart(start_date, end_date):

    final_dict = {}
    insights_dict = {}

    # Fetch insights dynamically for all brands
    for brand, models in brand_models.items():
        insights_dict[brand] = get_fk_insights(
            models['sales'], models['ads'], models['invoices'],
            models['master_sku'], models['cogs'], models['returns'], brand, start_date, end_date
        )

    # Extract the first 22 key-value pairs from each brand
    insights_list = [list(insights.items())[:36] for insights in insights_dict.values()]

    # Iterate over multiple brands dynamically
    for values in zip(*insights_list):
        print(f"Values of the loop: {values}")

        keys = [v[0] for v in values]  # Extract keys (they should be identical across brands)
        print(f"Keys: {keys}")
        values = [v[1] for v in values]  # Extract values
        print(f"Values: {values}")
        
        key = keys[0]  # Any key from the extracted list
        
        # The below code implementation is for the calculating the overall metrics for the given brands
        if any(substring in key for substring in ('cpc', 'roas', 'fbf_contribution', 'shopsy_contribution')):
            
            if 'percent_' in key:
                continue
            
            else:
                percent_change_key = 'percent_change_' + key.split('display_')[1]
                
                if 'cpc' in key:
                    
                    prev_cpc_values = [
                        Decimal(100) * Decimal(insights_dict[brand][key]) / (Decimal(insights_dict[brand][percent_change_key]) + Decimal(100))
                        for brand in brand_models.keys()
                    ]
                    current_clicks = [
                        Decimal(insights_dict[brand]['display_ads_spend']) / Decimal(insights_dict[brand][key])
                        for brand in brand_models.keys()
                    ]
                    prev_clicks = [
                        Decimal(insights_dict[brand]['prev_display_ads_spend']) / Decimal(val)
                        for brand, val in zip(brand_models.keys(), prev_cpc_values)
                    ]

                    total_ads_spend = sum(Decimal(insights_dict[brand]['display_ads_spend']) for brand in brand_models.keys())
                    total_prev_ads_spend = sum(Decimal(insights_dict[brand]['prev_display_ads_spend']) for brand in brand_models.keys())

                    overall_cpc = 0 if sum(current_clicks) == 0 else total_ads_spend / sum(current_clicks)
                    overall_prev_cpc = 0 if sum(prev_clicks) == 0 else total_prev_ads_spend / sum(prev_clicks)

                    overall_percent_change = round(((overall_cpc - overall_prev_cpc) * Decimal(100)) / overall_prev_cpc, 3) if overall_prev_cpc != 0 else Decimal(0)
                    
                    final_dict[key] = round(overall_cpc, 2)
                    final_dict[percent_change_key] = overall_percent_change

                elif 'roas' in key:
                    
                    prev_roas_value = [
                        Decimal(100) * Decimal(insights_dict[brand][key]) / (Decimal(insights_dict[brand][percent_change_key]) + Decimal(100))
                        for brand in brand_models.keys()
                    ]

                    current_ad_rev = [
                        Decimal(insights_dict[brand]['display_ads_spend']) * Decimal(insights_dict[brand][key])
                        for brand in brand_models.keys()
                    ]

                    prev_ad_rev = [
                        Decimal(insights_dict[brand]['prev_display_ads_spend']) * Decimal(val)
                        for brand, val in zip(brand_models.keys(), prev_roas_value)
                    ]

                    total_ads_spend = sum(Decimal(insights_dict[brand]['display_ads_spend']) for brand in brand_models.keys())
                    total_prev_ads_spend = sum(Decimal(insights_dict[brand]['prev_display_ads_spend']) for brand in brand_models.keys())

                    total_current_ad_rev = sum(current_ad_rev)
                    total_prev_ad_rev = sum(prev_ad_rev)

                    overall_roas = 0 if total_ads_spend == 0 else total_current_ad_rev / total_ads_spend
                    overall_prev_roas = 0 if total_prev_ads_spend == 0 else total_prev_ad_rev / total_prev_ads_spend

                    overall_percent_change = round(((overall_roas - overall_prev_roas) * Decimal(100)) / overall_prev_roas, 3) if overall_prev_roas != 0 else Decimal(0)

                    final_dict[key] = round(overall_roas, 2)
                    final_dict[percent_change_key] = overall_percent_change

                elif 'fbf_contribution' in key:
                    
                    current_fbf_sales = [
                        Decimal(insights_dict[brand][key]) * Decimal(insights_dict[brand]['display_net_revenue']) / Decimal(100)
                        for brand in brand_models.keys()
                    ]

                    prev_fbf_contri = [
                        Decimal(100) * Decimal(insights_dict[brand][key]) / (Decimal(insights_dict[brand][percent_change_key]) + Decimal(100))
                        for brand in brand_models.keys()
                    ]

                    prev_fbf_sales = [
                        Decimal(val) * Decimal(insights_dict[brand]['prev_display_net_revenue']) / Decimal(100)
                        for brand, val in zip(brand_models.keys(), prev_fbf_contri)
                    ]

                    overall_fbf_contri = sum(current_fbf_sales)*100/sum(Decimal(insights_dict[brand]['display_net_revenue']) for brand in brand_models.keys())
                    overall_prev_fbf_contri = sum(prev_fbf_sales)*100/sum(Decimal(insights_dict[brand]['prev_display_net_revenue']) for brand in brand_models.keys())

                    overall_percent_change = round(((overall_fbf_contri - overall_prev_fbf_contri) * Decimal(100)) / overall_prev_fbf_contri, 3) if overall_prev_fbf_contri != 0 else Decimal(0)

                    final_dict[key] = round(overall_fbf_contri, 2)
                    final_dict[percent_change_key] = overall_percent_change

                elif 'shopsy_contribution' in key:
                    
                    current_shopsy_sales = [
                        Decimal(insights_dict[brand][key]) * Decimal(insights_dict[brand]['display_net_revenue']) / Decimal(100)
                        for brand in brand_models.keys()
                    ]

                    prev_shopsy_contri = [
                        Decimal(100) * Decimal(insights_dict[brand][key]) / (Decimal(insights_dict[brand][percent_change_key]) + Decimal(100))
                        for brand in brand_models.keys()
                    ]

                    prev_shopsy_sales = [
                        Decimal(val) * Decimal(insights_dict[brand]['prev_display_net_revenue']) / Decimal(100)
                        for brand, val in zip(brand_models.keys(), prev_shopsy_contri)
                    ]

                    overall_shopsy_contri = sum(current_shopsy_sales)*100/sum(Decimal(insights_dict[brand]['display_net_revenue']) for brand in brand_models.keys())
                    overall_prev_shopsy_contri = sum(prev_shopsy_sales)*100/sum(Decimal(insights_dict[brand]['prev_display_net_revenue']) for brand in brand_models.keys())

                    overall_percent_change = round(((overall_shopsy_contri - overall_prev_shopsy_contri) * Decimal(100)) / overall_prev_shopsy_contri, 3) if overall_prev_shopsy_contri != 0 else Decimal(0)

                    final_dict[key] = round(overall_shopsy_contri, 2)
                    final_dict[percent_change_key] = overall_percent_change


        elif 'percent_' in key:
            # Calculate previous values dynamically
            current_key = 'display_' + key.split('percent_change_')[1]
            prev_values = [
                Decimal(100) * Decimal(insights_dict[brand][current_key]) / (Decimal(val) + Decimal(100))
                for brand, val in zip(brand_models.keys(), values)
            ]

            total_prev = sum(prev_values, Decimal(0))  # Ensures sum is computed correctly
            total_current = sum(Decimal(insights_dict[brand][current_key]) for brand in brand_models.keys())

            # Avoid division by zero
            overall_percent_change = (
                round(((total_current - total_prev) * Decimal(100)) / total_prev, 3) if total_prev != 0 else Decimal(0)
            )

            final_dict[key] = float(overall_percent_change)  # Convert back to float for output
        
        elif any(substring in key for substring in ('rto', 'rtv', 'miscellaneous_returns')):
            
            # Aggregating return metrics is sum of either 'rto', 'rtv', or 'miscellaneous_returns'
            # Don't get confused by total returns
            
            aggregated_returns = [
                Decimal(insights_dict[brand]['display_gross_units'])*Decimal(insights_dict[brand][key])/Decimal(100)
                for brand in brand_models.keys()
            ]

            total_aggregated_returns = sum(aggregated_returns)

            aggregated_qty = sum(Decimal(insights_dict[brand]['display_gross_units']) for brand in brand_models.keys())

            overall_percentage = total_aggregated_returns*100/aggregated_qty if aggregated_qty != 0 else Decimal(0)

            final_dict[key] = round(overall_percentage, 2)

        else:
            final_dict[key] = sum(values)  # Summing all brand values

    # Merging category-wise details dynamically
    category_keys = [
        "sales_details_title", "sales_details_vertical",
        "return_details_title", "return_details_vertical",
        "cancelled_details_title", "cancelled_details_vertical",
        "net_sales_details_title", "net_sales_details_vertical"
    ]

    for cat_key in category_keys:
        final_dict[cat_key] = sum((list(insights[cat_key]) for insights in insights_dict.values()), [])
    print(len(final_dict))
    return final_dict




# This function is complete and works for all sorts of brand like 1st Step, Jr Sr and NexTen
def all_brand_map_Flipkart(start_date, end_date):

    state_order_data = pd.DataFrame()

    # Process each brand dynamically
    # for brand, model in brands_config.items():
    for brand, models in brand_models.items():
        shipping_data = (
            models["sales"].objects
            .filter(order_date__range=[start_date, end_date])
            .values('customer_delivery_state')
            .annotate(total_quantity=Sum('item_quantity'))
            .order_by('total_quantity')
        )

        # Convert QuerySet to DataFrame
        brand_df = pd.DataFrame(list(shipping_data))

        # Rename column to avoid conflicts in merging
        if not brand_df.empty:
            brand_df.rename(columns={'total_quantity': f'total_quantity_{brand}'}, inplace=True)

            # Merge data dynamically
            if state_order_data.empty:
                state_order_data = brand_df
            else:
                state_order_data = pd.merge(
                    state_order_data, brand_df, on='customer_delivery_state', how='outer'
                )

    # Sum across all brands to get total quantity per state
    if not state_order_data.empty:
        quantity_columns = [col for col in state_order_data.columns if 'total_quantity_' in col]
        state_order_data['total_quantity'] = state_order_data[quantity_columns].sum(axis=1, min_count=1)

        # Keep only necessary columns
        state_order_data = state_order_data[['customer_delivery_state', 'total_quantity']]


    all_states = [
        "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh", "Goa", "Gujarat", 
        "Haryana", "Himachal Pradesh", "Jammu and Kashmir", "Jharkhand", "Karnataka", "Kerala", 
        "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram", "Nagaland", "Odisha", 
        "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana", "Tripura", "Uttar Pradesh", 
        "Uttarakhand", "West Bengal", "Andaman and Nicobar Islands", "Chandigarh", 
        "Dadra and Nagar Haveli and Daman and Diu", "Delhi", "Ladakh", "Lakshadweep", "Puducherry"
    ]


    df = state_order_data

    if df.empty:
        # Create a new DataFrame with all_states and total_quantity set to 0
        df = pd.DataFrame({
            'customer_delivery_state': all_states,
            'total_quantity': [0] * len(all_states)
        })

    # Fix naming issues and standardize
    state_replacements = {
        "Dadra & Nagar Haveli & Daman & Diu": "Dadra and Nagar Haveli and Daman and Diu",
        "Jammu & Kashmir": "Jammu and Kashmir",
        "Pondicherry": "Puducherry",
    }


    df["customer_delivery_state"] = df["customer_delivery_state"].replace(state_replacements)

    df = df[df["customer_delivery_state"] != "-"]

    # Get current states in the data
    current_states = set(df['customer_delivery_state'].unique())
    
    # Find missing states
    missing_states = set(all_states) - current_states
    
    # Add missing states with zero values
    if missing_states:
        missing_df = pd.DataFrame({
            'customer_delivery_state': list(missing_states),
            'total_quantity': [0] * len(missing_states)
        })
        df = pd.concat([df, missing_df], ignore_index=True)

    # Load the India GeoJSON
    with open("india.geojson", "r", encoding="utf-8") as f:
        india_geojson = json.load(f)

    # Convert to GeoDataFrame
    gdf = gpd.GeoDataFrame.from_features(india_geojson)
    
    # Dissolve districts into states
    gdf_dissolved = gdf.dissolve(by='st_nm', as_index=False)
    
    # Convert back to GeoJSON
    simplified_geojson = json.loads(gdf_dissolved.to_json())

    # Create the choropleth figure with simplified GeoJSON
    fig = go.Figure(data=go.Choropleth(
        geojson=simplified_geojson,
        locations=df['customer_delivery_state'],
        z=df['total_quantity'],
        locationmode='geojson-id',
        featureidkey='properties.st_nm',
        colorscale='Greens',
        colorbar=dict(
            title="Order Quantity",
            x=0.85,  # Shift color scale closer to the map
            y=0.5,   # Center color scale vertically
            ticks="outside"
        ),
        hovertemplate="<b>State: %{location}</b><br>" +
                      "Orders: %{z}<br><extra></extra>",
        showscale=True
    ))

    # Update the layout for better visualization
    fig.update_geos(
        visible=False,
        center=dict(lat=23.5937, lon=78.9629),  # Center of India
        projection_scale=5.5,  # Zoom into the map for a tighter fit
        showcoastlines=False,
        showframe=False,
        fitbounds="locations"  # Ensures the map tightly fits the data
    )

    fig.update_layout(
        title=dict(
            text='Order Distribution Across India',
            x=0.5,
            y=0.95
        ),
        geo=dict(
            scope='asia',
            showlakes=False,
            showcountries=False,
            subunitcolor='black',
            subunitwidth=1,
            showland=True,
            landcolor='white'
        ),
        margin=dict(r=0, t=0, l=0, b=0),  # Remove unnecessary margins
        height=500,  # Chart height
        width=600   # Chart width for a compact layout
    )

    return fig.to_json()


# This function is complete and works for all sorts of brand like 1st Step, Jr Sr and NexTen
def all_brand_pie_Flipkart(start_date, end_date):
    # Collect GMV data for all brands dynamically
    sales_data = []
    for seller, models in brand_models.items():
        
        gmv = models["sales"].objects.filter(order_date__range=[start_date, end_date]).aggregate(
            gmv=Sum(F('final_invoice_amount'))
        )['gmv'] or 0  # Handle None values by defaulting to 0
        
        sales_data.append({"seller": seller, "gmv": gmv})

    # Compute total GMV
    total_gmv = sum(item['gmv'] for item in sales_data if item['gmv'])

    # Calculate GMV proportions dynamically
    sales_data = [
        {
            'seller': item['seller'],
            'gmv': item['gmv'],
            'gmv_proportion': round((item['gmv'] * 100 / total_gmv), 2) if total_gmv else 0
        }
        for item in sales_data
    ]

    # Prepare data for the Plotly pie chart
    labels = [f"{item['seller']} ({item['gmv_proportion']}%)" for item in sales_data]
    sizes = [item['gmv'] for item in sales_data]

    # Create a Plotly pie chart
    fig = go.Figure(
        data=[
            go.Pie(
                labels=labels,
                values=sizes,
                textinfo='none',  # Disable text inside the pie chart
                hoverinfo='label+percent',  # Display label and percentage on hover
            )
        ]
    )

    # Update layout for the pie chart
    fig.update_layout(
        title="GMV Distribution by Seller",
        showlegend=True,
        legend_title="Seller",
        legend=dict(
            itemsizing="constant",
            orientation="v",
            x=1.1,  
            y=0.5,  
            xanchor="left",  
            bgcolor="rgba(255, 255, 255, 0)",  
        ),
        margin=dict(l=10, r=10, t=30, b=10),
        height=500,  
        width=600    
    )

    # Convert the Plotly figure to JSON
    return fig.to_json()


# This function is complete and works for all sorts of brand like 1st Step, Jr Sr and NexTen
def all_brand_dynamic_plot_Flipkart(start_date, end_date):
    import pandas as pd
    from plotly.subplots import make_subplots
    import plotly.graph_objects as go

    # Working on the Sales Data
    sales_dfs = []

    for brand, models in brand_models.items():
        # Fetch sales data dynamically for each brand
        sales_qs = models["sales"].objects.filter(order_date__range=[start_date, end_date]).values(
            'order_date', 'final_invoice_amount', 'item_quantity', 'event_sub_type'
        )

        sales_df = pd.DataFrame(list(sales_qs))

        if not sales_df.empty:
            # Filter only Sale & Return Cancellation events
            sales_df = sales_df[
                (sales_df['event_sub_type'] == 'Sale') | 
                (sales_df['event_sub_type'] == 'Return Cancellation')
            ]
            
            # Aggregate data per day
            sales_summary = sales_df.groupby('order_date').agg(
                gmv=('final_invoice_amount', 'sum'),
                qty=('item_quantity', 'sum')
            ).reset_index()

            sales_dfs.append(sales_summary)

    # Combine sales data from all brands
    combined_summary = pd.concat(sales_dfs, ignore_index=True) if sales_dfs else pd.DataFrame(columns=['order_date', 'gmv', 'qty'])

    # Step 2: Aggregate the combined data by order_date
    sales_agg = combined_summary.groupby('order_date').agg(
        gmv=('gmv', 'sum'),
        qty=('qty', 'sum')
    ).reset_index()

    sales_agg.rename(columns={'order_date': 'date'}, inplace=True)


    # Working on Ads Data
    ads_dfs = []

    for brand, models in brand_models.items():
        # Check if 'units_sold_direct' exists in the ads model (to annotate total_converted_units & total_revenue)
        if 'units_sold_direct' in [field.name for field in models["ads"]._meta.get_fields()]:
            ads_qs = models["ads"].objects.filter(date__range=[start_date, end_date]).annotate(
                total_converted_units=F('units_sold_direct') + F('units_sold_indirect'),
                total_revenue=F('direct_revenue') + F('indirect_revenue')
            ).values(
                'date', 'ad_spend', 'views', 'clicks', 'total_converted_units', 'total_revenue'
            )
        else:
            ads_qs = models["ads"].objects.filter(date__range=[start_date, end_date]).values(
                'date', 'ad_spend', 'views', 'clicks', 'total_converted_units', 'total_revenue'
            )

        ads_df = pd.DataFrame(list(ads_qs))

        if not ads_df.empty:
            ads_dfs.append(ads_df)

    # Combine ads data from all brands
    ads_dfs = pd.concat(ads_dfs, ignore_index=True) if ads_dfs else pd.DataFrame(columns=['date', 'ad_spend', 'views', 'clicks', 'total_converted_units', 'total_revenue'])

    print(ads_dfs.columns)
    print(ads_dfs)


    ads_agg = ads_dfs.groupby('date').agg(
        adSpend=('ad_spend', 'sum'),
        views=('views', 'sum'),
        revenue=('total_revenue', 'sum')
    ).reset_index()

    
    ads_agg['roi'] = ads_agg['revenue'] / ads_agg['adSpend']
    ads_agg['roi'].replace([float('inf'), -float('inf')], 0, inplace=True)  # Handle division by zero

    # Step 8: Define the plotting function
    def create_figure(df, metric, title):
        fig = make_subplots(rows=1, cols=1)
        fig.add_trace(go.Scatter(
            x=df['date'],
            y=df[metric],
            mode='lines+markers',
            marker=dict(size=8),
            line=dict(width=2),
            hoverinfo='x+y',
            name=metric.upper()
        ))
        fig.update_layout(
            title=title,
            xaxis=dict(title='Date', tickangle=45),
            yaxis=dict(title=metric.upper(), tickformat=".2f"),
            template='plotly_white',
            autosize=True,
            margin=dict(l=40, r=40, t=40, b=40)
        )
        return fig.to_json()

    # Step 9: Generate plots for GMV, Ad Spend, Quantity, Views, and ROI
    plots = {
        'gmv': create_figure(sales_agg, 'gmv', 'GMV vs Date'),
        'adsSpend': create_figure(ads_agg, 'adSpend', 'Ad Spend vs Date'),
        'qty': create_figure(sales_agg, 'qty', 'Quantity vs Date'),
        'views': create_figure(ads_agg, 'views', 'Views vs Date'),
        'roi': create_figure(ads_agg, 'roi', 'ROI vs Date')     
    }

    return {"dynamic_plot": plots}



"""--------------------Whatever code written here for Amazon is for the purpose of testing 
-----------------------(The final working code is written in the "data_analysis_amz.py")-------------------------"""

"""----------------------------------------For Amazon platform------------------------------------------"""
# This calculates the sales parameters for bot the single and multi-brand (This is complete)
def Amazon_sales_parameters(sales_data_model, return_data_model, brand=None, start_date=None, end_date=None):
    
    current_par = []
    prev_par = []
    percent_change = []

    for i in range(2):

        if i == 0:

            start_date_i = start_date
            end_date_i = end_date
            extended_date = end_date + timedelta(days=20)

            if brand != None:
                data_model = sales_data_model.objects.filter(invoice_date__range=[start_date_i, extended_date], item_description__icontains=brand.lower())
            else:    
                data_model = sales_data_model.objects.filter(invoice_date__range=[start_date_i, extended_date])


        else:

            # Setting it for previous n-days back for comparison
            delta = end_date_i - start_date_i
            end_date_i = start_date_i - timedelta(days=1)
            start_date_i = end_date_i - delta
            extended_date = end_date_i + timedelta(days=20)

            if brand != None:
                data_model = sales_data_model.objects.filter(invoice_date__range=[start_date_i, extended_date], item_description__icontains=brand.lower())
            else:
                data_model = sales_data_model.objects.filter(invoice_date__range=[start_date_i, extended_date])


            # This is for the display in cards
        display_gmv = data_model.filter(Q(transaction_type='Shipment'), invoice_date__range=[start_date_i, end_date_i]).aggregate(gmv=Sum(F('invoice_amount')))['gmv'] or 0
        display_qty = data_model.filter(Q(transaction_type='Shipment'), invoice_date__range=[start_date_i, end_date_i]).aggregate(qty=Sum(F('quantity')))['qty'] or 0
        
        sales_order_ids = data_model.filter(
            transaction_type="Shipment",
            invoice_date__range=[start_date_i, end_date_i]
        ).values_list('order_id', flat=True)

        return_order_ids = data_model.filter(
            order_id__in=sales_order_ids,
            transaction_type="Refund",
            invoice_date__range=[start_date_i, extended_date]
        ).values_list('order_id', flat=True)

        # Till here the code is fine for the simple and multi-brand account

        # Not applying the brand filter because the "Return Data" is very small so searching in the entire return data
        return_classification = return_data_model.objects.filter(
                order_id__in=OuterRef('order_id')
            ).annotate(
                classified_return=Case(
                    When(return_type='Amazon CS', then=Value('courier_return')),
                    When(return_type='C-Returns', then=Value('customer_return')),
                    When(return_type='Rejected', then=Value('courier_return')),
                    When(return_type='Undelivered', then=Value('courier_return')),
                    default=Value('miscellaneous returns'),
                    output_field=CharField(),
                )
            ).values('classified_return')

        return_quantity_subquery = return_data_model.objects.filter(
            order_id=OuterRef('order_id')
        ).values('order_id').annotate(
            total_return_qty=Sum('return_quantity'),
        ).values('total_return_qty')[:1]

        # 3. Use both in your main query
        sales_returns = sales_data_model.objects.filter(
            order_date__range=[start_date, extended_date],
            order_id__in=return_order_ids,
            transaction_type="Refund"
        ).annotate(
            classified_return=Coalesce(
                Subquery(return_classification),
                Value('miscellaneous returns')
            ),
            return_quantity=Coalesce(
                Subquery(return_quantity_subquery),
                Value(0),
                output_field=DecimalField()
            )
        )

        # 4. Final aggregation by classified_return
        return_result = sales_returns.values('classified_return').annotate(
            total_quantity=Sum('return_quantity')
        )
            
        print(f"return results {return_result}")

        # Build a dictionary mapping classification to its total quantity.
        return_totals = {entry['classified_return']: entry['total_quantity'] for entry in return_result}

        # Get each total; if missing, default to 0.
        courier_return = return_totals.get('courier_return', 0)
        customer_return = return_totals.get('customer_return', 0)
        miscellaneous_return = return_totals.get('miscellaneous returns', 0)   

        print(f"start_date {start_date} and end_date {end_date}")
        print(f"courier return: {courier_return}")
        print(f"customer return: {customer_return}")
        print(f"miscellaneous return: {miscellaneous_return}")


        display_return_rev = data_model.filter(order_id__in=return_order_ids, invoice_date__range=[start_date_i, extended_date], transaction_type="Refund").aggregate(return_rev=Sum(F('invoice_amount')))['return_rev'] or 0
        display_return_qty = data_model.filter(order_id__in=return_order_ids, invoice_date__range=[start_date_i, extended_date], transaction_type="Refund").aggregate(return_qty=Sum(F('quantity')))['return_qty'] or 0
        
        cancellation_ids = data_model.filter(order_id__in=sales_order_ids, invoice_date__range=[start_date_i, extended_date], transaction_type="Cancel").values_list('order_id', flat=True)
        display_cancellation_qty = data_model.filter(order_id__in=cancellation_ids, invoice_date__range=[start_date_i, extended_date], transaction_type="Cancel").aggregate(cancellation_qty=Sum(F('quantity')))['cancellation_qty'] or 0
        
        # This approach is used because the Invoive Amount in case of cancellation is 0, so we are looking for the cancelled order id and then picking their amount from their to get the cancellation amount
        display_cancellation_rev = data_model.filter(order_id__in=cancellation_ids, invoice_date__range=[start_date_i, extended_date], transaction_type="Shipment").aggregate(cancellation_rev=Sum(F('invoice_amount')))['cancellation_rev'] or 0
        
        rto_percent = 0 if (display_qty == 0 and miscellaneous_return == 0) else round(courier_return * 100/(display_qty - miscellaneous_return), 2)
        rtv_percent = 0 if (display_qty == 0 and display_cancellation_qty == 0 and courier_return == 0) else round((customer_return) * 100/(display_qty - display_cancellation_qty - courier_return), 2)
        miscellaneous_return_percent = 0 if display_qty == 0 else round(miscellaneous_return * 100 / display_qty, 2)

        # Added the display_return_rev because its already negative
        display_net_gmv = display_gmv + display_return_rev - display_cancellation_rev
        display_net_qty = display_qty - display_return_qty - display_cancellation_qty

        # fulfilment channel
        afn_sales = data_model.filter(Q(transaction_type='Shipment') & Q(fulfillment_channel='AFN'), invoice_date__range=[start_date_i, end_date_i]).aggregate(afn_gmv=Sum(F('invoice_amount')))['afn_gmv'] or 0
        afn_contribution = 0 if display_gmv == 0 else round(afn_sales*100/display_gmv, 2)
        print(f"AFN contribution: {afn_contribution}")

        if i == 0: current_par.extend([display_gmv, display_qty, display_return_rev, display_return_qty, display_cancellation_qty, display_cancellation_rev, display_net_gmv, display_net_qty, afn_contribution, rto_percent, rtv_percent, miscellaneous_return_percent, courier_return, customer_return, miscellaneous_return])
        else: prev_par.extend([display_gmv, display_qty, display_return_rev, display_return_qty, display_cancellation_qty, display_cancellation_rev, display_net_gmv, display_net_qty, afn_contribution, rto_percent, rtv_percent, miscellaneous_return_percent, courier_return, customer_return, miscellaneous_return])

    # calculating the percentage change
    for i, j in zip(current_par, prev_par):
        percentage_change = 0 if j == 0 else (i - j)*100/j
        percent_change.append(percentage_change)

    # PnL is sorted for the single brand and multi-brand account
    # Resetting the data model for PnL calculation table

    if brand != None:
        data_model = sales_data_model.objects.filter(invoice_date__range=[start_date, end_date], item_description__icontains=brand.lower())
    else:
        data_model = sales_data_model.objects.filter(invoice_date__range=[start_date, end_date])

    gmv = data_model.filter(Q(transaction_type='Shipment')).aggregate(gmv=Sum(F('invoice_amount')))['gmv'] or 0
    qty = data_model.filter(Q(transaction_type='Shipment')).aggregate(qty=Sum(F('quantity')))['qty'] or 0


    # this tracks all the returns and cancellation that were came in that date range  basically its the summary of the sales tax report (irrespective of the order date)
    return_rev = data_model.filter(transaction_type='Refund').aggregate(return_rev=Sum(F('invoice_amount')))['return_rev'] or 0
    return_qty = data_model.filter(transaction_type='Refund').aggregate(return_qty=Sum(F('quantity')))['return_qty'] or 0

    cancellation_qty = data_model.filter(transaction_type='Cancel').aggregate(cancellation_qty=Sum(F('quantity')))['cancellation_qty'] or 0
    
    # The below logic is for cancellation revenue purpose for only the PnL table purpose
    overall_cancelled_id = data_model.filter(
        transaction_type = 'Cancel'
    ).values_list('order_id', flat=True)
    
    pre_start_date = start_date - timedelta(days=45)

    cancellation_rev = sales_data_model.objects.filter(order_id__in=overall_cancelled_id, invoice_date__range=[pre_start_date, end_date], transaction_type='Shipment').aggregate(cancellation_rev=Sum(F('invoice_amount')))['cancellation_rev'] or 0

    # added the return_rev because return_rev is already negative
    net_gmv = gmv + return_rev - cancellation_rev
    net_qty = qty - return_qty - cancellation_qty

    net_gmv_without_tax = data_model.aggregate(net_gmv_wtax=Sum(F('tax_exclusive_gross')))['net_gmv_wtax'] or 0

    tax = net_gmv - net_gmv_without_tax

    return (current_par[0], current_par[1], current_par[2], current_par[3], current_par[4], current_par[5], current_par[6], current_par[7], current_par[8], current_par[9], current_par[10], current_par[11], current_par[12], current_par[13], current_par[14],
            gmv, qty, return_rev, return_qty, cancellation_rev, cancellation_qty, net_gmv, net_qty, net_gmv_without_tax, tax,
            percent_change[0], percent_change[1], percent_change[2], percent_change[3], percent_change[4], percent_change[5], percent_change[6], percent_change[7], percent_change[8])
    


# This field calculates the CODB costs for single as well as the multi-brand account
def Amazon_fees_parameters(fee_data_model, master_sku, brand=None, start_date=None, end_date=None):

    if brand != None:

        # This first filter out those ASIN that are associated with the given brand, not the all brand ASIN
        brand_specific_asin = master_sku.objects.filter(product_title__icontain=brand.lower()).values_list('asin', flat=True)

        # here we are applying filter on Fee_data_model for only those ASINs which are associated with that brand
        fee_data_model = fee_data_model.objects.filter(asin__in=brand_specific_asin)

    else:
        fee_data_model = fee_data_model.objects.all()


    start_month = start_date.month
    end_month = end_date.month

    delta_days = (end_date - start_date).days

    delta_month = end_month - start_month

    total_days_in_account = (delta_month+1)*30

    # This handel's the case when there is change of year occur between the start and end date 
    # (and especially when the start month is greater than the end month)
    if start_month > end_month:

        weight_handeling_fee = (
            fee_data_model.objects
            .annotate(month=ExtractMonth('end_date'))
            .filter(Q(month__gte=start_month) | Q(month__lte=end_month))  # Match months in two ranges
            .aggregate(weight_handeling_fee=Sum(F('fba_weight_handling_fee_total')))
            .get('weight_handeling_fee', 0)
        ) or 0

        fixed_closing_fee = (
            fee_data_model.objects
            .annotate(month=ExtractMonth('end_date'))
            .filter(Q(month__gte=start_month) | Q(month__lte=end_month))
            .aggregate(fixed_closing_fee=Sum(F('fixed_closing_fee_total')))
            .get('fixed_closing_fee', 0)
        ) or 0

        referral_fee = (
            fee_data_model.objects
            .annotate(month=ExtractMonth('end_date'))
            .filter(Q(month__gte=start_month) | Q(month__lte=end_month))
            .aggregate(referral_fee=Sum(F('referral_fee_total')))
            .get('referral_fee', 0)
        ) or 0

        refund_commission_fee = (
            fee_data_model.objects
            .annotate(month=ExtractMonth('end_date'))
            .filter(Q(month__gte=start_month) | Q(month__lte=end_month))
            .aggregate(refund_commission_fee=Sum(F('refund_commission_fee_total')))
            .get('refund_commission_fee', 0)
        ) or 0

    else:  
        # Normal case
        weight_handeling_fee = (
            fee_data_model.objects
            .annotate(month=ExtractMonth('end_date'))
            .filter(month__gte=start_month, month__lte=end_month)
            .aggregate(weight_handeling_fee=Sum(F('fba_weight_handling_fee_total')))
            .get('weight_handeling_fee', 0)
        ) or 0

        fixed_closing_fee = (
            fee_data_model.objects
            .annotate(month=ExtractMonth('end_date'))
            .filter(month__gte=start_month, month__lte=end_month)
            .aggregate(fixed_closing_fee=Sum(F('fixed_closing_fee_total')))
            .get('fixed_closing_fee', 0)
        ) or 0

        referral_fee = (
            fee_data_model.objects
            .annotate(month=ExtractMonth('end_date'))
            .filter(month__gte=start_month, month__lte=end_month)
            .aggregate(referral_fee=Sum(F('referral_fee_total')))
            .get('referral_fee', 0)
        ) or 0

        refund_commission_fee = (
            fee_data_model.objects
            .annotate(month=ExtractMonth('end_date'))
            .filter(month__gte=start_month, month__lte=end_month)
            .aggregate(refund_commission_fee=Sum(F('refund_commission_fee_total')))
            .get('refund_commission_fee', 0)
        ) or 0


    weight_handeling_fee = 0 if total_days_in_account == 0 else weight_handeling_fee*delta_days/total_days_in_account
    fixed_closing_fee = 0 if total_days_in_account == 0 else fixed_closing_fee*delta_days/total_days_in_account
    referral_fee = 0 if total_days_in_account == 0 else referral_fee*delta_days/total_days_in_account
    refund_commission_fee = 0 if total_days_in_account == 0 else refund_commission_fee*delta_days/total_days_in_account


    return weight_handeling_fee, fixed_closing_fee, referral_fee, refund_commission_fee


# This calculates the Ads parameters (SB, SD and SP) [Cannot be calculated for a particular brand in multiseller, because there is no mention of Brand name in the Campaign Name]
def Amazon_Ads_parameters(sb_data_model, sd_data_model, sp_data_model, start_date=None, end_date=None):

    current_par = []
    prev_par = []
    percent_change = []

    for i in range(2):
        
        if i == 0:

            start_date_i = start_date
            end_date_i = end_date

        else:
            
            delta = end_date_i - start_date_i
            end_date_i = start_date_i - timedelta(days=1)
            start_date_i = end_date_i - delta


        # considering SB Ads
        sb_data = sb_data_model.objects.filter(date__range=[start_date_i, end_date_i])

        sb_ads_spend = sb_data.aggregate(ads_spend=Sum(F('spend')))['ads_spend'] or 0
        sb_ads_rev = sb_data.aggregate(ads_rev=Sum(F('day_14_total_sales')))['ads_rev'] or 0

        sb_ads_clicks = sb_data.aggregate(clicks=Sum(F('clicks')))['clicks'] or 0
        sb_ads_impressions = sb_data.aggregate(impressions=Sum(F('impressions')))['impressions'] or 0
        sb_ads_orders = sb_data.aggregate(orders=Sum(F('day_14_total_orders')))['orders'] or 0

        sb_ads_cpc = 0 if sb_ads_spend == 0 else sb_ads_spend / sb_ads_clicks
        sb_ads_ctr = 0 if sb_ads_impressions == 0 else sb_ads_clicks / sb_ads_impressions
        sb_ads_cvr = 0 if sb_ads_clicks == 0 else sb_ads_orders / sb_ads_clicks
        sb_ads_roas = 0 if sb_ads_spend == 0 else sb_ads_rev / sb_ads_spend
        
        # print(f"SB ads spend {sb_ads_spend}")

        # considering SD Ads
        sd_data = sd_data_model.objects.filter(date__range=[start_date_i, end_date_i])

        sd_ads_spend = sd_data.aggregate(ads_spend=Sum(F('spend')))['ads_spend'] or 0
        sd_ads_rev = sd_data.aggregate(ads_rev=Sum(F('day_14_total_sales')))['ads_rev'] or 0
        
        sd_ads_clicks = sd_data.aggregate(clicks=Sum(F('clicks')))['clicks'] or 0
        sd_ads_impressions = sd_data.aggregate(impressions=Sum(F('impressions')))['impressions'] or 0
        sd_ads_orders = sd_data.aggregate(orders=Sum(F('day_14_total_orders')))['orders'] or 0

        sd_ads_cpc = 0 if sd_ads_clicks == 0 else sd_ads_spend / sd_ads_clicks
        sd_ads_cvr = 0 if sd_ads_clicks == 0 else sd_ads_orders / sd_ads_clicks
        sd_ads_ctr = 0 if sd_ads_impressions == 0 else sd_ads_clicks / sd_ads_impressions
        sd_ads_roas = 0 if sd_ads_spend == 0 else sd_ads_rev/sd_ads_spend
    

        # considering SP Ads
        sp_data = sp_data_model.objects.filter(date__range=[start_date_i, end_date_i])
        
        sp_ads_spend = sp_data.aggregate(ads_spend=Sum(F('spend')))['ads_spend'] or 0
        sp_ads_rev = sp_data.aggregate(ads_rev=Sum(F('day_14_total_sales')))['ads_rev'] or 0
        
        sp_ads_clicks = sp_data.aggregate(clicks=Sum(F('clicks')))['clicks'] or 0
        sp_ads_impressions = sp_data.aggregate(impressions=Sum(F('impressions')))['impressions'] or 0
        sp_ads_orders = sp_data.aggregate(orders=Sum(F('day_14_total_orders')))['orders'] or 0

        sp_ads_roas = 0 if sp_ads_spend == 0 else sp_ads_rev / sp_ads_spend 
        sp_ads_cpc = 0 if sp_ads_clicks == 0 else sp_ads_spend / sp_ads_clicks
        sp_ads_ctr = 0 if sp_ads_impressions == 0 else sp_ads_clicks / sp_ads_impressions
        sp_ads_cvr = 0 if sp_ads_clicks == 0 else sp_ads_orders / sp_ads_clicks


        # calculating overall Ads parameters
        ads_spend = sb_ads_spend + sd_ads_spend + sp_ads_spend
        ads_rev = sb_ads_rev + sd_ads_rev + sp_ads_rev

        ads_clicks = sb_ads_clicks + sd_ads_clicks + sp_ads_clicks
        ads_impressions = sb_ads_impressions + sd_ads_impressions + sp_ads_impressions
        ads_orders = sb_ads_orders + sd_ads_orders + sp_ads_orders

        ads_roas = 0 if ads_spend == 0 else ads_rev / ads_spend
        ads_cpc = 0 if ads_clicks == 0 else ads_spend / ads_clicks
        ads_ctr = 0 if ads_impressions == 0 else ads_clicks / ads_impressions
        ads_cvr = 0 if ads_clicks == 0 else ads_orders / ads_clicks

        if i == 0:
            current_par.extend([sb_ads_spend, sb_ads_rev, sb_ads_roas, sb_ads_cpc, sb_ads_ctr, sb_ads_cvr,
            sd_ads_spend, sd_ads_rev, sd_ads_roas, sd_ads_cpc, sd_ads_ctr, sd_ads_cvr, 
            sp_ads_spend, sp_ads_rev, sp_ads_roas, sp_ads_cpc, sp_ads_ctr, sp_ads_cvr,
            ads_spend, ads_rev, ads_roas, ads_cpc, ads_ctr, ads_cvr])
        
        else:
            prev_par.extend([sb_ads_spend, sb_ads_rev, sb_ads_roas, sb_ads_cpc, sb_ads_ctr, sb_ads_cvr,
            sd_ads_spend, sd_ads_rev, sd_ads_roas, sd_ads_cpc, sd_ads_ctr, sd_ads_cvr, 
            sp_ads_spend, sp_ads_rev, sp_ads_roas, sp_ads_cpc, sp_ads_ctr, sp_ads_cvr,
            ads_spend, ads_rev, ads_roas, ads_cpc, ads_ctr, ads_cvr])
    
    for i, j in zip(current_par, prev_par):
        percentage_change = (i - j) * 100 / j if j != 0 else 0
        percent_change.append(percentage_change)

    return (current_par[0], current_par[1], current_par[2], current_par[3], current_par[4], current_par[5],
            current_par[6], current_par[7], current_par[8], current_par[9], current_par[10], current_par[11],
            current_par[12], current_par[13], current_par[14], current_par[15], current_par[16], current_par[17],
            current_par[18], current_par[19], current_par[20], current_par[21], current_par[22], current_par[23],
            percent_change[0], percent_change[1], percent_change[2], percent_change[3], percent_change[4], percent_change[5],
            percent_change[6], percent_change[7], percent_change[8], percent_change[9], percent_change[10], percent_change[11],
            percent_change[12], percent_change[13], percent_change[14], percent_change[15], percent_change[16], percent_change[17],
            percent_change[18], percent_change[19], percent_change[20], percent_change[21], percent_change[22], percent_change[23],)



# # For making the line plot of the different trends such as gmv, ads_spend etc
# # This works for both the single as well as the multi-brand seller account

def get_dynamic_plot_AMZ(sales, sb_ads, sd_ads, sp_ads, brand, start_date, end_date):
    import pandas as pd
    from plotly.subplots import make_subplots
    import plotly.graph_objects as go
    from django.db.models import Sum, Q
    from django.db.models.functions import Cast
    from django.db.models import FloatField
    from itertools import chain
    from collections import defaultdict

    # --------------------------
    # Query Sales Data (for gmv and qty)
    # --------------------------
    if brand == "":
        sales_data = sales.objects.filter(invoice_date__range=[start_date, end_date])
    else:
        sales_data = sales.objects.filter(
            invoice_date__range=[start_date, end_date],
            item_description__icontains=brand.lower()
        )

    # Define sales aggregations
    data_aggregation_sales = {
        'gmv': Sum('invoice_amount', filter=(Q(transaction_type='Shipment'))),
        'qty': Sum('quantity', filter=(Q(transaction_type='Shipment'))),
    }

    figures = {}

    # Helper function to create a Plotly figure
    def create_figure(df, metric):
        fig = make_subplots(rows=1, cols=1)
        fig.add_trace(go.Scatter(
            x=df['date'],
            y=df['total_metric'],
            mode='lines+markers',
            marker=dict(size=8),
            line=dict(width=2),
            hoverinfo='x+y',
            name=metric.upper()
        ))
        fig.update_layout(
            title=f'{metric.upper()} vs Date',
            xaxis=dict(title='Date', tickangle=45),
            yaxis=dict(title=metric.upper(), tickformat=".2f"),
            template='plotly_white',
            autosize=True,
            margin=dict(l=40, r=40, t=40, b=40)
        )
        return fig.to_json()

    # Generate sales plots (gmv and qty)
    for graph_type, aggregation in data_aggregation_sales.items():
        aggregated_data = (
            sales_data.values('invoice_date')
            .annotate(total_metric=Cast(aggregation, FloatField()))
            .order_by('invoice_date')
        )
        df = pd.DataFrame(list(aggregated_data))
        df.rename(columns={'invoice_date': 'date'}, inplace=True)
        if df.empty:
            df = pd.DataFrame({'date': [start_date], 'total_metric': [0]})
        figures[graph_type] = create_figure(df, graph_type)

    # --------------------------
    # Combine Ads Data (from sb_ads, sd_ads, sp_ads) for views, adsSpend, and ads_rev
    # --------------------------
    # Query each ads model. If a brand filter is applied, use it.
    if brand == "":
        sb_qs = sb_ads.objects.filter(date__range=[start_date, end_date])
        sd_qs = sd_ads.objects.filter(date__range=[start_date, end_date])
        sp_qs = sp_ads.objects.filter(date__range=[start_date, end_date])
    else:
        sb_qs = sb_ads.objects.filter(
            date__range=[start_date, end_date],
            campaign_name__icontains=brand.lower()
        )
        sd_qs = sd_ads.objects.filter(
            date__range=[start_date, end_date],
            campaign_name__icontains=brand.lower()
        )
        sp_qs = sp_ads.objects.filter(
            date__range=[start_date, end_date],
            campaign_name__icontains=brand.lower()
        )

    # Annotate each queryset by grouping on 'date'
    sb_data = sb_qs.values('date').annotate(views=Sum('impressions'), adsSpend=Sum('spend'), ads_rev=Sum('day_14_total_sales'))
    sd_data = sd_qs.values('date').annotate(views=Sum('impressions'), adsSpend=Sum('spend'), ads_rev=Sum('day_14_total_sales'))
    sp_data = sp_qs.values('date').annotate(views=Sum('impressions'), adsSpend=Sum('spend'), ads_rev=Sum('day_14_total_sales'))

    # Combine the three datasets
    combined_ads = list(chain(sb_data, sd_data, sp_data))

    # Group results by date and sum the ads metrics
    grouped_ads = defaultdict(lambda: {'views': 0, 'adsSpend': 0, 'ads_rev': 0})
    for record in combined_ads:
        record_date = record['date']
        grouped_ads[record_date]['views'] += record.get('views') or 0
        grouped_ads[record_date]['adsSpend'] += record.get('adsSpend') or 0
        grouped_ads[record_date]['ads_rev'] += record.get('ads_rev') or 0

    # Convert grouped results to a sorted list of dictionaries
    ads_results = [
        {'date': date, 'views': data['views'], 'adsSpend': data['adsSpend'], 'ads_rev': data['ads_rev']}
        for date, data in grouped_ads.items()
    ]
    ads_results.sort(key=lambda x: x['date'])

    # Convert ads results to DataFrame once and use it for plotting ads metrics
    df_ads = pd.DataFrame(ads_results)
    print(df_ads)

    # Create plots for ads metrics: views and adsSpend
    for metric in ['views', 'adsSpend']:
        if df_ads.empty:
            df_temp = pd.DataFrame({'date': [start_date], 'total_metric': [0]})
        else:
            df_temp = df_ads.copy()
            df_temp['total_metric'] = df_temp[metric]
        figures[metric] = create_figure(df_temp, metric)
    
    # --------------------------
    # Calculate and Plot ROI (ads_rev / adsSpend)
    # --------------------------
    if df_ads.empty:
        df_roi = pd.DataFrame({'date': [start_date], 'total_metric': [0]})
    else:
        df_roi = df_ads.copy()
        # Calculate ROI safely: if adsSpend is zero, ROI is set to 0
        df_roi['total_metric'] = df_roi.apply(
            lambda row: row['ads_rev'] / row['adsSpend'] if row['adsSpend'] != 0 else 0, axis=1
        )
    figures['roi'] = create_figure(df_roi, 'roi')

    return {"dynamic_plot": figures}




# This works for both single and multi-brand accounts
def demographic_plot_AMZ(sales, brand, start_date, end_date):
    
    # Query sales data within the date range
    # state_order_data = (
    #     sales.objects
    #     .filter(invoice_date__range=[start_date, end_date])
    #     .values('ship_to_state')
    #     .annotate(total_quantity=Sum('quantity'))
    #     .order_by('quantity')
    # )

    if brand == "":

        state_order_data = (
            sales.objects
            .filter(invoice_date__range=[start_date, end_date])
            .values('ship_to_state')
            .annotate(total_quantity=Sum('quantity'))
            .order_by('quantity')
        )

    else:
        state_order_data = (
            sales.objects
            .filter(invoice_date__range=[start_date, end_date], item_description__icontains=brand.lower())
            .values('ship_to_state')
            .annotate(total_quantity=Sum('quantity'))
            .order_by('quantity')
        )

    # Complete list of all Indian states and union territories
    all_states = [
        "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh", "Goa", "Gujarat",
        "Haryana", "Himachal Pradesh", "Jammu and Kashmir", "Jharkhand", "Karnataka", "Kerala",
        "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram", "Nagaland", "Odisha",
        "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana", "Tripura", "Uttar Pradesh",
        "Uttarakhand", "West Bengal", "Andaman and Nicobar Islands", "Chandigarh",
        "Dadra and Nagar Haveli and Daman and Diu", "Delhi", "Ladakh", "Lakshadweep", "Puducherry"
    ]
    df = pd.DataFrame(list(state_order_data))

    if df.empty:

        df = pd.DataFrame({
            'ship_to_state': all_states,
            'total_quantity': [0] * len(all_states)
        })


    # Function to capitalize the first letter of every word and make 'AND' lowercase
    def format_ship_to_state(state):
        words = state.split()
        return ' '.join([word.capitalize() if word != "AND" else "and" for word in words])

    # Apply the function to the 'ship_to_state' column
    df['ship_to_state'] = df['ship_to_state'].apply(format_ship_to_state)

    # Find missing states and add them with zero quantity
    current_states = set(df['ship_to_state'].unique())
    missing_states = set(all_states) - current_states

    if missing_states:
        missing_df = pd.DataFrame({
            'ship_to_state': list(missing_states),
            'total_quantity': [0] * len(missing_states)
        })
        df = pd.concat([df, missing_df], ignore_index=True)

    # Load the India GeoJSON
    with open("india.geojson", "r", encoding="utf-8") as f:
        india_geojson = json.load(f)

    # Convert to GeoDataFrame and dissolve districts into states
    gdf = gpd.GeoDataFrame.from_features(india_geojson)
    gdf_dissolved = gdf.dissolve(by='st_nm', as_index=False)
    simplified_geojson = json.loads(gdf_dissolved.to_json())

    # Create the choropleth figure
    fig = go.Figure(data=go.Choropleth(
        geojson=simplified_geojson,
        locations=df['ship_to_state'],
        z=df['total_quantity'],
        locationmode='geojson-id',
        featureidkey='properties.st_nm',
        colorscale='Greens',
        colorbar=dict(
            title="Order Quantity",
            x=0.85,  # Shift color scale closer to the map
            y=0.5,   # Center color scale vertically
            ticks="outside"
        ),
        hovertemplate="<b>State: %{location}</b><br>" +
                      "Orders: %{z}<br><extra></extra>",
        showscale=True
    ))

    # Update the layout for better visualization
    fig.update_geos(
        visible=False,
        center=dict(lat=23.5937, lon=78.9629),  # Center of India
        projection_scale=5.5,  # Zoom into the map for a tighter fit
        showcoastlines=False,
        showframe=False,
        fitbounds="locations"  # Ensures the map tightly fits the data
    )

    fig.update_layout(
        title=dict(
            text='Order Distribution Across India',
            x=0.5,
            y=0.95
        ),
        geo=dict(
            scope='asia',
            showlakes=False,
            showcountries=False,
            subunitcolor='black',
            subunitwidth=1,
            showland=True,
            landcolor='white'
        ),
        margin=dict(r=0, t=0, l=0, b=0),  # Remove unnecessary margins
        height=500,  # Chart height
        width=600   # Chart width for a compact layout
    )

    return fig.to_json()

# This works for both single and multi-brand seller account
def pie_chart_AMZ(sales_data, master_sku, brand, start_date, end_date):

    if brand == "":
        sales_data = sales_data.objects.filter(invoice_date__range=[start_date, end_date])
    else:
        sales_data = sales_data.objects.filter(product_title__icontains=brand.lower(), invoice_date__range=[start_date, end_date])

    # Subqueries for product title and vertical
    product_title_subquery = master_sku.objects.filter(sku=OuterRef('sku')).values('product_title')[:1]
    product_vertical_subquery = master_sku.objects.filter(sku=OuterRef('sku')).values('product_vertical')[:1]

    # Annotate sales data with product title and vertical
    sales_with_title = sales_data.annotate(
        consolidated_product_title=Coalesce(Subquery(product_title_subquery), Value("Unknown"), output_field=CharField()),
        product_sku=F('sku'),
        vertical=Coalesce(Subquery(product_vertical_subquery), Value("Unknown"), output_field=CharField())
    )

    # Aggregate GMV by vertical
    sales_aggregation_by_vertical = sales_with_title.values('vertical').annotate(
        gmv=Cast(Sum('invoice_amount', filter=(Q(transaction_type='Shipment'))), FloatField())
    ).order_by('vertical')

    # Calculate total GMV
    total_gmv = sum(item['gmv'] for item in sales_aggregation_by_vertical if item['gmv'])

    # Add GMV proportions for each vertical
    sales_aggregation_with_proportions = [
        {
            'vertical': item['vertical'],
            'gmv': item['gmv'],
            'gmv_proportion': round(((item['gmv'] or 0) * 100 / total_gmv), 2) if total_gmv else 0  # Avoid division by zero
        }
        for item in sales_aggregation_by_vertical
    ]

    # Prepare data for the Plotly pie chart
    labels = [
        f"{item['vertical']} ({item['gmv_proportion']}%)"
        for item in sales_aggregation_with_proportions
    ]
    sizes = [item['gmv'] for item in sales_aggregation_with_proportions]

    # Create a Plotly pie chart without annotations inside the chart
    fig = go.Figure(
        data=[
            go.Pie(
                labels=labels,
                values=sizes,
                textinfo='none',  # Disable text on the pie chart
                hoverinfo='label+percent',  # Display label and percentage on hover
                # marker=dict(line=dict(color='black', width=1))  # Outline the slices
            )
        ]
    )

    # Update layout for the pie chart with extra top margin for title spacing
    fig.update_layout(
        title="GMV Distribution by Vertical",
        title_y=0.95,  # Adjust title position slightly down
        showlegend=True,
        legend_title="Verticals",
        legend=dict(
            itemsizing="constant",
            orientation="v",  # Vertical orientation for the legend
            x=1.1,  # Adjust this to move the legend closer to the pie chart
            y=0.5,  # Center the legend vertically
            xanchor="left",  # Anchor the legend closer to the pie chart
            bgcolor="rgba(255, 255, 255, 0)",  # Transparent background
        ),
        margin=dict(
            l=10,  # Left margin
            r=10,  # Right margin
            t=60,  # Increased top margin for title spacing
            b=10   # Bottom margin
        ),
        height=500,  # Adjust chart height
        width=600    # Adjust chart width
    )

    # Convert the Plotly figure to JSON
    return fig.to_json()



# As of now this represents the consolidated product level and vertical level data on the given order date, not the transaction date
def return_product_AMZ(sales, master_sku, brand, start_date, end_date):

    """This for accounting the sales that happend in the selected date range for the given brand"""
    if brand == "":
        sales_data = sales.objects.filter(invoice_date__range=[start_date, end_date])
    else:
        sales_data = sales.objects.filter(invoice_date__range=[start_date, end_date], item_description__icontains=brand.lower())
    

    product_title_subquery = master_sku.objects.filter(sku=OuterRef('sku')).values('product_title')[:1]
    product_vertical_subquery = master_sku.objects.filter(sku=OuterRef('sku')).values('product_vertical')[:1]


    """Calculation for sales"""
    sales_with_title = sales_data.annotate(
        consolidated_product_title=Coalesce(Subquery(product_title_subquery), Value("Unknown"), output_field=CharField()),
        product_sku=F('sku'),
        vertical=Coalesce(Subquery(product_vertical_subquery), Value("Unknown"), output_field=CharField())
    )

    # Aggregation based on consolidated_product_title
    sales_aggregation_by_title = sales_with_title.values('sku','consolidated_product_title').annotate(
        gmv=Cast(Sum('invoice_amount', filter=(Q(transaction_type='Shipment'))), FloatField()),
        qty=Cast(Sum('quantity', filter=(Q(transaction_type='Shipment'))), FloatField()),
    ).order_by('sku')

    # Aggregation based on vertical
    sales_aggregation_by_vertical = sales_with_title.values('vertical').annotate(
        vertical_gmv=Cast(Sum('invoice_amount', filter=(Q(transaction_type='Shipment'))), FloatField()),
        vertical_qty=Cast(Sum('quantity', filter=(Q(transaction_type='Shipment'))), FloatField()),
    ).order_by('vertical')

    
    """This is for account the returns that will be made in the coming 20 days from the end date"""

    # Extend the date range by 20 days
    extended_end_date = end_date + timedelta(days=45)

    # Get the OrderIDs where event_sub_type = "Sale" within the selected date range
    sale_order_ids = sales_data.filter(
        transaction_type="Shipment",
        invoice_date__range=[start_date, end_date]
    ).values_list('order_id', flat=True)

    """Calculation for returns"""
    # Check for 'Return' event_sub_type for these OrderIDs within the extended range
    returned_orders = sales.objects.filter(
        order_id__in=sale_order_ids,
        transaction_type="Refund",
        invoice_date__range=[start_date, extended_end_date]
    ).values_list('order_id', flat=True)

    # Annotate sales data with product title, SKU
    returned_with_title = returned_orders.annotate(
        consolidated_product_title=Coalesce(Subquery(product_title_subquery), Value("Unknown"), output_field=CharField()),
        product_sku=F('sku')
    )

    # Annotate sales data with product title, SKU
    returned_with_vertical = returned_orders.annotate(
        vertical=Coalesce(Subquery(product_vertical_subquery), Value("Unknown"), output_field=CharField()),
        product_sku=F('sku')
    )

    # Aggregate details for returned SKUs
    return_aggregation_by_title = returned_with_title.values('sku', 'consolidated_product_title').annotate(
        returned_gmv=Cast(Sum('invoice_amount'), FloatField()),  # Sum of GMV
        returned_qty=Cast(Sum('quantity'), FloatField())  # Sum of quantities
    ).order_by('sku')  # Optional: Order by SKU for better readability
    
    # Aggregate details for returned SKUs
    return_aggregation_by_vertical = returned_with_vertical.values('vertical').annotate(
        returned_vertical_gmv=Cast(Sum('invoice_amount'), FloatField()),  # Sum of GMV
        returned_vertical_qty=Cast(Sum('quantity'), FloatField())  # Sum of quantities
    ).order_by('vertical')  # Optional: Order by SKU for better readability

    """This accounts for the cancellations that happened in the next 20 days from the end date"""

    cancellation_orders = sales.objects.filter(
        order_id__in=sale_order_ids,
        transaction_type="Cancel",
        invoice_date__range=[start_date, extended_end_date]
    ).values_list('order_id', flat=True)
    
    # This is to make a query such that to get the mapping of order ids and the corresponding transaction_type as Shipment
    shipment_for_cancelled_orders = sales.objects.filter(
        order_id__in=cancellation_orders,
        transaction_type="Shipment"
    )



    """Calculation for cancellations"""
    # # Annotate sales data with product title, SKU
    cancellation_with_title = shipment_for_cancelled_orders.annotate(
        consolidated_product_title=Coalesce(Subquery(product_title_subquery), Value("Unknown"), output_field=CharField()),
        product_sku=F('sku')
    )


    # Annotate sales data with product title, SKU
    cancellation_with_vertical = shipment_for_cancelled_orders.annotate(
        vertical=Coalesce(Subquery(product_vertical_subquery), Value("Unknown"), output_field=CharField()),
        product_sku=F('sku')
    )

    # # Aggregate details for returned SKU by Title
    cancelled_aggregation_by_title = cancellation_with_title.values('sku', 'consolidated_product_title').annotate(
        cancelled_gmv=Cast(Sum('invoice_amount'), FloatField()),
        cancelled_qty=Cast(Sum('quantity'), FloatField())
    ).order_by('sku')

    
    # Aggregate details for returned SKU by Vertical
    cancelled_aggregation_by_vertical = cancellation_with_vertical.values('vertical').annotate(
        cancelled_vertical_gmv=Cast(Sum('invoice_amount'), FloatField()),  # Sum of GMV
        cancelled_vertical_qty=Cast(Sum('quantity'), FloatField())  # Sum of quantities
    ).order_by('vertical')  # Optional: Order by SKU for better readability


    """For calculating the net gmv and qty both by vertical and by title"""

    # Convert QuerySets into dictionaries keyed by sku (for title-level) and vertical (for vertical-level)
    sales_title_dict = {record['sku']: record for record in sales_aggregation_by_title}
    sales_vertical_dict = {record['vertical']: record for record in sales_aggregation_by_vertical}

    return_title_dict = {record['sku']: record for record in return_aggregation_by_title}
    return_vertical_dict = {record['vertical']: record for record in return_aggregation_by_vertical}

    cancellation_title_dict = {record['sku']: record for record in cancelled_aggregation_by_title}
    cancellation_vertical_dict = {record['vertical']: record for record in cancelled_aggregation_by_vertical}

    # Get union of all SKUs and verticals
    all_title = set(sales_title_dict.keys()) | set(return_title_dict.keys()) | set(cancellation_title_dict.keys())
    all_vertical = set(sales_vertical_dict.keys()) | set(return_vertical_dict.keys()) | set(cancellation_vertical_dict.keys())

    # Calculate net sales by title (using SKU as key)
    net_sale_by_title = {}
    for sku in all_title:
        sales_record = sales_title_dict.get(sku, {})
        return_record = return_title_dict.get(sku, {})
        cancellation_record = cancellation_title_dict.get(sku, {})

        # print(sales_record.get('gmv', 0))
        # print(return_record.get('returned_gmv', 0))
        
        net_sale_by_title[sku] = {
            'net_gmv': (sales_record.get('gmv') or 0) - (return_record.get('returned_gmv') or 0) - (cancellation_record.get('cancelled_gmv') or 0),
            'net_qty': (sales_record.get('qty') or 0) - (return_record.get('returned_qty') or 0) - (cancellation_record.get('cancelled_qty') or 0),
            'consolidated_product_title': sales_record.get('consolidated_product_title', "Unknown")
        }

    # Calculate net sales by vertical
    net_sales_by_vertical = {}
    for vertical in all_vertical:
        sales_record = sales_vertical_dict.get(vertical, {})
        return_record = return_vertical_dict.get(vertical, {})
        cancellation_record = cancellation_vertical_dict.get(vertical, {})

        net_sales_by_vertical[vertical] = {
            'net_vertical_gmv': (sales_record.get('vertical_gmv') or 0) - (return_record.get('returned_vertical_gmv') or 0),
            'net_vertical_qty': (sales_record.get('vertical_qty') or 0) - (return_record.get('returned_vertical_qty') or 0) - (cancellation_record.get('cancelled_vertical_qty') or 0),
            'vertical': sales_record.get('vertical', vertical)
        }


    return {
        "sales_by_title":sales_aggregation_by_title,
        "sales_by_vertical":sales_aggregation_by_vertical,

        "return_by_title":return_aggregation_by_title,
        "return_by_vertical":return_aggregation_by_vertical,

        "cancellation_by_title":cancelled_aggregation_by_title,
        "cancellation_by_vertical":cancelled_aggregation_by_vertical,

        "net_sales_by_title":net_sale_by_title,
        "net_sales_by_vertical":net_sales_by_vertical
    }


# Calculating the COGS for the Brand on Amazon platform
def cogs_calculation(sales_data, cogs_vertical, start_date, end_date):
    
    # ------approach------
    # This functions looks up for every "SKU" that is present in Sales data, into "COGS and Vertical" data
    # for COGS related to that "SKU" and then multiplies it with the item_quantity and that's how cogs is taken into account 

    # As of now I am not not deducting the COGS of cancellation from the Gross sales because the cancellation amount is not present in the Sales data
    # We can map the Cancellation amount by using the Invoice ID of Sales made (Make sure to impelement this thing in the Sales parameter and COGS both)

    # Apply date filter to sales data
    if start_date and end_date:
        sales = sales_data.objects.filter(invoice_date__range=[start_date, end_date])
    else:
        sales = sales_data.objects.all()

    # Subquery for COGS and Vertical data from the 'cogs_vertical' model
    cogs_vertical_subquery = cogs_vertical.objects.filter(sku=OuterRef('sku')).values('cogs')[:1]

    # Annotate sales data with Vertical and COGS values, and calculate total COGS for each item
    sales_with_data = sales.annotate(
        COGS=Coalesce(Subquery(cogs_vertical_subquery), Value(0), output_field=DecimalField(max_digits=10, decimal_places=2))
    ).annotate(
        total_cogs=F('COGS') * F('quantity')  # Multiply COGS by quantity
    )

    # Calculate COGS for different event types
    sales_cogs = sales_with_data.filter(transaction_type='Shipment').aggregate(sales_cogs=Sum('total_cogs'))['sales_cogs'] or 0
    return_cogs = sales_with_data.filter(transaction_type='Refund').aggregate(return_cogs=Sum('total_cogs'))['return_cogs'] or 0
    # cancellation_cogs = sales_with_data.filter(event_sub_type='Cancellation').aggregate(total_cogs=Sum('total_cogs'))['total_cogs'] or 0

    # Calculate the total COGS
    cogs = sales_cogs - return_cogs

    return cogs


# Amazon PnL parameters calculations
def Amazon_PnL_parameters(sales_data, cogs_vertical, fees_data, sb_ads_data, sd_ads_data, sp_ads_data, return_data, brand, master_sku, start_date, end_date):
    
    (_, _, _, _, _, _, _, _, _, _, _, _, _,
    _, _, gmv, qty, return_rev, return_qty, cancellation_rev, cancellation_qty, net_gmv, net_qty, net_gmv_without_tax, tax, _, _, 
    _, _, _, _, _, _, _) = Amazon_sales_parameters(sales_data, return_data, brand, start_date, end_date)

    # CODB insights
    weight_handeling_fee, fixed_closing_fee, referral_fee, refund_commission_fee = Amazon_fees_parameters(fees_data, master_sku, brand, start_date, end_date)

    # COGS details
    cogs = cogs_calculation(sales_data, cogs_vertical, start_date, end_date)

    # Ads Insights
    (_, _, _, _, _, _,
        _, _, _, _, _, _,
        _, _, _, _, _, _,
        ads_spend, _, _, _, _, _,
        _, _, _, _, _, _,
        _, _, _, _, _, _,
        _, _, _, _, _, _,
        _, _, _, _, _, _) = Amazon_Ads_parameters(sb_ads_data, sd_ads_data, sp_ads_data, start_date, end_date)
    
    operations = 0

    codb = float(weight_handeling_fee) + float(fixed_closing_fee) + float(referral_fee)
    net_revenue_with_tax = float(net_gmv) + float(refund_commission_fee)
    net_revenue_without_tax = float(net_revenue_with_tax) - float(tax)
    product_margin = float(net_revenue_without_tax) - float(cogs)
    cm1 = float(product_margin) + float(codb)
    cm2 = float(cm1) - float(operations)
    cm3 = float(cm2) - float(ads_spend)
    profit_percentage = 0 if net_revenue_with_tax == 0 else float(cm3)*100/float(net_revenue_without_tax)
    
    results = [round(float(value), 2) for value in [
        gmv, qty, cancellation_rev, cancellation_qty, return_rev, return_qty, refund_commission_fee,
        net_revenue_with_tax, net_qty, -tax, net_gmv_without_tax, -cogs, product_margin, -codb,
        -weight_handeling_fee, -fixed_closing_fee, -referral_fee,
        cm1, -operations, cm2, -ads_spend, cm3, profit_percentage
    ]]
    
    return results


# This function is for processing the PnL parameters (This is done, make sure that you add "brand" as the parameter in the views.py)
def Amazon_PnL_calculator(start_date, end_date, time_format, seller, brand):

    no_of_days = (end_date - start_date).days + 1
    no_of_weeks = no_of_days//7 + 1
    no_of_months = no_of_days//30 + 1

    results = [0] * 32

    pnl_details = {}

    # For seeing the Pnl day-wise
    if time_format == 'day':
        
        start_date_i = start_date
        end_date_i = start_date

        for i in range(1, no_of_days+1):
            
            if end_date_i > end_date:
                break
            
            sub_final = []

            if seller != 'All Seller':
                data_model = amazon_brand_models[seller]
                results = Amazon_PnL_parameters(
                    data_model["sales"],
                    data_model["cogs"],
                    data_model["codb_fees"],
                    data_model["sb_ads"],
                    data_model["sd_ads"],
                    data_model["sp_ads"],
                    brand,
                    data_model["master_sku"],
                    start_date_i,
                    end_date_i
                )
            else:
                # This is for calculating the PnL parameters
                for data_model in amazon_brand_models:
                    sub_final = Amazon_PnL_parameters(
                        amazon_brand_models[data_model]["sales"],
                        amazon_brand_models[data_model]["cogs"],
                        amazon_brand_models[data_model]["codb_fees"],
                        amazon_brand_models[data_model]["sb_ads"],
                        amazon_brand_models[data_model]["sd_ads"],
                        amazon_brand_models[data_model]["sp_ads"],
                        brand,
                        amazon_brand_models[data_model]["master_sku"],
                        start_date_i,
                        end_date_i
                    )

                    results = [a + b for a,b in zip(sub_final, results)]
            
            # Convert string to datetime object
            # start_i = start_date_i
            start_i = start_date_i.date()

            pnl_details[f"{start_i}"] = results
            
            results = [0] * 32

            start_date_i = end_date_i + timedelta(1)
            end_date_i = start_date_i
            
        return pnl_details

    # For seeing the PnL week-wise
    elif time_format == 'week':
        
        if no_of_weeks == 1:
            start_date_i = start_date
            end_date_i = end_date

        else:
            start_date_i = start_date
            end_date_i = start_date + timedelta(6)

        for i in range(1, no_of_weeks+1):

            if end_date_i > end_date or start_date_i > end_date_i:
                break

            sub_final = []

            if seller != 'All Seller':
                data_model = amazon_brand_models[seller]
                results = Amazon_PnL_parameters(
                    data_model["sales"],
                    data_model["cogs"],
                    data_model["codb_fees"],
                    data_model["sb_ads"],
                    data_model["sd_ads"],
                    data_model["sp_ads"],
                    brand,
                    data_model["master_sku"],
                    start_date_i,
                    end_date_i
                )
            else:
                for data_model in amazon_brand_models:
                    sub_final = Amazon_PnL_parameters(
                        amazon_brand_models[data_model]["sales"],
                        amazon_brand_models[data_model]["cogs"],
                        amazon_brand_models[data_model]["codb_fees"],
                        amazon_brand_models[data_model]["sb_ads"],
                        amazon_brand_models[data_model]["sd_ads"],
                        amazon_brand_models[data_model]["sp_ads"],
                        brand,
                        amazon_brand_models[data_model]["master_sku"],
                        start_date_i,
                        end_date_i
                    )

                    results = [a + b for a,b in zip(sub_final, results)]
            
            # this is for running in the actual code base
            start_i = start_date_i.date()
            end_i = end_date_i.date()
            # This is for running in the run_analysis file
            # start_i = start_date_i
            # end_i = end_date_i


            pnl_details[f"{start_i}_to_{end_i}"] = results
            
            results = [0] * 32

            start_date_i = end_date_i + timedelta(1)

            if ((no_of_days - i*7) >= 7):
                end_date_i = start_date_i + timedelta(6)
            elif (no_of_days - i*7 > 0):
                end_date_i = start_date_i + timedelta(no_of_days - i*7 - 1)
            
        return pnl_details

    # For seeing the PnL month-wise
    elif time_format == "month":

        if no_of_months == 1:
            start_date_i = start_date
            end_date_i = end_date

        else:
            start_date_i = start_date
            end_date_i = start_date + timedelta(29)
        
        for i in range(1, no_of_months+1):

            if end_date_i > end_date or start_date_i > end_date_i:
                break

            sub_final = []

            if seller != 'All Seller':
                data_model = amazon_brand_models[seller]
                results = Amazon_PnL_parameters(
                    data_model["sales"],
                    data_model["cogs"],
                    data_model["codb_fees"],
                    data_model["sb_ads"],
                    data_model["sd_ads"],
                    data_model["sp_ads"],
                    brand,
                    data_model["master_sku"],
                    start_date_i,
                    end_date_i
                )
            else:
                for data_model in amazon_brand_models:
                    sub_final = Amazon_PnL_parameters(
                        amazon_brand_models[data_model]["sales"],
                        amazon_brand_models[data_model]["cogs"],
                        amazon_brand_models[data_model]["codb_fees"],
                        amazon_brand_models[data_model]["sb_ads"],
                        amazon_brand_models[data_model]["sd_ads"],
                        amazon_brand_models[data_model]["sp_ads"],
                        brand,
                        amazon_brand_models[data_model]["master_sku"],
                        start_date_i,
                        end_date_i
                    )

                    results = [a + b for a,b in zip(sub_final, results)]

            # This is for running in actual code base
            start_i = start_date_i.date()
            end_i = end_date_i.date()
            # the below is for running in the run_analysis file
            # start_i = start_date_i
            # end_i = end_date_i
            

            pnl_details[f"{start_i}_to_{end_i}"] = results

            results = [0] * 32

            start_date_i = end_date_i + timedelta(1)

            if ((no_of_days - i*30) >= 30):
                end_date_i = start_date_i + timedelta(29)
            elif (no_of_days - i*30 > 0):
                end_date_i = start_date_i + timedelta(no_of_days - i*30 - 1)

        return pnl_details
        
    else:

        start_date_i = start_date
        end_date_i = end_date

        if seller != 'All Seller':
                data_model = amazon_brand_models[seller]
                results = Amazon_PnL_parameters(
                    data_model["sales"],
                    data_model["cogs"],
                    data_model["codb_fees"],
                    data_model["sb_ads"],
                    data_model["sd_ads"],
                    data_model["sp_ads"],
                    brand,
                    data_model["master_sku"],
                    start_date_i,
                    end_date_i
                )
        else:
            for data_model in amazon_brand_models:
                sub_final = Amazon_PnL_parameters(
                    amazon_brand_models[data_model]["sales"],
                    amazon_brand_models[data_model]["cogs"],
                    amazon_brand_models[data_model]["codb_fees"],
                    amazon_brand_models[data_model]["sb_ads"],
                    amazon_brand_models[data_model]["sd_ads"],
                    amazon_brand_models[data_model]["sp_ads"],
                    brand,
                    amazon_brand_models[data_model]["master_sku"],
                    start_date_i,
                    end_date_i
                )

                results = [a + b for a,b in zip(sub_final, results)]

        # This is for running in the actual code base
        start_i = start_date_i.date()
        end_i = end_date_i.date()
        # This is for running in the run_analysis file
        # start_i = start_date_i
        # end_i = end_date_i
            

        pnl_details[f"{start_i}_to_{end_i}"] = results

        return pnl_details
    



def get_AMZ_insights(sales_data, fees_data, sb_ads_data, sd_ads_data, sp_ads_data, master_sku, cogs, returns_data, brand, start_date=None, end_date=None):

    # delta_days = end_date - start_date
    # prev_end_date = start_date - timedelta(days=1)
    # prev_start_date = prev_end_date - delta_days
    
    # insights dictionary
    amz_insights = {}

    # sales insights (This is complete as per the Flipkart current view)
    (display_gmv, display_qty, display_return_gmv, display_return_qty, display_cancelled_qty, display_cancelled_rev, display_net_gmv,
        display_net_qty, display_afn_contribution, rto_percent, rtv_percent, miscellaneous_return_percent, courier_return, customer_return, miscellaneous_return, gmv, qty, return_rev, return_qty, cancellation_rev, cancellation_qty, net_gmv, net_qty, net_gmv_without_tax, tax, display_gmv_percent, display_qty_percent, 
        display_return_gmv_percent, display_return_qty_percent, display_cancelled_qty_percent, display_cancelled_rev_percent, display_net_gmv_percent, 
        display_net_qty_percent, display_afn_contribution_percent) = Amazon_sales_parameters(sales_data, returns_data, brand, start_date, end_date)
    
    # Ads Insights
    (sb_ads_spend, sb_ads_rev, sb_ads_roas, sb_ads_cpc, sb_ads_ctr, sb_ads_cvr,
        sd_ads_spend, sd_ads_rev, sd_ads_roas, sd_ads_cpc, sd_ads_ctr, sd_ads_cvr, 
        sp_ads_spend, sp_ads_rev, sp_ads_roas, sp_ads_cpc, sp_ads_ctr, sp_ads_cvr,
        ads_spend, ads_rev, ads_roas, ads_cpc, ads_ctr, ads_cvr,

        percent_change_sb_ads_spend, percent_change_sb_ads_rev, percent_change_sb_ads_roas, percent_change_sb_ads_cpc, percent_change_sb_ads_ctr, percent_change_sb_ads_cvr,
        percent_change_sd_ads_spend, percent_change_sd_ads_rev, percent_change_sd_ads_roas, percent_change_sd_ads_cpc, percent_change_sd_ads_ctr, percent_change_sd_ads_cvr,
        percent_change_sp_ads_spend, percent_change_sp_ads_rev, percent_change_sp_ads_roas, percent_change_sp_ads_cpc, percent_change_sp_ads_ctr, percent_change_sp_ads_cvr,
        percent_change_ads_spend, percent_change_ads_rev, percent_change_ads_roas, percent_change_ads_cpc, percent_change_ads_ctr, percent_change_ads_cvr,) = Amazon_Ads_parameters(sb_ads_data, sd_ads_data, sp_ads_data, start_date, end_date)
    
    # product level details
    product_data = return_product_AMZ(sales_data, master_sku, brand, start_date, end_date)

    sales_details_title = list(product_data['sales_by_title'].values(
        'sku', 'consolidated_product_title', 'gmv', 'qty'
    ))

    sales_details_vertical = list(product_data['sales_by_vertical'].values(
        'vertical', 'vertical_gmv', 'vertical_qty'
    ))

    return_details_title = list(product_data['return_by_title'].values(
        'sku', 'consolidated_product_title', 'returned_gmv', 'returned_qty'
    ))

    return_details_vertical = list(product_data['return_by_vertical'].values(
        'vertical', 'returned_vertical_gmv', 'returned_vertical_qty'
    ))

    cancelled_details_title = list(product_data['cancellation_by_title'].values(
        'sku', 'consolidated_product_title', 'cancelled_qty'
    ))

    cancelled_details_vertical = list(product_data['cancellation_by_vertical'].values(
        'vertical', 'cancelled_vertical_qty'
    ))

    net_sales_details_title = [
        {
            'sku': sku,
            'consolidated_product_title': details.get('consolidated_product_title'),
            'net_gmv': details.get('net_gmv'),
            'net_qty': details.get('net_qty')
        }
        for sku, details in product_data['net_sales_by_title'].items()
    ]

    net_sales_details_vertical = [
        {
            'vertical': vertical,
            'net_vertical_gmv': details.get('net_vertical_gmv'),
            'net_vertical_qty': details.get('net_vertical_qty')
        }
        for vertical, details in product_data['net_sales_by_vertical'].items()
    ]

    amz_insights = {
        
        # first for the cards
        "display_gross_revenue": display_gmv,
        "display_gross_units": display_qty,
        "display_returned_amt": -1*display_return_gmv,
        "display_returned_units": display_return_qty,
        "display_net_revenue": display_net_gmv,
        "display_net_units": display_net_qty,
        "display_cancellation_amt": display_cancelled_rev,
        "display_cancellation_units": display_cancelled_qty,
        "display_ads_spend": round(ads_spend, 2),
        "display_rto_percent": round(rto_percent, 2),
        "display_rtv_percent": round(rtv_percent, 2),
        "display_misc_return_percent": round(miscellaneous_return_percent, 2),
        "display_rto_return": round(courier_return, 2),
        "display_rtv_return": round(customer_return, 2),
        "display_misc_return": round(miscellaneous_return, 2),
        "display_roas": round(ads_roas, 2),
        "display_cpc": round(ads_cpc, 2),
        "display_cvr": round(ads_cvr, 2),
        "display_ctr": round(ads_ctr, 2),
        "display_afn_contribution": display_afn_contribution,

        # change in the percentage for the cards
        "percent_change_gross_revenue": display_gmv_percent,
        "percent_change_gross_units": display_qty_percent,
        "percent_change_returned_amt": display_return_gmv_percent,
        "percent_change_returned_units": display_return_qty_percent,
        "percent_change_net_revenue": display_net_gmv_percent,
        "percent_change_net_units": display_net_qty_percent,
        "percent_change_cancellation_amt": display_cancelled_rev_percent,
        "percent_change_cancellation_units": display_cancelled_qty_percent,
        "percent_change_ads_spend": percent_change_ads_spend,
        "percent_change_roas": percent_change_ads_roas,
        "percent_change_cpc": percent_change_ads_cpc,
        "percent_change_cvr": percent_change_ads_cvr,
        "percent_change_ctr": percent_change_ads_ctr,
        "percent_change_afn_contribution": display_afn_contribution_percent,
        

        # verify then move to other files for taking it to the frontend

        "sales_details_title": sales_details_title,
        "sales_details_vertical": sales_details_vertical,
        "return_details_title": return_details_title,
        "return_details_vertical": return_details_vertical,
        "cancelled_details_title": cancelled_details_title,
        "cancelled_details_vertical": cancelled_details_vertical,
        "net_sales_details_title": net_sales_details_title,
        "net_sales_details_vertical": net_sales_details_vertical

    }

    return amz_insights

