'''
The "command" folder is for calling the required functions(that are logic based) 
which are present in the "service" folder 

This file simply calls the function which are defined in the data_analysis.py file.
So that means you have to run this file "python manage.py run_analysis"
'''

# management/commands/run_analysis.py
from django.core.management.base import BaseCommand
import pprint
from backend.services.data_analysis import (Flipkart_invoice_parameters, get_fk_insights, Flipkart_ads_parameters, 
                                            Flipkart_sales_parameters, calculate_cogs_with_date_filter, return_product_flipkart, 
                                            demographic_plot_flipkart, pie_chart_flipkart, 
                                            all_brand_Flipkart, all_brand_map_Flipkart, all_brand_pie_Flipkart, all_brand_dynamic_plot_Flipkart, Flipkart_PnL_calculator,
                                            Flipkart_multi_brand_sales, Flipkart_MP_ads_multi_brand, Flipkart_multi_brand_invoice, calculate_cogs_multi_brand,
                                            Flipkart_PnL_calculator_multi_brand, get_fk_insights_multi_brand, return_product_flipkart_multi_brand, Flipkart_MP_ads_parameters,
                                            demo_function, cogs_calculation, Amazon_fees_parameters, demo_AMZ, Amazon_sales_parameters, return_product_AMZ)

from backend.services.data_analysis_amz import (Amazon_Ads_parameters, Amazon_PnL_calculator, get_AMZ_insights, 
                                                pie_chart_AMZ, get_dynamic_plot_AMZ, all_brand_AMZ, all_brand_map_AMZ, all_brand_pie_AMZ, all_brand_dynamic_plot_AMZ)




from backend.models import (First_step_AdsData_FK, First_step_InvoiceData_FK, First_step_SalesData_FK, First_step_cogs_vertical, First_step_FK_Return_data,
                            First_step_Master_SKU, First_step_SalesData_AMZ, First_step_CODBFeesData_AMZ, First_step_SB_Ads_AMZ, 
                            First_step_SD_Ads_AMZ, First_step_SP_Ads_AMZ, First_step_ReturnData_AMZ,
                            Jr_Sr_AdsData_FK_MP, Jr_Sr_cogs, Jr_Sr_cogs_master_sku, Jr_Sr_InvoiceData_FK, Jr_Sr_SalesData_FK,
                            NexTen_AdsData_FK_MP, NexTen_COGS_Master_SKU, NexTen_InvoiceData_FK, NexTen_SalesData_FK, NexTen_Return_data)

from django.db.models import OuterRef, Subquery, F, Value, DecimalField, CharField, Sum, Q
from django.db.models.functions import Coalesce
from datetime import date, timedelta
import plotly.io as pio
import plotly.graph_objects as go
import json


class Command(BaseCommand):
    help = 'Run analysis on sales data'

    def handle(self, *args, **kwargs):
       

        # Define your date range
        start_date = date(2024, 12, 1)
        end_date = date(2024, 12, 3)

        pnl_start_date = date(2024, 10, 1)
        pnl_end_date = date(2024, 10, 1)
        pnl_prev_start_date = date(2024, 9, 30)
        pnl_prev_end_date = date(2024, 9, 30)

        overall_result = all_brand_AMZ(start_date, end_date)
        # print(f"final output: {overall_result}")

        # get_AMZ_insights(First_step_SalesData_AMZ, First_step_CODBFeesData_AMZ, First_step_SB_Ads_AMZ, First_step_SD_Ads_AMZ, First_step_SP_Ads_AMZ,
        #                  First_step_Master_SKU, First_step_cogs_vertical, First_step_ReturnData_AMZ, "", start_date, end_date)

        # (_, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _,
        #     _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _) = Amazon_sales_parameters(First_step_SalesData_AMZ, First_step_ReturnData_AMZ, "", start_date, end_date)

        