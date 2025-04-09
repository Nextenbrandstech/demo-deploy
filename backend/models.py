from django.db import models
from datetime import datetime
from decimal import Decimal, InvalidOperation

"""Amazon data models start here"""


class First_step_SalesData_AMZ(models.Model):
    seller_gstin = models.CharField(max_length=255)
    invoice_number = models.CharField(max_length=255)
    invoice_date = models.DateTimeField(null=True, blank=True)
    transaction_type = models.CharField(max_length=255)
    order_id = models.CharField(max_length=255)
    shipment_id = models.CharField(max_length=255)
    shipment_date = models.DateTimeField(null=True, blank=True)
    order_date = models.DateTimeField(null=True, blank=True)
    shipment_item_id = models.CharField(max_length=255)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    item_description = models.CharField(max_length=500)
    asin = models.CharField(max_length=255)
    hsn_or_sac = models.CharField(max_length=255)
    sku = models.CharField(max_length=255)
    product_tax_code = models.CharField(max_length=255)
    bill_from_city = models.CharField(max_length=255)
    bill_from_state = models.CharField(max_length=255)
    bill_from_country = models.CharField(max_length=255)
    bill_from_postal_code = models.CharField(max_length=255)
    ship_from_city = models.CharField(max_length=255)
    ship_from_state = models.CharField(max_length=255)
    ship_from_country = models.CharField(max_length=255)
    ship_from_postal_code = models.CharField(max_length=255)
    ship_to_city = models.CharField(max_length=255)
    ship_to_state = models.CharField(max_length=255)
    ship_to_country = models.CharField(max_length=255)
    ship_to_postal_code = models.CharField(max_length=255)
    invoice_amount = models.DecimalField(max_digits=10, decimal_places=2)
    tax_exclusive_gross = models.DecimalField(max_digits=10, decimal_places=2)
    total_tax_amount = models.DecimalField(max_digits=10, decimal_places=2)
    cgst_rate = models.DecimalField(max_digits=10, decimal_places=2)
    sgst_rate = models.DecimalField(max_digits=10, decimal_places=2)
    utgst_rate = models.DecimalField(max_digits=10, decimal_places=2)
    igst_rate = models.DecimalField(max_digits=10, decimal_places=2)
    compensatory_cess_rate = models.DecimalField(max_digits=10, decimal_places=2)
    principal_amount = models.DecimalField(max_digits=10, decimal_places=2)
    principal_amount_basis = models.DecimalField(max_digits=10, decimal_places=2)
    cgst_tax = models.DecimalField(max_digits=10, decimal_places=2)
    sgst_tax = models.DecimalField(max_digits=10, decimal_places=2)
    igst_tax = models.DecimalField(max_digits=10, decimal_places=2)
    utgst_tax = models.DecimalField(max_digits=10, decimal_places=2)
    compensatory_cess_tax = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_amount = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_amount_basis = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_cgst_tax = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_sgst_tax = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_utgst_tax = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_igst_tax = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_cess_tax_amount = models.DecimalField(max_digits=10, decimal_places=2)
    gift_wrap_amount = models.DecimalField(max_digits=10, decimal_places=2)
    gift_wrap_amount_basis = models.DecimalField(max_digits=10, decimal_places=2)
    gift_wrap_cgst_tax = models.DecimalField(max_digits=10, decimal_places=2)
    gift_wrap_sgst_tax = models.DecimalField(max_digits=10, decimal_places=2)
    gift_wrap_utgst_tax = models.DecimalField(max_digits=10, decimal_places=2)
    gift_wrap_igst_tax = models.DecimalField(max_digits=10, decimal_places=2)
    gift_wrap_compensatory_cess_tax = models.DecimalField(max_digits=10, decimal_places=2)
    item_promo_discount = models.DecimalField(max_digits=10, decimal_places=2)
    item_promo_discount_basis = models.DecimalField(max_digits=10, decimal_places=2)
    item_promo_tax = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_promo_discount = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_promo_discount_basis = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_promo_tax = models.DecimalField(max_digits=10, decimal_places=2)
    gift_wrap_promo_discount = models.DecimalField(max_digits=10, decimal_places=2)
    gift_wrap_promo_discount_basis = models.DecimalField(max_digits=10, decimal_places=2)
    gift_wrap_promo_tax = models.DecimalField(max_digits=10, decimal_places=2)
    tcs_cgst_tax = models.DecimalField(max_digits=10, decimal_places=2)
    tcs_cgst_amount = models.DecimalField(max_digits=10, decimal_places=2)
    tcs_sgst_rate = models.DecimalField(max_digits=10, decimal_places=2)
    tcs_utgst_rate = models.DecimalField(max_digits=10, decimal_places=2)
    tcs_utgst_amount = models.DecimalField(max_digits=10, decimal_places=2)
    tcs_igst_rate = models.DecimalField(max_digits=10, decimal_places=2)
    tcs_igst_amount = models.DecimalField(max_digits=10, decimal_places=2)
    warehouse_id = models.CharField(max_length=255)
    fulfillment_channel = models.CharField(max_length=255)
    payment_method_code = models.CharField(max_length=255)
    credit_note_no = models.CharField(max_length=255)
    credit_note_date = models.DateTimeField(null=True, blank=True)
    

    def __str__(self):
        return self.invoice_number
    
    class Meta:
        db_table = "First_step_SalesData_AMZ"  # Explicitly set the table name

# This is "Selling Economics and Fees report" for the Amazon platform that covers all the CODB details
class First_step_CODBFeesData_AMZ(models.Model):
    
    amazon_store = models.CharField(max_length=50)
    start_date = models.DateField()
    end_date = models.DateField()
    parent_asin = models.CharField(max_length=100)
    asin = models.CharField(max_length=100)
    fnsku = models.CharField(max_length=100)
    msku = models.CharField(max_length=100)
    currency_code = models.CharField(max_length=50)
    average_sales_price = models.DecimalField(max_digits=8, decimal_places=2)
    units_sold = models.DecimalField(max_digits=8, decimal_places=2)
    units_returned = models.DecimalField(max_digits=8, decimal_places=2)
    net_units_sold = models.DecimalField(max_digits=8, decimal_places=2)
    sales = models.DecimalField(max_digits=8, decimal_places=2)
    net_sales = models.DecimalField(max_digits=8, decimal_places=2)
    fba_weight_handling_fee_per_unit = models.DecimalField(max_digits=8, decimal_places=2)
    fba_weight_handling_fee_quantity = models.DecimalField(max_digits=8, decimal_places=2)
    fba_weight_handling_fee_total = models.DecimalField(max_digits=8, decimal_places=2)
    fixed_closing_fee_per_unit = models.DecimalField(max_digits=8, decimal_places=2)
    fixed_closing_fee_quantity = models.DecimalField(max_digits=8, decimal_places=2)
    fixed_closing_fee_total = models.DecimalField(max_digits=8, decimal_places=2)
    referral_fee_per_unit = models.DecimalField(max_digits=8, decimal_places=2)
    referral_fee_quantity = models.DecimalField(max_digits=8, decimal_places=2)
    referral_fee_total = models.DecimalField(max_digits=8, decimal_places=2)
    refund_commission_fee_per_unit = models.DecimalField(max_digits=8, decimal_places=2)
    refund_commission_fee_quantity = models.DecimalField(max_digits=8, decimal_places=2)
    refund_commission_fee_total = models.DecimalField(max_digits=8, decimal_places=2)

    def save(self, *args, **kwargs):
        # Convert start_date if it is a string
        if isinstance(self.start_date, str):  # For format "12-01-2024"
            try:
                # Parse as mm-dd-yyyy and ensure it's treated as December 1, 2024
                self.start_date = datetime.strptime(self.start_date.strip(), '%m-%d-%Y').date()
            except ValueError as e:
                raise ValueError(f"Invalid start_date format: {self.start_date}. Expected format: mm-dd-yyyy.") from e

        # Convert end_date if it is a string
        if isinstance(self.end_date, str):  # For format "12/31/2024"
            try:
                # Parse as mm/dd/yyyy
                self.end_date = datetime.strptime(self.end_date.strip(), '%m/%d/%Y').date()
            except ValueError as e:
                raise ValueError(f"Invalid end_date format: {self.end_date}. Expected format: mm/dd/yyyy.") from e

        # List of all DecimalField fields
        decimal_fields = [
            'average_sales_price',
            'units_sold',
            'units_returned',
            'net_units_sold',
            'sales',
            'net_sales',
            'fba_weight_handling_fee_per_unit',
            'fba_weight_handling_fee_quantity',
            'fba_weight_handling_fee_total',
            'fixed_closing_fee_per_unit',
            'fixed_closing_fee_quantity',
            'fixed_closing_fee_total',
            'referral_fee_per_unit',
            'referral_fee_quantity',
            'referral_fee_total',
            'refund_commission_fee_per_unit',
            'refund_commission_fee_quantity',
            'refund_commission_fee_total',
        ]

        # Convert NaN or None to Decimal(0) for all DecimalField fields
        for field in decimal_fields:
            value = getattr(self, field, None)
            if value is None or str(value).lower() == 'nan':
                setattr(self, field, Decimal(0))

        # Call the parent class save method
        super().save(*args, **kwargs)



    def __str__(self):
        return self.asin

    def Meta(self):
        db_table = "First_step_CODBFeesData_AMZ"    # Explicitly set the table name


class First_step_SP_Ads_AMZ(models.Model):
    date = models.DateField(blank=True, null=True)
    portfolio_name = models.CharField(max_length=50, blank=True)
    currency = models.CharField(max_length=50, blank=True)
    campaign_name = models.CharField(max_length=100, blank=True)
    ad_group_name = models.CharField(max_length=100, blank=True)
    targeting = models.CharField(max_length=100, blank=True)
    match_type = models.CharField(max_length=100, blank=True, null=True)
    
    # Adjusted DecimalFields with appropriate max_digits and decimal_places
    impressions = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    top_of_search_impression_share = models.DecimalField(max_digits=6, decimal_places=5, null=True, blank=True)
    clicks = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    ctr = models.DecimalField(max_digits=6, decimal_places=5, null=True, blank=True)
    cpc = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True)  # Increased max_digits
    spend = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)  # Increased max_digits
    total_advertising_cost_of_sales = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True)
    total_return_on_advertising_spend = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True)
    day_14_total_sales = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)  # Increased max_digits
    day_14_total_orders = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    day_14_total_units = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    day_14_conversion_rate = models.DecimalField(max_digits=6, decimal_places=5, null=True, blank=True)
    
    def preprocess_value(self, value):
        """
        Preprocesses numeric values:
        - Removes currency symbols like ₹.
        - Removes percentage symbols (%).
        - Handles None or NaN values and converts them to Decimal(0).
        """
        if value is None or str(value).lower() == 'nan':
            return Decimal(0)
        try:
            # Remove ₹ symbol, % symbol, and any extra spaces
            value = str(value).replace('₹', '').replace('%', '').strip()
            return Decimal(value)
        except (InvalidOperation, ValueError):
            raise ValueError(f"Invalid value for numeric field: {value}")
    
    def save(self, *args, **kwargs):
        # Convert the date if it is a string in the format "Dec 01, 2024"
        if isinstance(self.date, str):
            try:
                # Parse the date using the format "Dec 01, 2024"
                self.date = datetime.strptime(self.date.strip(), '%b %d, %Y').date()
            except ValueError as e:
                raise ValueError(f"Invalid date format: {self.date}. Expected format: Dec 01, 2024.") from e
        
        # List of all DecimalField fields
        decimal_fields = [
            'impressions',
            'top_of_search_impression_share',
            'clicks',
            'ctr',
            'cpc',
            'spend',
            'total_advertising_cost_of_sales',
            'total_return_on_advertising_spend',
            'day_14_total_sales',
            'day_14_total_orders',
            'day_14_total_units',
            'day_14_conversion_rate',
        ]
    
        # Preprocess all DecimalField fields
        for field in decimal_fields:
            value = getattr(self, field, None)
            try:
                setattr(self, field, self.preprocess_value(value))
            except ValueError as e:
                raise ValueError(f"Error processing field '{field}': {e}")
    
        # Call the parent class save method
        super().save(*args, **kwargs)


    def __str__(self):
        return self.campaign_name
    
    def Meta(self):
        db_table = "First_step_SP_Ads_AMZ"


class First_step_SB_Ads_AMZ(models.Model):

    date = models.DateField(null=True, blank=True)
    portfolio_name = models.CharField(max_length=100, null=True)
    currency = models.CharField(max_length=50, null=True)
    campaign_name = models.CharField(max_length=250, null=True)
    cost_type = models.CharField(max_length=10, null=True)
    country = models.CharField(max_length=50, null=True)
    impressions = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    clicks = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    ctr = models.DecimalField(max_digits=5, decimal_places=4, null=True)
    cpc = models.DecimalField(max_digits=5, decimal_places=4, null=True)
    spend = models.DecimalField(max_digits=10, decimal_places=3, null=True)
    total_advertising_cost_of_sales = models.DecimalField(max_digits=6, decimal_places=4, null=True)
    total_return_on_advertising_spend = models.DecimalField(max_digits=6, decimal_places=4, null=True)
    day_14_total_sales = models.DecimalField(max_digits=10, decimal_places=5, null=True)
    day_14_total_orders = models.DecimalField(max_digits=10, decimal_places=4, null=True)
    day_14_total_units = models.DecimalField(max_digits=10, decimal_places=4, null=True)
    day_14_conversion_rate = models.DecimalField(max_digits=10, decimal_places=5, null=True)
    viewable_impressions = models.DecimalField(max_digits=10, decimal_places=4, null=True)
    cost_per_1000_viewable_impressions = models.DecimalField(max_digits=10, decimal_places=5, null=True)
    view_through_rate = models.DecimalField(max_digits=8, decimal_places=4, null=True)
    click_through_rate_for_views = models.DecimalField(max_digits=10, decimal_places=4, null=True)
    video_first_quartile_views = models.DecimalField(max_digits=10, decimal_places=5)
    video_midpoint_views = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    video_third_quartile_views = models.DecimalField(max_digits=10, decimal_places=4, null=True)
    video_complete_views = models.DecimalField(max_digits=10, decimal_places=4, null=True)
    video_unmutes = models.DecimalField(max_digits=10, decimal_places=4, null=True)
    seconds_5_views = models.DecimalField(max_digits=10, decimal_places=4, null=True)
    seconds_5_view_rate = models.DecimalField(max_digits=10, decimal_places=4, null=True)
    day_14_branded_searches = models.DecimalField(max_digits=10, decimal_places=4, null=True)
    day_14_detail_page_views = models.DecimalField(max_digits=10, decimal_places=4, null=True)
    day_14_new_to_brand_orders = models.DecimalField(max_digits=10, decimal_places=4, null=True)
    day_14_percent_of_orders_new_to_brand = models.DecimalField(max_digits=10, decimal_places=4, null=True)
    day_14_new_to_brand_sales = models.DecimalField(max_digits=10, decimal_places=5, null=True)
    day_14_percent_of_sales_new_to_brand = models.DecimalField(max_digits=10, decimal_places=4, null=True)
    day_14_new_to_brand_units = models.DecimalField(max_digits=10, decimal_places=4, null=True)
    day_14_percent_of_units_new_to_brand = models.DecimalField(max_digits=10, decimal_places=4, null=True)
    day_14_new_to_brand_order_rate = models.DecimalField(max_digits=10, decimal_places=4, null=True)
    total_advertising_cost_of_sales_clicks = models.DecimalField(max_digits=10, decimal_places=4, null=True)
    total_return_on_advertising_spend_clicks = models.DecimalField(max_digits=10, decimal_places=4, null=True)
    day_14_total_sales_clicks = models.DecimalField(max_digits=10, decimal_places=4, null=True)
    day_14_total_orders_clicks = models.DecimalField(max_digits=10, decimal_places=4, null=True)
    day_14_total_units_clicks = models.DecimalField(max_digits=10, decimal_places=4, null=True)
    new_to_brand_detail_page_views = models.DecimalField(max_digits=10, decimal_places=4, null=True)
    new_to_brand_detail_page_view_click_through_conversions = models.DecimalField(max_digits=10, decimal_places=4, null=True)
    new_to_brand_detail_page_view_rate = models.DecimalField(max_digits=10, decimal_places=4, null=True)
    effective_cost_per_new_to_brand_detail_page_view = models.DecimalField(max_digits=10, decimal_places=4, null=True)
    day_14_atc = models.DecimalField(max_digits=10, decimal_places=4, null=True)
    day_14_atc_clicks = models.DecimalField(max_digits=10, decimal_places=4, null=True)
    day_14_atcr = models.DecimalField(max_digits=10, decimal_places=4, null=True)
    effective_cost_per_add_to_cart = models.DecimalField(max_digits=10, decimal_places=4, null=True)
    branded_searches_click_through_conversions = models.DecimalField(max_digits=10, decimal_places=4, null=True)
    branded_searches_rate = models.DecimalField(max_digits=10, decimal_places=4, null=True)
    effective_cost_per_branded_search = models.DecimalField(max_digits=10, decimal_places=4, null=True)
    long_term_sales = models.DecimalField(max_digits=10, decimal_places=4, null=True)
    long_term_roas = models.DecimalField(max_digits=10, decimal_places=4, null=True)


    def save(self, *args, **kwargs):
        # Convert the date if it is a string in the format "Dec 01, 2024"
        if isinstance(self.date, str):
            try:
                # Parse the date using the format "Dec 01, 2024"
                self.date = datetime.strptime(self.date.strip(), '%b %d, %Y').date()
            except ValueError as e:
                raise ValueError(f"Invalid date format: {self.date}. Expected format: Dec 01, 2024.") from e
        
        # List of all DecimalField fields
        decimal_fields = [
            'impressions',
            'clicks',
            'ctr',
            'cpc',
            'spend',
            'total_advertising_cost_of_sales',
            'total_return_on_advertising_spend',
            'day_14_total_sales',
            'day_14_total_orders',
            'day_14_total_units',
            'day_14_conversion_rate',
            'viewable_impressions',
            'cost_per_1000_viewable_impressions',
            'view_through_rate',
            'click_through_rate_for_views',
            'video_first_quartile_views',
            'video_midpoint_views',
            'video_third_quartile_views',
            'video_complete_views',
            'video_unmutes',
            'seconds_5_views',
            'seconds_5_view_rate',
            'day_14_branded_searches',
            'day_14_detail_page_views',
            'day_14_new_to_brand_orders',
            'day_14_percent_of_orders_new_to_brand',
            'day_14_new_to_brand_sales',
            'day_14_percent_of_sales_new_to_brand',
            'day_14_new_to_brand_units',
            'day_14_percent_of_units_new_to_brand',
            'day_14_new_to_brand_order_rate',
            'total_advertising_cost_of_sales_clicks',
            'total_return_on_advertising_spend_clicks',
            'day_14_total_sales_clicks',
            'day_14_total_orders_clicks',
            'day_14_total_units_clicks',
            'new_to_brand_detail_page_views',
            'new_to_brand_detail_page_view_click_through_conversions',
            'new_to_brand_detail_page_view_rate',
            'effective_cost_per_new_to_brand_detail_page_view',
            'day_14_atc',
            'day_14_atc_clicks',
            'day_14_atcr',
            'effective_cost_per_add_to_cart',
            'branded_searches_click_through_conversions',
            'branded_searches_rate',
            'effective_cost_per_branded_search',
            'long_term_sales',
            'long_term_roas',

        ]

        # Convert NaN or None to Decimal(0) for all DecimalField fields
        for field in decimal_fields:
            value = getattr(self, field, None)
            if value is None or str(value).lower() == 'nan':
                setattr(self, field, Decimal(0))

        super().save(*args, **kwargs)



    def __str__(self):
        return self.campaign_name
    
    def Meta(self):
        db_table = "First_step_SB_Ads_AMZ"


class First_step_SD_Ads_AMZ(models.Model):
    date = models.DateField(null=True, blank=True)
    portfolio_name = models.CharField(max_length=100, null=True)
    currency = models.CharField(max_length=25, null=True)
    campaign_name = models.CharField(max_length=100, null=True)
    cost_type = models.CharField(max_length=100, null=True)
    ad_group_name = models.CharField(max_length=100, null=True)
    targeting = models.CharField(max_length=100, null=True)
    bid_optimization = models.CharField(max_length=100, null=True)
    impressions = models.DecimalField(max_digits=10, decimal_places=4, null=True)
    viewable_impressions = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    clicks = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    ctr = models.DecimalField(max_digits=5, decimal_places=5, null=True)
    day_14_detail_page_views = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    spend = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    cpc = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    cost_per_1000_viewable_impressions = models.DecimalField(max_digits=8, decimal_places=4, null=True)
    total_advertising_cost_of_sales = models.DecimalField(max_digits=6, decimal_places=4, null=True)
    total_return_on_advertising_spend = models.DecimalField(max_digits=8, decimal_places=4, null=True)
    day_14_total_orders = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    day_14_total_units = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    day_14_total_sales = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    day_14_new_to_brand_orders = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    day_14_new_to_brand_sales = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    day_14_new_to_brand_units = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    total_advertising_cost_of_sales_clicks = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    total_return_on_advertising_spend_click = models.DecimalField(max_digits=4, decimal_places=2, null=True)
    day_14_total_orders_click = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    day_14_total_units_click = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    day_14_total_sales_click = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    day_14_new_to_brand_orders_click = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    day_14_new_to_brand_sales_click = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    day_14_new_to_brand_units_click = models.DecimalField(max_digits=5, decimal_places=2, null=True)

    def __str__(self):
        return self.campaign_name
    
    class Meta:
        db_table = "First_step_SD_Ads_AMZ"


class First_step_ReturnData_AMZ(models.Model):

    order_id = models.CharField(max_length=20)
    order_date = models.DateField(null=True, blank=True)
    return_request_date = models.DateField(null=True, blank=True)
    return_request_status = models.CharField(max_length=25)
    amazon_rma_id = models.CharField(max_length=20)
    seller_rma_id = models.CharField(max_length=20)
    label_type = models.CharField(max_length=30)
    label_cost = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    currency_code = models.CharField(max_length=5)
    return_carrier = models.CharField(max_length=50)
    tracking_id = models.CharField(max_length=30)
    label_to_be_paid_by = models.CharField(max_length=15)
    a_to_z_claim = models.CharField(max_length=3)
    is_prime = models.CharField(max_length=3)
    asin = models.CharField(max_length=20)
    merchant_sku = models.CharField(max_length=20)
    item_name = models.CharField(max_length=500)
    return_quantity = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    return_reason = models.CharField(max_length=100)
    in_policy = models.CharField(max_length=3)
    return_type = models.CharField(max_length=20)
    resolution = models.CharField(max_length=20)
    invoice_number = models.CharField(max_length=20)
    return_delivery_date = models.DateField(null=True, blank=True)
    order_amount = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    order_quantity = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    safet_action_reason = models.CharField(max_length=100)
    safet_claim_id = models.CharField(max_length=20)
    safet_claim_status = models.CharField(max_length=20)
    safet_claim_creation_time = models.DateTimeField(null=True, blank=True)
    safet_claim_reimbursement_amount = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    refund_amount = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    category = models.CharField(max_length=50)


    
    def __str__(self):
        return self.order_id
    
    class Meta:
        db_table = "First_step_ReturnData_AMZ"




""""Flipkart data models start here"""

class First_step_SalesData_FK(models.Model):
    seller_gstin = models.CharField(max_length=500)
    order_id = models.CharField(max_length=255)
    order_item_id = models.CharField(max_length=255)
    product_title = models.CharField(max_length=500)

    fsn = models.CharField(max_length=255)
    sku = models.CharField(max_length=255)


    hsn_code = models.CharField(max_length=255)
    event_type = models.CharField(max_length=255)
    event_sub_type = models.CharField(max_length=255)
    order_type = models.CharField(max_length=255)
    fulfilment_type = models.CharField(max_length=255)

    order_date = models.DateTimeField(blank=True, null=True)
    order_approval_date = models.DateTimeField(blank=True, null=True)

    item_quantity = models.DecimalField(max_digits=10, decimal_places=2)

    order_shipped_from_state = models.CharField(max_length=255)
    warehouse_id = models.CharField(max_length=255)

    price_before_discount = models.DecimalField(max_digits=10, decimal_places=2)
    total_discount = models.DecimalField(max_digits=10, decimal_places=2)
    seller_share = models.DecimalField(max_digits=10, decimal_places=2)
    bank_offer_share = models.DecimalField(max_digits=10, decimal_places=2)
    price_after_discount = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_charges = models.DecimalField(max_digits=10, decimal_places=2)
    final_invoice_amount = models.DecimalField(max_digits=10, decimal_places=2)
    type_of_tax = models.DecimalField(max_digits=10, decimal_places=2)
    taxable_value = models.DecimalField(max_digits=10, decimal_places=2)
    cst_rate = models.DecimalField(max_digits=10, decimal_places=2)
    cst_amount = models.DecimalField(max_digits=10, decimal_places=2)
    vat_rate = models.DecimalField(max_digits=10, decimal_places=2)
    vat_amount = models.DecimalField(max_digits=10, decimal_places=2)
    luxury_cess_rate = models.DecimalField(max_digits=10, decimal_places=2)
    luxury_cess_amount = models.DecimalField(max_digits=10, decimal_places=2)
    igst_rate = models.DecimalField(max_digits=10, decimal_places=2)
    igst_amount = models.DecimalField(max_digits=10, decimal_places=2)
    cgst_rate = models.DecimalField(max_digits=10, decimal_places=2)
    cgst_amount = models.DecimalField(max_digits=10, decimal_places=2)
    sgst_rate = models.DecimalField(max_digits=10, decimal_places=2)
    sgst_amount = models.DecimalField(max_digits=10, decimal_places=2)
    tcs_igst_rate = models.DecimalField(max_digits=10, decimal_places=2)
    tcs_igst_amount = models.DecimalField(max_digits=10, decimal_places=2)
    tcs_cgst_rate = models.DecimalField(max_digits=10, decimal_places=2)
    tcs_cgst_amount = models.DecimalField(max_digits=10, decimal_places=2)
    tcs_sgst_rate = models.DecimalField(max_digits=10, decimal_places=2)
    tcs_sgst_amount = models.DecimalField(max_digits=10, decimal_places=2)
    total_tcs_deducted = models.DecimalField(max_digits=10, decimal_places=2)

    buyer_invoice_id = models.CharField(max_length=255)

    buyer_invoice_date = models.DateTimeField(blank=True, null=True)

    buyer_invoive_amount = models.DecimalField(max_digits=10, decimal_places=2)
    customer_billing_pincode = models.CharField(max_length=255)
    customer_billing_state = models.CharField(max_length=255)
    customer_delivery_pincode = models.CharField(max_length=255)
    customer_delivery_state = models.CharField(max_length=255)

    usual_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    is_shopsy_order = models.CharField(max_length=255)
    tds_rate = models.DecimalField(max_digits=10, decimal_places=2)
    tds_amount = models.DecimalField(max_digits=10, decimal_places=2)

    # Data pre-processing of SKU and FSN column that removes '"""' from start and end
    def save(self, *args, **kwargs):
        # Strip leading and trailing quotes from SKU and FSN before saving
        if self.sku:
            self.sku = self.sku.strip('"""')
            if self.sku.startswith("SKU:"):
                self.sku = self.sku[4:].strip()
        if self.fsn:
            self.fsn = self.fsn.strip('"""')
        super().save(*args, **kwargs)

    def __str__(self):
        return self.fsn
    
    class Meta:
        db_table = "First_step_SalesData_FK"  # Explicitly set the table name


class First_step_cogs_vertical(models.Model):

    sku = models.CharField(max_length=255)
    pid = models.CharField(max_length=255)
    vertical = models.CharField(max_length=255)
    mrp = models.DecimalField(max_digits=10, decimal_places=2)
    cogs = models.DecimalField(max_digits=10, decimal_places=2)


    def __str__(self):
        return self.sku
    
    class Meta:
        db_table = "First_step_cogs_vertical"  # Explicitly set the table name


class First_step_InvoiceData_FK(models.Model):

    service_type = models.CharField(max_length=255)
    order_item_id = models.CharField(max_length=255)
    recall_id = models.CharField(max_length=255)
    warehouse_state_code = models.CharField(max_length=255)
    fee_name = models.CharField(max_length=255)
    total_fee_amount = models.DecimalField(max_digits=10, decimal_places=2)
    fee_amount = models.DecimalField(max_digits=10, decimal_places=2)
    fee_waiver_amount = models.DecimalField(max_digits=10, decimal_places=2)
    cgst_rate = models.DecimalField(max_digits=10, decimal_places=2)
    sgst_rate = models.DecimalField(max_digits=10, decimal_places=2)
    igst_rate = models.DecimalField(max_digits=10, decimal_places=2)
    cgst_amount = models.DecimalField(max_digits=10, decimal_places=2)
    sgst_amount = models.DecimalField(max_digits=10, decimal_places=2)
    igst_amount = models.DecimalField(max_digits=10, decimal_places=2)
    total_tax_amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(null=True)

    def __str__(self):
        return self.fee_name
    
    class Meta:
        db_table = "First_step_invoice_FK"  # Explicitly set the table name


class First_step_AdsData_FK(models.Model):

    campaign_id = models.CharField(max_length=255)
    campaign_name = models.CharField(max_length=255)
    ad_group_id = models.CharField(max_length=255)
    ad_group_name = models.CharField(max_length=255)
    date = models.DateField(null=True)
    views = models.DecimalField(max_digits=10, decimal_places=2)
    clicks = models.DecimalField(max_digits=10, decimal_places=2)
    ctr = models.DecimalField(max_digits=10, decimal_places=2)
    cvr = models.DecimalField(max_digits=10, decimal_places=2)
    ad_spend = models.DecimalField(max_digits=10, decimal_places=2)
    units_sold_direct = models.DecimalField(max_digits=10, decimal_places=2)
    units_sold_indirect = models.DecimalField(max_digits=10, decimal_places=2)
    direct_revenue = models.DecimalField(max_digits=10, decimal_places=2)
    indirect_revenue = models.DecimalField(max_digits=10, decimal_places=2)
    roi_direct = models.DecimalField(max_digits=10, decimal_places=2)
    roi_indirect = models.DecimalField(max_digits=10, decimal_places=2)


    def __str__(self):
        return self.campaign_name
    
    class Meta:
        db_table = "First_step_AdsData_FK"  # Explicitly set the table name


class First_step_Master_SKU(models.Model):
    
    sku = models.CharField(max_length=255, null=True)
    product_title = models.CharField(max_length=500, null=True)
    ean = models.CharField(max_length=200, null=True)
    length = models.CharField(max_length=25, null=True)
    breadth = models.CharField(max_length=25, null=True)
    height = models.CharField(max_length=25, null=True)
    weight = models.CharField(max_length=25, null=True)
    fk_platform_sku = models.CharField(max_length=300, null=True)
    fk_fsn = models.CharField(max_length=255, null=True)
    amazon_platform_sku = models.CharField(max_length=255, null=True)
    amazon_asin = models.CharField(max_length=255, null=True)
    first_cry_platform_sku = models.CharField(max_length=255, null=True)
    first_cry_product_id = models.CharField(max_length=255, null=True)
    myntra_platformsku = models.CharField(max_length=255, null=True)
    myntra_product_id = models.CharField(max_length=255, null=True)
    jiomart_platform_sku = models.CharField(max_length=255, null=True)
    jiomart_product_id = models.CharField(max_length=255, null=True)
    meesho_platform_sku = models.CharField(max_length=255, null=True)
    meesho_product_id = models.CharField(max_length=255, null=True)
    pharmeasy_platform_sku = models.CharField(max_length=255, null=True)
    pharmeasy_product_id = models.CharField(max_length=255, null=True)
    rk_world_platform_sku = models.CharField(max_length=255, null=True)
    rk_world_product_id = models.CharField(max_length=255, null=True)
    mrp = models.CharField(max_length=25, null=True)
    gst = models.CharField(max_length=25, null=True)
    hsn = models.CharField(max_length=255, null=True)
    cogs = models.CharField(max_length=25, null=True)
    product_vertical = models.CharField(max_length=255, null=True)

    def __str__(self):
        return self.product_title
    
    class Meta:
        db_table = "First_step_Master_sku"  # Explicitly set the table name


class First_step_FK_Return_data(models.Model):

    return_id = models.CharField(max_length=100)
    order_item_id = models.CharField(max_length=100)
    fulfilment_type = models.CharField(max_length=25)
    # return_requested_date = models.DateField(null=True)
    # return_approval_date = models.DateField(null=True)
    return_status = models.CharField(max_length=100)
    return_reason = models.CharField(max_length=500)
    return_sub_reason = models.CharField(max_length=500)
    return_type = models.CharField(max_length=100)
    return_result = models.CharField(max_length=100)
    return_expectation = models.CharField(max_length=100)
    reverse_logistics_tracking_id = models.CharField(max_length=100)
    sku = models.CharField(max_length=100)
    fsn = models.CharField(max_length=100)
    product_title = models.CharField(max_length=500)
    quantity = models.DecimalField(max_digits=5, decimal_places=2)
    return_completion_type = models.CharField(max_length=100)
    primary_pv_output = models.CharField(max_length=100)
    detailed_pv_output = models.CharField(max_length=100)
    final_condition_of_returned_product = models.CharField(max_length=100)
    tech_visit_sla = models.CharField(max_length=100)
    # tech_visit_by_date = models.DateField(null=True)
    # tech_visit_completion_datetime = models.DateTimeField(null=True)
    tech_visit_completion_breach = models.CharField(max_length=100)
    return_completion_sla = models.CharField(max_length=100)
    # return_complete_by_date = models.DateField(null=True)
    # return_completion_date = models.DateField(null=True)
    return_completion_breach = models.CharField(max_length=100)
    # return_cancellation_date = models.DateField(null=True)
    return_cancellation_reason = models.CharField(max_length=500)

    def save(self, *args, **kwargs):
        # Remove prefixes
        self.sku = self.sku.replace("SKU:", "").strip()
        self.return_id = self.return_id.replace("RI:", "").strip()
        self.order_item_id = self.order_item_id.replace("OI:", "").strip()

        # datetime_obj = datetime.strptime(self.return_approval_date, "%y-%m-%d %H:%M:%S.%f")
        # self.return_approval_date = datetime_obj.strftime("%y-%m-%d %H:%M:%S")

        # date_obj = datetime.strptime(self.return_completion_date, "%d/%m/%Y")
        # self.return_completion_date = date_obj.strftime("%y-%m-%d")

        super().save(*args, **kwargs)

    def __str__(self):
        return self.order_item_id

    class Meta:
        db_table = "First_step_FK_Return_data"




"""For Jr Sr database"""

class Jr_Sr_SalesData_FK(models.Model):
    seller_gstin = models.CharField(max_length=500)
    order_id = models.CharField(max_length=255)
    order_item_id = models.CharField(max_length=255)
    product_title = models.CharField(max_length=500)

    fsn = models.CharField(max_length=255)
    sku = models.CharField(max_length=255)


    hsn_code = models.CharField(max_length=255)
    event_type = models.CharField(max_length=255)
    event_sub_type = models.CharField(max_length=255)
    order_type = models.CharField(max_length=255)
    fulfilment_type = models.CharField(max_length=255)

    order_date = models.DateTimeField(blank=True, null=True)
    order_approval_date = models.DateTimeField(blank=True, null=True)

    item_quantity = models.DecimalField(max_digits=10, decimal_places=2)

    order_shipped_from_state = models.CharField(max_length=255)
    warehouse_id = models.CharField(max_length=255)

    price_before_discount = models.DecimalField(max_digits=10, decimal_places=2)
    total_discount = models.DecimalField(max_digits=10, decimal_places=2)
    seller_share = models.DecimalField(max_digits=10, decimal_places=2)
    bank_offer_share = models.DecimalField(max_digits=10, decimal_places=2)
    price_after_discount = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_charges = models.DecimalField(max_digits=10, decimal_places=2)
    final_invoice_amount = models.DecimalField(max_digits=10, decimal_places=2)
    type_of_tax = models.DecimalField(max_digits=10, decimal_places=2)
    taxable_value = models.DecimalField(max_digits=10, decimal_places=2)
    cst_rate = models.DecimalField(max_digits=10, decimal_places=2)
    cst_amount = models.DecimalField(max_digits=10, decimal_places=2)
    vat_rate = models.DecimalField(max_digits=10, decimal_places=2)
    vat_amount = models.DecimalField(max_digits=10, decimal_places=2)
    luxury_cess_rate = models.DecimalField(max_digits=10, decimal_places=2)
    luxury_cess_amount = models.DecimalField(max_digits=10, decimal_places=2)
    igst_rate = models.DecimalField(max_digits=10, decimal_places=2)
    igst_amount = models.DecimalField(max_digits=10, decimal_places=2)
    cgst_rate = models.DecimalField(max_digits=10, decimal_places=2)
    cgst_amount = models.DecimalField(max_digits=10, decimal_places=2)
    sgst_rate = models.DecimalField(max_digits=10, decimal_places=2)
    sgst_amount = models.DecimalField(max_digits=10, decimal_places=2)
    tcs_igst_rate = models.DecimalField(max_digits=10, decimal_places=2)
    tcs_igst_amount = models.DecimalField(max_digits=10, decimal_places=2)
    tcs_cgst_rate = models.DecimalField(max_digits=10, decimal_places=2)
    tcs_cgst_amount = models.DecimalField(max_digits=10, decimal_places=2)
    tcs_sgst_rate = models.DecimalField(max_digits=10, decimal_places=2)
    tcs_sgst_amount = models.DecimalField(max_digits=10, decimal_places=2)
    total_tcs_deducted = models.DecimalField(max_digits=10, decimal_places=2)

    buyer_invoice_id = models.CharField(max_length=255)

    buyer_invoice_date = models.DateTimeField(blank=True, null=True)

    buyer_invoive_amount = models.DecimalField(max_digits=10, decimal_places=2)
    customer_billing_pincode = models.CharField(max_length=255)
    customer_billing_state = models.CharField(max_length=255)
    customer_delivery_pincode = models.CharField(max_length=255)
    customer_delivery_state = models.CharField(max_length=255)

    usual_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    is_shopsy_order = models.CharField(max_length=255)
    tds_rate = models.DecimalField(max_digits=10, decimal_places=2)
    tds_amount = models.DecimalField(max_digits=10, decimal_places=2)

    # Data pre-processing of SKU and FSN column that removes '"""' from start and end
    def save(self, *args, **kwargs):
        # Strip leading and trailing quotes from SKU and FSN before saving
        if self.sku:
            self.sku = self.sku.strip('"""')
            if self.sku.startswith("SKU:"):
                self.sku = self.sku[4:].strip()
        if self.fsn:
            self.fsn = self.fsn.strip('"""')
        super().save(*args, **kwargs)

    def __str__(self):
        return self.fsn
    
    class Meta:
        db_table = "Jr_Sr_SalesData_FK"  # Explicitly set the table name


class Jr_Sr_AdsData_FK_MP(models.Model):

    campaign_id = models.CharField(max_length=150)
    campaign_name = models.CharField(max_length=300)
    date = models.DateField(null=True, blank=True)
    ad_spend = models.DecimalField(max_digits=10, decimal_places=2)
    views = models.DecimalField(max_digits=9, decimal_places=2)
    clicks = models.DecimalField(max_digits=9, decimal_places=2)
    total_converted_units = models.DecimalField(max_digits=5, decimal_places=2)
    total_revenue = models.DecimalField(max_digits=10, decimal_places=2)
  
    def __str__(self):
        return self.campaign_name
    
    class Meta:
        db_table = "Jr_Sr_AdsData_FK_MP"  # Explicitly set the table name


class Jr_Sr_InvoiceData_FK(models.Model):
    
    service_type = models.CharField(max_length=255)
    order_item_id = models.CharField(max_length=255)
    recall_id = models.CharField(max_length=255)
    warehouse_state_code = models.CharField(max_length=255)
    fee_name = models.CharField(max_length=255)
    total_fee_amount = models.DecimalField(max_digits=10, decimal_places=2)
    fee_amount = models.DecimalField(max_digits=10, decimal_places=2)
    fee_waiver_amount = models.DecimalField(max_digits=10, decimal_places=2)
    cgst_rate = models.DecimalField(max_digits=10, decimal_places=2)
    sgst_rate = models.DecimalField(max_digits=10, decimal_places=2)
    igst_rate = models.DecimalField(max_digits=10, decimal_places=2)
    cgst_amount = models.DecimalField(max_digits=10, decimal_places=2)
    sgst_amount = models.DecimalField(max_digits=10, decimal_places=2)
    igst_amount = models.DecimalField(max_digits=10, decimal_places=2)
    total_tax_amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(null=True)

    def __str__(self):
        return self.fee_name
    
    class Meta:
        db_table = "Jr_Sr_InvoiceData_FK"  # Explicitly set the table name

class Jr_Sr_cogs_master_sku(models.Model):
    
    product_vertical = models.CharField(max_length=100)
    size = models.CharField(max_length=10)
    pack_size = models.DecimalField(max_digits=6, decimal_places=2)
    check_name = models.CharField(max_length=100)
    product_title = models.CharField(max_length=500)
    sku = models.CharField(max_length=100)
    fsn = models.CharField(max_length=100)
    lid = models.CharField(max_length=100)
    mrp = models.DecimalField(max_digits=6, decimal_places=2)
    settlement_per_unit = models.DecimalField(max_digits=6, decimal_places=2)
    cogs = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.product_vertical
    
    class Meta:
        db_table = "Jr_Sr_cogs_master_sku"


class Jr_Sr_cogs(models.Model):
    product_title = models.CharField(max_length=300)
    sku = models.CharField(max_length=100)
    mrp = models.DecimalField(max_digits=10, decimal_places=2)
    settlement_per_unit = models.DecimalField(max_digits=5, decimal_places=2)
    cogs = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.sku
    
    class Meta:
        db_table = "Jr_Sr_cogs"



class Jr_Sr_FK_Return_data(models.Model):

    return_id = models.CharField(max_length=100)
    order_item_id = models.CharField(max_length=100)
    fulfilment_type = models.CharField(max_length=25)
    # return_requested_date = models.DateField(null=True)
    # return_approval_date = models.DateField(null=True)
    return_status = models.CharField(max_length=100)
    return_reason = models.CharField(max_length=500)
    return_sub_reason = models.CharField(max_length=500)
    return_type = models.CharField(max_length=100)
    return_result = models.CharField(max_length=100)
    return_expectation = models.CharField(max_length=100)
    reverse_logistics_tracking_id = models.CharField(max_length=100)
    sku = models.CharField(max_length=100)
    fsn = models.CharField(max_length=100)
    product_title = models.CharField(max_length=500)
    quantity = models.DecimalField(max_digits=5, decimal_places=2)
    return_completion_type = models.CharField(max_length=100)
    primary_pv_output = models.CharField(max_length=100)
    detailed_pv_output = models.CharField(max_length=100)
    final_condition_of_returned_product = models.CharField(max_length=100)
    tech_visit_sla = models.CharField(max_length=100)
    # tech_visit_by_date = models.DateField(null=True)
    # tech_visit_completion_datetime = models.DateTimeField(null=True)
    tech_visit_completion_breach = models.CharField(max_length=100)
    return_completion_sla = models.CharField(max_length=100)
    # return_complete_by_date = models.DateField(null=True)
    # return_completion_date = models.DateField(null=True)
    return_completion_breach = models.CharField(max_length=100)
    # return_cancellation_date = models.DateField(null=True)
    return_cancellation_reason = models.CharField(max_length=500)

    def save(self, *args, **kwargs):
        # Remove prefixes
        self.sku = self.sku.replace("SKU:", "").strip()
        self.return_id = self.return_id.replace("RI:", "").strip()
        self.order_item_id = self.order_item_id.replace("OI:", "").strip()

        # datetime_obj = datetime.strptime(self.return_approval_date, "%y-%m-%d %H:%M:%S.%f")
        # self.return_approval_date = datetime_obj.strftime("%y-%m-%d %H:%M:%S")

        # date_obj = datetime.strptime(self.return_completion_date, "%d/%m/%Y")
        # self.return_completion_date = date_obj.strftime("%y-%m-%d")

        super().save(*args, **kwargs)

    def __str__(self):
        return self.order_item_id

    class Meta:
        db_table = "Jr_Sr_FK_Return_data"

"""NexTen Brands"""

class NexTen_SalesData_FK(models.Model):
    seller_gstin = models.CharField(max_length=500)
    order_id = models.CharField(max_length=255)
    order_item_id = models.CharField(max_length=255)
    product_title = models.CharField(max_length=500)

    fsn = models.CharField(max_length=255)
    sku = models.CharField(max_length=255)


    hsn_code = models.CharField(max_length=255)
    event_type = models.CharField(max_length=255)
    event_sub_type = models.CharField(max_length=255)
    order_type = models.CharField(max_length=255)
    fulfilment_type = models.CharField(max_length=255)

    order_date = models.DateTimeField(blank=True, null=True)
    order_approval_date = models.DateTimeField(blank=True, null=True)

    item_quantity = models.DecimalField(max_digits=10, decimal_places=2)

    order_shipped_from_state = models.CharField(max_length=255)
    warehouse_id = models.CharField(max_length=255)

    price_before_discount = models.DecimalField(max_digits=10, decimal_places=2)
    total_discount = models.DecimalField(max_digits=10, decimal_places=2)
    seller_share = models.DecimalField(max_digits=10, decimal_places=2)
    bank_offer_share = models.DecimalField(max_digits=10, decimal_places=2)
    price_after_discount = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_charges = models.DecimalField(max_digits=10, decimal_places=2)
    final_invoice_amount = models.DecimalField(max_digits=10, decimal_places=2)
    type_of_tax = models.DecimalField(max_digits=10, decimal_places=2)
    taxable_value = models.DecimalField(max_digits=10, decimal_places=2)
    cst_rate = models.DecimalField(max_digits=10, decimal_places=2)
    cst_amount = models.DecimalField(max_digits=10, decimal_places=2)
    vat_rate = models.DecimalField(max_digits=10, decimal_places=2)
    vat_amount = models.DecimalField(max_digits=10, decimal_places=2)
    luxury_cess_rate = models.DecimalField(max_digits=10, decimal_places=2)
    luxury_cess_amount = models.DecimalField(max_digits=10, decimal_places=2)
    igst_rate = models.DecimalField(max_digits=10, decimal_places=2)
    igst_amount = models.DecimalField(max_digits=10, decimal_places=2)
    cgst_rate = models.DecimalField(max_digits=10, decimal_places=2)
    cgst_amount = models.DecimalField(max_digits=10, decimal_places=2)
    sgst_rate = models.DecimalField(max_digits=10, decimal_places=2)
    sgst_amount = models.DecimalField(max_digits=10, decimal_places=2)
    tcs_igst_rate = models.DecimalField(max_digits=10, decimal_places=2)
    tcs_igst_amount = models.DecimalField(max_digits=10, decimal_places=2)
    tcs_cgst_rate = models.DecimalField(max_digits=10, decimal_places=2)
    tcs_cgst_amount = models.DecimalField(max_digits=10, decimal_places=2)
    tcs_sgst_rate = models.DecimalField(max_digits=10, decimal_places=2)
    tcs_sgst_amount = models.DecimalField(max_digits=10, decimal_places=2)
    total_tcs_deducted = models.DecimalField(max_digits=10, decimal_places=2)

    buyer_invoice_id = models.CharField(max_length=255)

    buyer_invoice_date = models.DateTimeField(blank=True, null=True)

    buyer_invoive_amount = models.DecimalField(max_digits=10, decimal_places=2)
    customer_billing_pincode = models.CharField(max_length=255)
    customer_billing_state = models.CharField(max_length=255)
    customer_delivery_pincode = models.CharField(max_length=255)
    customer_delivery_state = models.CharField(max_length=255)

    usual_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    is_shopsy_order = models.CharField(max_length=255)
    tds_rate = models.DecimalField(max_digits=10, decimal_places=2)
    tds_amount = models.DecimalField(max_digits=10, decimal_places=2)

    # Data pre-processing of SKU and FSN column that removes '"""' from start and end
    def save(self, *args, **kwargs):
        # Strip leading and trailing quotes from SKU and FSN before saving
        if self.sku:
            self.sku = self.sku.strip('"""')
            if self.sku.startswith("SKU:"):
                self.sku = self.sku[4:].strip()
        if self.fsn:
            self.fsn = self.fsn.strip('"""')
        super().save(*args, **kwargs)

    def __str__(self):
        return self.fsn
    
    class Meta:
        db_table = "NexTen_SalesData_FK"  # Explicitly set the table name



class NexTen_AdsData_FK_MP(models.Model):
    
    campaign_id = models.CharField(max_length=150)
    campaign_name = models.CharField(max_length=300)
    date = models.DateField(null=True, blank=True)
    ad_spend = models.DecimalField(max_digits=10, decimal_places=2)
    views = models.DecimalField(max_digits=9, decimal_places=2)
    clicks = models.DecimalField(max_digits=9, decimal_places=2)
    total_converted_units = models.DecimalField(max_digits=5, decimal_places=2)
    total_revenue = models.DecimalField(max_digits=10, decimal_places=2)
  
    def __str__(self):
        return self.campaign_name
    
    class Meta:
        db_table = "NexTen_AdsData_FK_MP"  # Explicitly set the table name


class NexTen_InvoiceData_FK(models.Model):
    
    service_type = models.CharField(max_length=255)
    order_item_id = models.CharField(max_length=255)
    recall_id = models.CharField(max_length=255)
    warehouse_state_code = models.CharField(max_length=255)
    fee_name = models.CharField(max_length=255)
    total_fee_amount = models.DecimalField(max_digits=10, decimal_places=2)
    fee_amount = models.DecimalField(max_digits=10, decimal_places=2)
    fee_waiver_amount = models.DecimalField(max_digits=10, decimal_places=2)
    cgst_rate = models.DecimalField(max_digits=10, decimal_places=2)
    sgst_rate = models.DecimalField(max_digits=10, decimal_places=2)
    igst_rate = models.DecimalField(max_digits=10, decimal_places=2)
    cgst_amount = models.DecimalField(max_digits=10, decimal_places=2)
    sgst_amount = models.DecimalField(max_digits=10, decimal_places=2)
    igst_amount = models.DecimalField(max_digits=10, decimal_places=2)
    total_tax_amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(null=True)

    def __str__(self):
        return self.fee_name
    
    class Meta:
        db_table = "NexTen_InvoiceData_FK"  # Explicitly set the table name



class NexTen_COGS_Master_SKU(models.Model):

    product_title = models.CharField(max_length=500)
    sku = models.CharField(max_length=300)
    product_vertical = models.CharField(max_length=50)
    fsn = models.CharField(max_length=100)
    cogs = models.DecimalField(max_digits=5, decimal_places=2)
    brand = models.CharField(max_length=100)
    seller = models.CharField(max_length=100)

    def __str__(self):
        return self.product_vertical
    
    class Meta:
        db_table = "NexTen_COGS_Master_SKU" # Mentioning the Name of the database



class NexTen_Return_data(models.Model):

    return_id = models.CharField(max_length=100)
    order_item_id = models.CharField(max_length=100)
    fulfilment_type = models.CharField(max_length=25)
    # return_requested_date = models.DateField(null=True)
    # return_approval_date = models.DateField(null=True)
    return_status = models.CharField(max_length=100)
    return_reason = models.CharField(max_length=500)
    return_sub_reason = models.CharField(max_length=500)
    return_type = models.CharField(max_length=100)
    return_result = models.CharField(max_length=100)
    return_expectation = models.CharField(max_length=100)
    reverse_logistics_tracking_id = models.CharField(max_length=100)
    sku = models.CharField(max_length=100)
    fsn = models.CharField(max_length=100)
    product_title = models.CharField(max_length=500)
    quantity = models.DecimalField(max_digits=5, decimal_places=2)
    return_completion_type = models.CharField(max_length=100)
    primary_pv_output = models.CharField(max_length=100)
    detailed_pv_output = models.CharField(max_length=100)
    final_condition_of_returned_product = models.CharField(max_length=100)
    tech_visit_sla = models.CharField(max_length=100)
    # tech_visit_by_date = models.DateField(null=True)
    # tech_visit_completion_datetime = models.DateTimeField(null=True)
    tech_visit_completion_breach = models.CharField(max_length=100)
    return_completion_sla = models.CharField(max_length=100)
    # return_complete_by_date = models.DateField(null=True)
    # return_completion_date = models.DateField(null=True)
    return_completion_breach = models.CharField(max_length=100)
    # return_cancellation_date = models.DateField(null=True)
    return_cancellation_reason = models.CharField(max_length=500)

    def save(self, *args, **kwargs):
        # Remove prefixes
        self.sku = self.sku.replace("SKU:", "").strip()
        self.return_id = self.return_id.replace("RI:", "").strip()
        self.order_item_id = self.order_item_id.replace("OI:", "").strip()

        # datetime_obj = datetime.strptime(self.return_approval_date, "%y-%m-%d %H:%M:%S.%f")
        # self.return_approval_date = datetime_obj.strftime("%y-%m-%d %H:%M:%S")

        # date_obj = datetime.strptime(self.return_completion_date, "%d/%m/%Y")
        # self.return_completion_date = date_obj.strftime("%y-%m-%d")

        super().save(*args, **kwargs)

    def __str__(self):
        return self.order_item_id

    class Meta:
        db_table = "NexTen_Return_data"





    


    

# This database is created for the reason of keeping track of uploaded files in the database
class UploadedFileTracker(models.Model):
    file_name = models.CharField(max_length=500, unique=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file_name

    class Meta:
        db_table = "list_of_files_uploaded"


