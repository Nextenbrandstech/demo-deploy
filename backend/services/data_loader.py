'''
This file is for defining the logic of loading the data 
and handeling the tough cases that are related to the data
And this function is getting called in the commands folder of the 
respective folder such as this is getting called in "upload_files.py"
'''

import pandas as pd
import numpy as np
from datetime import datetime
from decimal import Decimal
from django.utils.timezone import make_aware
from backend.models import (First_step_SalesData_AMZ, First_step_CODBFeesData_AMZ, First_step_SP_Ads_AMZ, First_step_SB_Ads_AMZ, First_step_SD_Ads_AMZ, First_step_ReturnData_AMZ,
                            First_step_SalesData_FK, First_step_cogs_vertical, First_step_InvoiceData_FK, 
                            First_step_AdsData_FK, First_step_Master_SKU)

"""Amazon's data is getting loaded here"""

def load_sales_Amazon(file_path, data_model):

    # Read the data from the file
    data = pd.read_excel(file_path)

    date_columns = ['Invoice Date', 'Shipment Date', 'Order Date', 'Credit Note Date']

    # Convert date columns, coerce errors to NaT (invalid date will become NaT)

    for col in date_columns:
        data[col] = pd.to_datetime(data[col], errors='coerce')

    # Delete all existing records before inserting new ones
    data_model.objects.all().delete()

    # Iterate through the DataFrame and create a new First_step_SalesData_AMZ object for each row

    for index, row in data.iterrows():
        data_model.objects.create(
            seller_gstin=row['Seller Gstin'],
            invoice_number=row['Invoice Number'],
            # Assign None if the date is NaT
            invoice_date=row['Invoice Date'].date() if pd.notna(row['Invoice Date']) else None,
            transaction_type=row['Transaction Type'],
            order_id=row['Order Id'],
            shipment_id=row['Shipment Id'],
            # Assign None if the date is NaT
            shipment_date=row['Shipment Date'].date() if pd.notna(row['Shipment Date']) else None,
            order_date = row['Order Date'].date() if pd.notna(row['Order Date']) else None,

            shipment_item_id=row['Shipment Item Id'],
            quantity=row['Quantity'],
            item_description=row['Item Description'],
            asin=row['Asin'],
            hsn_or_sac=row['Hsn/sac'],
            sku=row['Sku'],
            product_tax_code=row['Product Tax Code'],
            bill_from_city=row['Bill From City'],
            bill_from_state=row['Bill From State'],
            bill_from_country=row['Bill From Country'],
            bill_from_postal_code=row['Bill From Postal Code'],
            ship_from_city=row['Ship From City'],
            ship_from_state=row['Ship From State'],
            ship_from_country=row['Ship From Country'],
            ship_from_postal_code=row['Ship From Postal Code'],
            ship_to_city=row['Ship To City'],
            ship_to_state=row['Ship To State'],
            ship_to_country=row['Ship To Country'],
            ship_to_postal_code=row['Ship To Postal Code'],
            invoice_amount=row['Invoice Amount'],
            tax_exclusive_gross=row['Tax Exclusive Gross'],
            total_tax_amount=row['Total Tax Amount'],
            cgst_rate=row['Cgst Rate'],
            sgst_rate=row['Sgst Rate'],
            utgst_rate=row['Utgst Rate'],
            igst_rate=row['Igst Rate'],
            compensatory_cess_rate=row['Compensatory Cess Rate'],
            principal_amount=row['Principal Amount'],
            principal_amount_basis=row['Principal Amount Basis'],
            cgst_tax=row['Cgst Tax'],
            sgst_tax=row['Sgst Tax'],
            igst_tax=row['Igst Tax'],
            utgst_tax=row['Utgst Tax'],
            compensatory_cess_tax=row['Compensatory Cess Tax'],
            shipping_amount=row['Shipping Amount'],
            shipping_amount_basis=row['Shipping Amount Basis'],
            shipping_cgst_tax=row['Shipping Cgst Tax'],
            shipping_sgst_tax=row['Shipping Sgst Tax'],
            shipping_utgst_tax=row['Shipping Utgst Tax'],
            shipping_igst_tax=row['Shipping Igst Tax'],
            shipping_cess_tax_amount=row['Shipping Cess Tax Amount'],
            gift_wrap_amount=row['Gift Wrap Amount'],
            gift_wrap_amount_basis=row['Gift Wrap Amount Basis'],
            gift_wrap_cgst_tax=row['Gift Wrap Cgst Tax'],
            gift_wrap_sgst_tax=row['Gift Wrap Sgst Tax'],
            gift_wrap_utgst_tax=row['Gift Wrap Utgst Tax'],
            gift_wrap_igst_tax=row['Gift Wrap Igst Tax'],
            gift_wrap_compensatory_cess_tax=row['Gift Wrap Compensatory Cess Tax'],
            item_promo_discount=row['Item Promo Discount'],
            item_promo_discount_basis=row['Item Promo Discount Basis'],
            item_promo_tax=row['Item Promo Tax'],
            shipping_promo_discount=row['Shipping Promo Discount'],
            shipping_promo_discount_basis=row['Shipping Promo Discount Basis'],
            shipping_promo_tax=row['Shipping Promo Tax'],
            gift_wrap_promo_discount=row['Gift Wrap Promo Discount'],
            gift_wrap_promo_discount_basis=row['Gift Wrap Promo Discount Basis'],
            gift_wrap_promo_tax=row['Gift Wrap Promo Tax'],
            tcs_cgst_tax=row['Tcs Cgst Rate'],
            tcs_cgst_amount=row['Tcs Cgst Amount'],
            tcs_sgst_rate=row['Tcs Sgst Rate'],
            tcs_utgst_rate=row['Tcs Utgst Rate'],
            tcs_utgst_amount=row['Tcs Utgst Amount'],
            tcs_igst_rate=row['Tcs Igst Rate'],
            tcs_igst_amount=row['Tcs Igst Amount'],
            warehouse_id=row['Warehouse Id'],
            fulfillment_channel=row['Fulfillment Channel'],
            payment_method_code=row['Payment Method Code'],
            credit_note_no=row['Credit Note No'],
            # Assign None if the date is NaT
            credit_note_date=row['Credit Note Date'].date() if pd.notna(row['Credit Note Date']) else None
        )

# This is basically "Selling Economics and fees report of the Amazon platform that covers all the CODB details"
def load_CODBfees_data_AMZ(file_path, data_model):
    
    # read the data from file
    data = pd.read_excel(file_path)

    for index, row in data.iterrows():
        data_model.objects.create(
            amazon_store = row['Amazon store'],
            start_date = row['Start date'],
            end_date = row['End date'],
            parent_asin = row['Parent ASIN'],
            asin = row['ASIN'],
            fnsku = row['FNSKU'],
            msku = row['MSKU'],
            currency_code = row['Currency code'],
            average_sales_price = row['Average sales price'],
            units_sold = row['Units sold'],
            units_returned = row['Units returned'],
            net_units_sold = row['Net units sold'],
            sales = row['Sales'],
            net_sales = row['Net sales'],
            fba_weight_handling_fee_per_unit = row['FBA Weight Handling Fee per unit'],
            fba_weight_handling_fee_quantity = row['FBA Weight Handling Fee quantity'],
            fba_weight_handling_fee_total = row['FBA Weight Handling Fee total'],
            fixed_closing_fee_per_unit = row['FixedClosingFee per unit'],
            fixed_closing_fee_quantity = row['FixedClosingFee quantity'],
            fixed_closing_fee_total = row['FixedClosingFee total'],
            referral_fee_per_unit = row['Referral fee per unit'],
            referral_fee_quantity = row['Referral fee quantity'],
            referral_fee_total = row['Referral fee total'],
            refund_commission_fee_per_unit = row['RefundCommissionFee per unit'],
            refund_commission_fee_quantity = row['RefundCommissionFee quantity'],
            refund_commission_fee_total = row['RefundCommissionFee total']
        )

def load_SP_Ads_AMZ(file_path, data_model):

    data = pd.read_excel(file_path)

    for index, row in data.iterrows():
        data_model.objects.create(
            date = row['Date'],
            portfolio_name = row['Portfolio name'],
            currency = row['Currency'],
            campaign_name = row['Campaign Name'],
            ad_group_name = row['Ad Group Name'],
            targeting = row['Targeting'],
            match_type = None if row['Match Type'] == '-' else row['Match Type'],
            impressions = row['Impressions'],
            top_of_search_impression_share = row['Top-of-search Impression Share'],
            clicks = row['Clicks'],
            ctr = row['Click-Thru Rate (CTR)'],
            cpc = row['Cost Per Click (CPC)'],
            spend = row['Spend'],
            total_advertising_cost_of_sales = row['Total Advertising Cost of Sales (ACOS) '],
            total_return_on_advertising_spend = row['Total Return on Advertising Spend (ROAS)'],
            day_14_total_sales = row['14 Day Total Sales '],
            day_14_total_orders = row['14 Day Total Orders (#)'],
            day_14_total_units = row['14 Day Total Units (#)'],
            day_14_conversion_rate = row['14 Day Conversion Rate']
        )


def load_SB_Ads_AMZ(file_path, data_model):
    
    data = pd.read_excel(file_path)

    for index, row in data.iterrows():
        data_model.objects.create(
            date = row['Date'],
            portfolio_name = row['Portfolio name'],
            currency = row['Currency'],
            campaign_name = row['Campaign Name'],
            cost_type = row['Cost Type'],
            country = row['Country'],
            impressions = row['Impressions'],
            clicks = row['Clicks'],
            ctr = row['Click-Thru Rate (CTR)'],
            cpc = row['Cost Per Click (CPC)'],
            spend = row['Spend'],
            total_advertising_cost_of_sales = row['Total Advertising Cost of Sales (ACOS) '],
            total_return_on_advertising_spend = row['Total Return on Advertising Spend (ROAS)'],
            day_14_total_sales = row['14 Day Total Sales '],
            day_14_total_orders = row['14 Day Total Orders (#)'],
            day_14_total_units = row['14 Day Total Units (#)'],
            day_14_conversion_rate = row['14 Day Conversion Rate'],
            viewable_impressions = row['Viewable Impressions'],
            cost_per_1000_viewable_impressions = row['Cost per 1,000 viewable impressions (VCPM)'],
            view_through_rate = row['View-Through Rate (VTR)'],
            click_through_rate_for_views = row['Click-Through Rate for Views (vCTR)'],
            video_first_quartile_views = row['Video First Quartile Views'],
            video_midpoint_views = row['Video Midpoint Views'],
            video_third_quartile_views = row['Video Third Quartile Views'],
            video_complete_views = row['Video Complete Views'],
            video_unmutes = row['Video Unmutes'],
            seconds_5_views = row['5 Second Views'],
            seconds_5_view_rate = row['5 Second View Rate'],
            day_14_branded_searches = row['14 Day Branded Searches'],
            day_14_detail_page_views = row['14 Day Detail Page Views (DPV)'],
            day_14_new_to_brand_orders = row['14 Day New-to-brand Orders (#)'],
            day_14_percent_of_orders_new_to_brand = row['14 Day % of Orders New-to-brand'],
            day_14_new_to_brand_sales = row['14 Day New-to-brand Sales'],
            day_14_percent_of_sales_new_to_brand = row['14 Day % of Sales New-to-brand'],
            day_14_new_to_brand_units = row['14 Day New-to-brand Units (#)'],
            day_14_percent_of_units_new_to_brand = row['14 Day % of Units New-to-brand'],
            day_14_new_to_brand_order_rate = row['14 Day New-to-brand Order Rate'],
            total_advertising_cost_of_sales_clicks = row['Total Advertising Cost of Sales (ACOS) - (Click)'],
            total_return_on_advertising_spend_clicks = row['Total Return on Advertising Spend (ROAS) - (Click)'],
            day_14_total_sales_clicks = row['14 Day Total Sales - (Click)'],
            day_14_total_orders_clicks = row['14 Day Total Orders (#) - (Click)'],
            day_14_total_units_clicks = row['14 Day Total Units (#) - (Click)'],
            new_to_brand_detail_page_views = row['New-to-brand detail page views'],
            new_to_brand_detail_page_view_click_through_conversions = row['New-to-brand detail page view click-through conversions'],
            new_to_brand_detail_page_view_rate = row['New-to-brand detail page view rate'],
            effective_cost_per_new_to_brand_detail_page_view = row['Effective cost per new-to-brand detail page view'],
            day_14_atc = row['14 Day ATC'],
            day_14_atc_clicks = row['14 Day ATC Clicks'],
            day_14_atcr = row['14 Day ATCR'],
            effective_cost_per_add_to_cart = row['Effective cost per Add to Cart (eCPATC)'],
            branded_searches_click_through_conversions = row['Branded Searches click-through conversions'],
            branded_searches_rate = row['Branded Searches Rate'],
            effective_cost_per_branded_search = row['Effective cost per Branded Search'],
            long_term_sales = row['Long-Term Sales'],
            long_term_roas = row['Long-Term ROAS']
        )

def load_SD_Ads_AMZ(file_path, data_model):
    
    data = pd.read_excel(file_path)

    for index, row in data.iterrows():
        data_model.objects.create(
            date = row['Date'],
            portfolio_name = row['Portfolio name'],
            currency = row['Currency'],
            campaign_name = row['Campaign Name'],
            cost_type = row['Cost Type'],
            ad_group_name = row['Ad Group Name'],
            targeting = row['Targeting'],
            bid_optimization = row['Bid Optimization'],
            impressions = row['Impressions'],
            viewable_impressions = row['Viewable Impressions'],
            clicks = row['Clicks'],
            ctr = row['Click-Thru Rate (CTR)'],
            day_14_detail_page_views = row['14 Day Detail Page Views (DPV)'],
            spend = row['Spend'],
            cpc = row['Cost Per Click (CPC)'],
            cost_per_1000_viewable_impressions = row['Cost per 1,000 viewable impressions (VCPM)'],
            total_advertising_cost_of_sales = row['Total Advertising Cost of Sales (ACOS)'],
            total_return_on_advertising_spend = row['Total Return on Advertising Spend (ROAS)'],
            day_14_total_orders = row['14 Day Total Orders (#)'],
            day_14_total_units = row['14 Day Total Units (#)'],
            day_14_total_sales = row['14 Day Total Sales'],
            day_14_new_to_brand_orders = row['14 Day New-to-brand Orders (#)'],
            day_14_new_to_brand_sales = row['14 Day New-to-brand Sales'],
            day_14_new_to_brand_units = row['14 Day New-to-brand Units (#)'],
            total_advertising_cost_of_sales_clicks = row['Total Advertising Cost of Sales (ACOS) - (Click)'],
            total_return_on_advertising_spend_click = row['Total Return on Advertising Spend (ROAS) - (Click)'],
            day_14_total_orders_click = row['14 Day Total Orders (#) - (Click)'],
            day_14_total_units_click = row['14 Day Total Units (#) - (Click)'],
            day_14_total_sales_click = row['14 Day Total Sales (#) - (Click)'],
            day_14_new_to_brand_orders_click = row['14 Day New-to-brand Orders (#) - (Click)'],
            day_14_new_to_brand_sales_click = row['14 Day New-to-brand Sales - (Click)'],
            day_14_new_to_brand_units_click = row['14 Day New-to-brand Units (#) - (Click)']
        )



def load_Return_AMZ(file_path, data_model):
    data = pd.read_excel(file_path)

    # Clean column names
    data.columns = data.columns.str.strip()

    # Strip strings in all object columns
    for col in data.select_dtypes(include='object').columns:
        data[col] = data[col].map(lambda x: x.strip() if isinstance(x, str) else x)

    # Handle DecimalField-compatible columns
    FLOAT_COLUMNS = [
        'Label cost', 'Return quantity', 'Order Amount',
        'Order quantity', 'SafeT claim reimbursement amount', 'Refunded Amount'
    ]
    BAD_FLOAT_VALUES = ['“”', '”', '“', '', ' ', 'nan', 'NaN', 'None']

    for col in FLOAT_COLUMNS:
        if col in data.columns:
            data[col] = pd.to_numeric(data[col].replace(BAD_FLOAT_VALUES, np.nan), errors='coerce').fillna(0)

    # Handle date and datetime columns
    DATE_COLUMNS = ['Order date', 'Return request date', 'Return delivery date']
    DATETIME_COLUMNS = ['SafeT claim creation time']

    for col in DATE_COLUMNS:
        if col in data.columns:
            data[col] = pd.to_datetime(data[col], errors='coerce')

    for col in DATETIME_COLUMNS:
        if col in data.columns:
            data[col] = pd.to_datetime(data[col], errors='coerce')

    def make_datetime_aware_if_needed(dt):
        if pd.isnull(dt):
            return None
        try:
            return make_aware(dt)
        except Exception:
            return dt

    for index, row in data.iterrows():
        try:
            data_model.objects.create(
                order_id = row['Order ID'],
                order_date = row['Order date'],
                return_request_date = row['Return request date'],
                return_request_status = row['Return request status'],
                amazon_rma_id = row['Amazon RMA ID'],
                seller_rma_id = row['Seller RMA ID'],
                label_type = row['Label type'],
                label_cost = row['Label cost'],
                currency_code = row['Currency code'],
                return_carrier = row['Return carrier'],
                tracking_id = row['Tracking ID'],
                label_to_be_paid_by = row['Label to be paid by'],
                a_to_z_claim = row['A-to-z claim'],
                is_prime = row['Is prime'],
                asin = row['ASIN'],
                merchant_sku = row['Merchant SKU'],
                item_name = row['Item Name'],
                return_quantity = row['Return quantity'],
                return_reason = row['Return reason'],
                in_policy = row['In policy'],
                return_type = row['Return type'],
                resolution = row['Resolution'],
                invoice_number = row['Invoice number'],
                return_delivery_date = row['Return delivery date'],
                order_amount = row['Order Amount'],
                order_quantity = row['Order quantity'],
                safet_action_reason = row['SafeT Action reason'],
                safet_claim_id = row['SafeT claim ID'],
                safet_claim_status = row['SafeT claim state'],
                safet_claim_creation_time = make_datetime_aware_if_needed(row['SafeT claim creation time']),
                safet_claim_reimbursement_amount = row['SafeT claim reimbursement amount'],
                refund_amount = row['Refunded Amount'],
                category = row['Category']
            )
        except Exception as e:
            print(f"\n❌ Error at row {index + 2} (Excel row): {e}")
            print("Row data:", row.to_dict())




"""Flipkart's data is getting loaded here"""

def load_sales_FK(file_path, data_model):
    
    # read the data from file
    data = pd.read_excel(file_path)

    for index, row in data.iterrows():
        data_model.objects.create(
            seller_gstin = row['Seller GSTIN'],
            order_id = row['Order ID'],
            order_item_id = row['Order Item ID'],
            product_title = row['Product Title/Description'],
            fsn = row['FSN'],
            sku = row['SKU'],
            hsn_code = row['HSN Code'],
            event_type = row['Event Type'],
            event_sub_type = row['Event Sub Type'],
            order_type = row['Order Type'],
            fulfilment_type = row['Fulfilment Type'],

            order_date = None if row['Order Date'] == "-" else row['Order Date'],
            order_approval_date = None if row['Order Approval Date '] == "-" else row['Order Approval Date '],
            

            item_quantity = row['Item Quantity'],
            order_shipped_from_state = row['Order Shipped From (State)'],
            warehouse_id = row['Warehouse ID'],
            price_before_discount = row['Price before discount'],
            total_discount = row['Total Discount'],
            seller_share = row['Seller Share '],
            bank_offer_share = row['Bank Offer Share'],
            price_after_discount = row['Price after discount (Price before discount-Total discount)'],
            shipping_charges = row['Shipping Charges'],
            final_invoice_amount = row['Final Invoice Amount (Price after discount+Shipping Charges)'],
            type_of_tax = row['Type of tax'],
            taxable_value = row['Taxable Value (Final Invoice Amount -Taxes)'],
            cst_rate = row['CST Rate'],
            cst_amount = row['CST Amount'],
            vat_rate = row['VAT Rate'],
            vat_amount = row['VAT Amount'],
            luxury_cess_rate = row['Luxury Cess Rate'],
            luxury_cess_amount = row['Luxury Cess Amount'],
            igst_rate = row['IGST Rate'],
            igst_amount = row['IGST Amount'],
            cgst_rate = row['CGST Rate'],
            cgst_amount = row['CGST Amount'],
            sgst_rate = row['SGST Rate (or UTGST as applicable)'],
            sgst_amount = row['SGST Amount (Or UTGST as applicable)'],
            tcs_igst_rate = row['TCS IGST Rate'],
            tcs_igst_amount = row['TCS IGST Amount'],
            tcs_cgst_rate = row['TCS CGST Rate'],
            tcs_cgst_amount = row['TCS CGST Amount'],
            tcs_sgst_rate = row['TCS SGST Rate'],
            tcs_sgst_amount = row['TCS SGST Amount'],
            total_tcs_deducted = row['Total TCS Deducted'],
            buyer_invoice_id = row['Buyer Invoice ID'],
            
            buyer_invoice_date = row['Buyer Invoice Date'],

            buyer_invoive_amount = row['Buyer Invoice Amount '],
            customer_billing_pincode = row['Customer\'s Billing Pincode'],
            customer_billing_state = row['Customer\'s Billing State'],
            customer_delivery_pincode = row['Customer\'s Delivery Pincode'],
            customer_delivery_state = row['Customer\'s Delivery State'],
            
            usual_price = None if pd.isna(row['Usual Price']) or row['Usual Price'] == "NA" else Decimal(row['Usual Price']),

            is_shopsy_order = row['Is Shopsy Order?'],
            tds_rate = row['TDS Rate'],
            tds_amount = row['TDS Amount']
        )

def load_Invoice_FK(file_path, data_model):

    # read the data from file
    data = pd.read_excel(file_path)

    # deleting the existing data before inserting the new ones
    # data_model.objects.all().delete()

    for index, row in data.iterrows():
        data_model.objects.create(
            service_type = row['Service Type'],
            order_item_id = row['Order Item ID/ Listing ID/ Campaign ID/Transaction ID'],
            recall_id = row['Recall ID'],
            warehouse_state_code = row['Warehouse State Code'],
            fee_name = row['Fee Name'],
            total_fee_amount = row['Total Fee Amount(Rs.)'],
            fee_amount = row['Fee Amount (Rs.)'],
            fee_waiver_amount = row['Fee Waiver Amount(Rs.)'],
            cgst_rate = row['CGST Rate'],
            sgst_rate = row['SGST/UTGST Rate'],
            igst_rate = row['IGST Rate'],
            cgst_amount = row['CGST Amount'],
            sgst_amount = row['SGST/UTGST Amount'],
            igst_amount = row['IGST Amount'],
            total_tax_amount = row['Total Tax Amount (Rs.)'],
            date = row['Date']
        )

def load_Ads_FK(file_path, data_model):
    
    data = pd.read_excel(file_path)

    # data_model.objects.all().delete()

    for index, row in data.iterrows():
        data_model.objects.create(
            campaign_id = row['Campaign ID'],
            campaign_name = row['Campaign Name'],
            ad_group_id = row['Ad Group ID'],
            ad_group_name = row['AdGroup Name'],
            date = row['Date'],
            views = row['Views'],
            clicks = row['Clicks'],
            ctr = row['CTR'],
            cvr = row['CVR'],
            ad_spend = row['Ad Spend'],
            units_sold_direct = row['Units Sold (Direct)'],
            units_sold_indirect = row['Units Sold (Indirect)'],
            direct_revenue = row['Direct Revenue'],
            indirect_revenue = row['Indirect Revenue'],
            roi_direct = row['ROI (Direct)'],
            roi_indirect = row['ROI (Indirect)']
        )

def load_Ads_FK_MP(file_path, data_model):
    data = pd.read_excel(file_path)

    for index, row in data.iterrows():
        data_model.objects.create(
            campaign_id = row['Campaign ID'],
            campaign_name = row['Campaign Name'],
            date = row['Date'],
            ad_spend = row['Ad Spend'],
            views = row['Views'],
            clicks = row['Clicks'],
            total_converted_units = row['Total converted units'],
            total_revenue = row['Total Revenue (Rs.)']
        )

def load_Return_FK(file_path, data_model):
    data = pd.read_excel(file_path)

    for index, row in data.iterrows():
        data_model.objects.create(
            return_id = row['return_id'],
            order_item_id = row['order_item_id'],
            fulfilment_type = row['fulfilment_type'],
            # return_requested_date = row['return_requested_date'],
            # return_approval_date = row['return_approval_date'],
            return_status = row['return_status'],
            return_reason = row['return_reason'],
            return_sub_reason = row['return_sub_reason'],
            return_type = row['return_type'],
            return_result = row['return_result'],
            return_expectation = row['return_expectation'],
            reverse_logistics_tracking_id = row['reverse_logistics_tracking_id'],
            sku = row['sku'],
            fsn = row['fsn'],
            product_title = row['product_title'],
            quantity = row['quantity'],
            return_completion_type = row['return_completion_type'],
            primary_pv_output = row['primary_pv_output'],
            detailed_pv_output = row['detailed_pv_output'],
            final_condition_of_returned_product = row['final_condition_of_returned_product'],
            tech_visit_sla = row['tech_visit_sla'],
            # tech_visit_by_date = row['tech_visit_by_date'],
            # tech_visit_completion_datetime = row['tech_visit_completion_datetime'],
            tech_visit_completion_breach = row['tech_visit_completion_breach'],
            return_completion_sla = row['return_completion_sla'],
            # return_complete_by_date = row['return_complete_by_date'],
            # return_completion_date = row['return_completion_date'],
            return_completion_breach = row['return_completion_breach'],
            # return_cancellation_date = row['return_cancellation_date'],
            return_cancellation_reason = row['return_cancellation_reason']
        )

def load_First_step_Master_SKU(file_path, data_model):

    data = pd.read_excel(file_path)

    data_model.objects.all().delete()

    for index, row in data.iterrows():
        data_model.objects.create(
            sku = row['SKU'],
            product_title = row['Product Title'],
            ean = row['EAN'],
            length = row['L'],
            breadth = row['B'],
            height = row['H'],
            weight = row['Wt'],
            fk_platform_sku = row['Flipkart Platform SKU'],
            fk_fsn = row['Flipkart FSN'],
            amazon_platform_sku = row['Amazon Platform SKU'],
            amazon_asin = row['Amazon ASIN'],
            first_cry_platform_sku = row['FirstCry Platform SKU'],
            first_cry_product_id = row['FirstCry Product Id'],
            myntra_platformsku = row['Myntra Platform SKU'],
            myntra_product_id = row['Myntra Product Id'],
            jiomart_platform_sku = row['Jiomart Platform SKU'],
            jiomart_product_id = row['Jiomart Product Id'],
            meesho_platform_sku = row['Meesho Platform SKU'],
            meesho_product_id = row['Meesho Product Id'],
            pharmeasy_platform_sku = row['Pharmeasy Platform SKU'],
            pharmeasy_product_id = row['Pharmeasy Product Id'],
            rk_world_platform_sku = row['RK World Platform SKU'],
            rk_world_product_id = row['RK World Product Id'],
            mrp = row['MRP'],
            gst = row['GST'],
            hsn = row['HSN'],
            cogs = row['Cogs'],
            product_vertical = row['Vertical']
        )

def load_First_step_cogs_vertical(file_path, data_model):

    # read the data from file
    data = pd.read_excel(file_path)

    # delete all the existing data before inserting the new ones (to tackle the problem of duplicacy)
    data_model.objects.all().delete()

    for index, row in data.iterrows():
        # previously it was First_step_cogs_vertical
        data_model.objects.create(
            sku = row['SKU'],
            pid = row['PID'],
            vertical = row['VERTICAL'],
            mrp = row['MRP'],
            cogs = row['Cogs']
        )

def load_Jr_Sr_cogs_Master_SKU(file_path, data_model):
    
    data = pd.read_excel(file_path)

    # for clearing out the data from the database
    data_model.objects.all().delete()

    for index, row in data.iterrows():
        data_model.objects.create(
            product_vertical = row['Vertical'],
            size = row['Size'],
            pack_size = row['Pack size'],
            check_name = row['Check_name'],
            product_title = row['Product Title'],
            sku = row['SKU'],
            fsn = row['FSN'],
            lid = row['LID'],
            mrp = row['MRP'],
            settlement_per_unit = row['Settlement per unit'],
            cogs = row['Cogs']
        )

def load_Jr_Sr_cogs(file_path, data_model):
    data = pd.read_excel(file_path)

    data_model.objects.all().delete()

    for index, row in data.iterrows():
        data_model.objects.create(
            product_title = row['Product Title'],
            sku = row['SKU'],
            mrp = row['MRP'],
            settlement_per_unit = row['Settlement per unit'],
            cogs = row['Cogs']
        )



"""NexTen Database loading"""

def load_NexTen_COGS_Master_SKU(file_path, data_model):
    
    data = pd.read_excel(file_path)

    data_model.objects.all().delete()

    for index, row in data.iterrows():
        data_model.objects.create(
            product_title = row['Product Title'],
            sku = row['SKU'],
            product_vertical = row['Vertical'],
            fsn = row['FSN'],
            cogs = row['Cogs'],
            brand = row['Brand'],
            seller = row['Seller']
        )

    