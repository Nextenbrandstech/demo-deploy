from django.db.models import OuterRef, Subquery, F, Value, DecimalField, CharField, DateField
from django.db.models.functions import Coalesce, TruncDate, Abs, Cast, ExtractMonth
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from django.db.models import Q, Sum, F, FloatField, ExpressionWrapper, Count, Case, When, Value
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


# first import the required database
from backend.models import (First_step_cogs_vertical, First_step_Master_SKU, First_step_CODBFeesData_AMZ, First_step_SalesData_AMZ,
                            First_step_SB_Ads_AMZ, First_step_SD_Ads_AMZ, First_step_SP_Ads_AMZ, First_step_ReturnData_AMZ,
                            Jr_Sr_cogs, Jr_Sr_cogs_master_sku, NexTen_COGS_Master_SKU)

amazon_brand_models = {
    "TRI": {
        "sales": First_step_SalesData_AMZ,
        "sb_ads": First_step_SB_Ads_AMZ,
        "sd_ads": First_step_SD_Ads_AMZ,
        "sp_ads": First_step_SP_Ads_AMZ,
        "codb_fees": First_step_CODBFeesData_AMZ,
        "master_sku": First_step_Master_SKU,
        "cogs": First_step_cogs_vertical,
        "returns": First_step_ReturnData_AMZ
    }
}


"""--------------------------------------------------For Amazon platform----------------------------------------------"""
# This calculates the sales parameters associated with the Brand
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
        brand_specific_asin = master_sku.objects.filter(product_title__icontains=brand.lower()).values_list('amazon_asin', flat=True)

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
            fee_data_model
            .annotate(month=ExtractMonth('end_date'))
            .filter(Q(month__gte=start_month) | Q(month__lte=end_month))  # Match months in two ranges
            .aggregate(weight_handeling_fee=Sum(F('fba_weight_handling_fee_total')))
            .get('weight_handeling_fee', 0)
        ) or 0

        fixed_closing_fee = (
            fee_data_model
            .annotate(month=ExtractMonth('end_date'))
            .filter(Q(month__gte=start_month) | Q(month__lte=end_month))
            .aggregate(fixed_closing_fee=Sum(F('fixed_closing_fee_total')))
            .get('fixed_closing_fee', 0)
        ) or 0

        referral_fee = (
            fee_data_model
            .annotate(month=ExtractMonth('end_date'))
            .filter(Q(month__gte=start_month) | Q(month__lte=end_month))
            .aggregate(referral_fee=Sum(F('referral_fee_total')))
            .get('referral_fee', 0)
        ) or 0

        refund_commission_fee = (
            fee_data_model
            .annotate(month=ExtractMonth('end_date'))
            .filter(Q(month__gte=start_month) | Q(month__lte=end_month))
            .aggregate(refund_commission_fee=Sum(F('refund_commission_fee_total')))
            .get('refund_commission_fee', 0)
        ) or 0

    else:  
        # Normal case
        weight_handeling_fee = (
            fee_data_model
            .annotate(month=ExtractMonth('end_date'))
            .filter(month__gte=start_month, month__lte=end_month)
            .aggregate(weight_handeling_fee=Sum(F('fba_weight_handling_fee_total')))
            .get('weight_handeling_fee', 0)
        ) or 0

        fixed_closing_fee = (
            fee_data_model
            .annotate(month=ExtractMonth('end_date'))
            .filter(month__gte=start_month, month__lte=end_month)
            .aggregate(fixed_closing_fee=Sum(F('fixed_closing_fee_total')))
            .get('fixed_closing_fee', 0)
        ) or 0

        referral_fee = (
            fee_data_model
            .annotate(month=ExtractMonth('end_date'))
            .filter(month__gte=start_month, month__lte=end_month)
            .aggregate(referral_fee=Sum(F('referral_fee_total')))
            .get('referral_fee', 0)
        ) or 0

        refund_commission_fee = (
            fee_data_model
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


# This calculates the Ads parameters (SB, SD and SP)
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




# This works for both Multiple and Single seller 
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


# This works for Multi-brand as well as single brands both
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
# This works for both single and multi-seller brand
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
def cogs_calculation(sales_data, cogs_vertical, brand, start_date, end_date):
    
    # ------approach------
    # This functions looks up for every "SKU" that is present in Sales data, into "COGS and Vertical" data
    # for COGS related to that "SKU" and then multiplies it with the item_quantity and that's how cogs is taken into account 

    # As of now I am not not deducting the COGS of cancellation from the Gross sales because the cancellation amount is not present in the Sales data
    # We can map the Cancellation amount by using the Invoice ID of Sales made (Make sure to impelement this thing in the Sales parameter and COGS both)

    # Apply date filter to sales data
    if brand == "":
        sales = sales_data.objects.filter(invoice_date__range=[start_date, end_date])
    else:
        sales = sales_data.objects.filter(invoice_date__range=[start_date, end_date], item_description__icontains=brand.lower())

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
    cogs = cogs_calculation(sales_data, cogs_vertical, brand, start_date, end_date)

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
                    data_model["returns"],
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
                        amazon_brand_models[data_model]["returns"],
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
                    data_model["returns"],
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
                        amazon_brand_models[data_model]["returns"],
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
                    data_model["returns"],
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
                        amazon_brand_models[data_model]["returns"],
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
                    data_model["returns"],
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
                    amazon_brand_models[data_model]["returns"],
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



"""--------------As of now the above functions is for handling single and multi-brand seller account-----------------"""

"""The below code is for showing the metrices overall"""

"""From Monday 7 April start working on the "all_seller" implementation part"""

def all_brand_AMZ(start_date, end_date):

    final_dict = {}
    insights_dict = {}

    # Fetch insights dynamically for all brands
    for brand, models in amazon_brand_models.items():
        insights_dict[brand] = get_AMZ_insights(
            models['sales'], models['codb_fees'], models['sb_ads'], models['sd_ads'], models['sp_ads'],
            models['master_sku'], models['cogs'], models['returns'], brand, start_date, end_date
        )

    # Extract the first 33 key-value pairs from each brand
    insights_list = [list(insights.items())[:33] for insights in insights_dict.values()]

    # Iterate over multiple brands dynamically
    for values in zip(*insights_list):
        print(f"Values of the loop: {values}")

        keys = [v[0] for v in values]  # Extract keys (they should be identical across brands)
        print(f"Keys: {keys}")
        values = [v[1] for v in values]  # Extract values
        print(f"Values: {values}")
        
        key = keys[0]  # Any key from the extracted list
        
        # The below code implementation is for the calculating the overall metrics for the given brands
        if any(substring in key for substring in ('cpc', 'cvr', 'ctr', 'roas', 'afn_contribution')):
            
            if 'percent_' in key:
                continue
            
            else:
                percent_change_key = 'percent_change_' + key.split('display_')[1] 
                
                if 'cpc' in key:
                    
                    prev_cpc_values = [
                        Decimal(100) * Decimal(insights_dict[brand][key]) / (Decimal(insights_dict[brand][percent_change_key]) + Decimal(100))
                        for brand in amazon_brand_models.keys()
                    ]
                    current_clicks = [
                        Decimal(insights_dict[brand]['display_ads_spend']) / Decimal(insights_dict[brand][key])
                        for brand in amazon_brand_models.keys()
                    ]
                    prev_clicks = [
                        Decimal(insights_dict[brand]['prev_display_ads_spend']) / Decimal(val)
                        for brand, val in zip(amazon_brand_models.keys(), prev_cpc_values)
                    ]

                    total_ads_spend = sum(Decimal(insights_dict[brand]['display_ads_spend']) for brand in amazon_brand_models.keys())
                    total_prev_ads_spend = sum(Decimal(insights_dict[brand]['prev_display_ads_spend']) for brand in amazon_brand_models.keys())

                    overall_cpc = 0 if sum(current_clicks) == 0 else total_ads_spend / sum(current_clicks)
                    overall_prev_cpc = 0 if sum(prev_clicks) == 0 else total_prev_ads_spend / sum(prev_clicks)

                    overall_percent_change = round(((overall_cpc - overall_prev_cpc) * Decimal(100)) / overall_prev_cpc, 3) if overall_prev_cpc != 0 else Decimal(0)
                    
                    final_dict[key] = round(overall_cpc, 2)
                    final_dict[percent_change_key] = overall_percent_change

                elif 'roas' in key:
                    
                    prev_roas_value = [
                        Decimal(100) * Decimal(insights_dict[brand][key]) / (Decimal(insights_dict[brand][percent_change_key]) + Decimal(100))
                        for brand in amazon_brand_models.keys()
                    ]

                    current_ad_rev = [
                        Decimal(insights_dict[brand]['display_ads_spend']) * Decimal(insights_dict[brand][key])
                        for brand in amazon_brand_models.keys()
                    ]

                    prev_ad_rev = [
                        Decimal(insights_dict[brand]['prev_display_ads_spend']) * Decimal(val)
                        for brand, val in zip(amazon_brand_models.keys(), prev_roas_value)
                    ]

                    total_ads_spend = sum(Decimal(insights_dict[brand]['display_ads_spend']) for brand in amazon_brand_models.keys())
                    total_prev_ads_spend = sum(Decimal(insights_dict[brand]['prev_display_ads_spend']) for brand in amazon_brand_models.keys())

                    total_current_ad_rev = sum(current_ad_rev)
                    total_prev_ad_rev = sum(prev_ad_rev)

                    overall_roas = 0 if total_ads_spend == 0 else total_current_ad_rev / total_ads_spend
                    overall_prev_roas = 0 if total_prev_ads_spend == 0 else total_prev_ad_rev / total_prev_ads_spend

                    overall_percent_change = round(((overall_roas - overall_prev_roas) * Decimal(100)) / overall_prev_roas, 3) if overall_prev_roas != 0 else Decimal(0)

                    final_dict[key] = round(overall_roas, 2)
                    final_dict[percent_change_key] = overall_percent_change

                elif 'afn_contribution' in key:
                    
                    current_fbf_sales = [
                        Decimal(insights_dict[brand][key]) * Decimal(insights_dict[brand]['display_net_revenue']) / Decimal(100)
                        for brand in amazon_brand_models.keys()
                    ]

                    prev_fbf_contri = [
                        Decimal(100) * Decimal(insights_dict[brand][key]) / (Decimal(insights_dict[brand][percent_change_key]) + Decimal(100))
                        for brand in amazon_brand_models.keys()
                    ]

                    prev_fbf_sales = [
                        Decimal(val) * Decimal(insights_dict[brand]['prev_display_net_revenue']) / Decimal(100)
                        for brand, val in zip(amazon_brand_models.keys(), prev_fbf_contri)
                    ]

                    overall_fbf_contri = sum(current_fbf_sales)*100/sum(Decimal(insights_dict[brand]['display_net_revenue']) for brand in amazon_brand_models.keys())
                    overall_prev_fbf_contri = sum(prev_fbf_sales)*100/sum(Decimal(insights_dict[brand]['prev_display_net_revenue']) for brand in amazon_brand_models.keys())

                    overall_percent_change = round(((overall_fbf_contri - overall_prev_fbf_contri) * Decimal(100)) / overall_prev_fbf_contri, 3) if overall_prev_fbf_contri != 0 else Decimal(0)

                    final_dict[key] = round(overall_fbf_contri, 2)
                    final_dict[percent_change_key] = overall_percent_change

                elif 'shopsy_contribution' in key:
                    
                    current_shopsy_sales = [
                        Decimal(insights_dict[brand][key]) * Decimal(insights_dict[brand]['display_net_revenue']) / Decimal(100)
                        for brand in amazon_brand_models.keys()
                    ]

                    prev_shopsy_contri = [
                        Decimal(100) * Decimal(insights_dict[brand][key]) / (Decimal(insights_dict[brand][percent_change_key]) + Decimal(100))
                        for brand in amazon_brand_models.keys()
                    ]

                    prev_shopsy_sales = [
                        Decimal(val) * Decimal(insights_dict[brand]['prev_display_net_revenue']) / Decimal(100)
                        for brand, val in zip(amazon_brand_models.keys(), prev_shopsy_contri)
                    ]

                    overall_shopsy_contri = sum(current_shopsy_sales)*100/sum(Decimal(insights_dict[brand]['display_net_revenue']) for brand in amazon_brand_models.keys())
                    overall_prev_shopsy_contri = sum(prev_shopsy_sales)*100/sum(Decimal(insights_dict[brand]['prev_display_net_revenue']) for brand in amazon_brand_models.keys())

                    overall_percent_change = round(((overall_shopsy_contri - overall_prev_shopsy_contri) * Decimal(100)) / overall_prev_shopsy_contri, 3) if overall_prev_shopsy_contri != 0 else Decimal(0)

                    final_dict[key] = round(overall_shopsy_contri, 2)
                    final_dict[percent_change_key] = overall_percent_change


        elif 'percent_' in key:
            # Calculate previous values dynamically
            current_key = 'display_' + key.split('percent_change_')[1]
            prev_values = [
                Decimal(100) * Decimal(insights_dict[brand][current_key]) / (Decimal(val) + Decimal(100))
                for brand, val in zip(amazon_brand_models.keys(), values)
            ]

            total_prev = sum(prev_values, Decimal(0))  # Ensures sum is computed correctly
            total_current = sum(Decimal(insights_dict[brand][current_key]) for brand in amazon_brand_models.keys())

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
                for brand in amazon_brand_models.keys()
            ]

            total_aggregated_returns = sum(aggregated_returns)

            aggregated_qty = sum(Decimal(insights_dict[brand]['display_gross_units']) for brand in amazon_brand_models.keys())

            overall_percentage = total_aggregated_returns*100/aggregated_qty if aggregated_qty != 0 else Decimal(0)

            final_dict[key] = round(overall_percentage, 2)

        else:
            final_dict[key] = sum(values)  # Summing all brand values

    # Merging category-wise details dynamically
    category_keys = [
        "sales_details_title", "sales_details_vertical",
        "return_details_title", "return_details_vertical",
        "cancelled_details_title", "cancelled_details_vertical",
        "net_sale_details_title", "net_sale_details_vertical"
    ]

    for cat_key in category_keys:
        final_dict[cat_key] = sum((list(insights[cat_key]) for insights in insights_dict.values()), [])
    print(len(final_dict))
    return final_dict
