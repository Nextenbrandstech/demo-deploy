# backend/admin.py
from django.contrib import admin

from .models import (First_step_SalesData_AMZ, First_step_CODBFeesData_AMZ, First_step_SP_Ads_AMZ, First_step_SB_Ads_AMZ, 
                     First_step_SD_Ads_AMZ, First_step_ReturnData_AMZ,
                     First_step_SalesData_FK , First_step_cogs_vertical, First_step_InvoiceData_FK, First_step_AdsData_FK, First_step_Master_SKU, First_step_FK_Return_data,
                     UploadedFileTracker, 
                     Jr_Sr_AdsData_FK_MP, Jr_Sr_InvoiceData_FK, Jr_Sr_SalesData_FK, Jr_Sr_cogs_master_sku, Jr_Sr_cogs, Jr_Sr_FK_Return_data,
                     NexTen_AdsData_FK_MP, NexTen_COGS_Master_SKU, NexTen_InvoiceData_FK, NexTen_SalesData_FK, NexTen_Return_data) # Import your model


"""Registering the models for Amazon Platform"""

@admin.register(First_step_SalesData_AMZ)
class First_step_SalesData_AMZAdmin(admin.ModelAdmin):
    list_display = (
        'seller_gstin',
        'invoice_number',
        'invoice_date',
        'transaction_type',
        'order_id',
        'shipment_id',
        'shipment_date',
        'order_date',
        'shipment_item_id',
        'quantity',
        'item_description',
        'asin',
        'hsn_or_sac',
        'sku',
        'product_tax_code',
        'bill_from_city',
        'bill_from_state',
        'bill_from_country',
        'bill_from_postal_code',
        'ship_from_city',
        'ship_from_state',
        'ship_from_country',
        'ship_from_postal_code',
        'ship_to_city',
        'ship_to_state',
        'ship_to_country',
        'ship_to_postal_code',
        'invoice_amount',
        'tax_exclusive_gross',
        'total_tax_amount',
        'cgst_rate',
        'sgst_rate',
        'utgst_rate',
        'igst_rate',
        'compensatory_cess_rate',
        'principal_amount',
        'principal_amount_basis',
        'cgst_tax',
        'sgst_tax',
        'utgst_tax',
        'igst_tax',
        'compensatory_cess_tax',
        'shipping_amount',
        'shipping_amount_basis',
        'shipping_cgst_tax',
        'shipping_sgst_tax',
        'shipping_utgst_tax',
        'shipping_igst_tax',
        'shipping_cess_tax_amount',
        'gift_wrap_amount',
        'gift_wrap_amount_basis',
        'gift_wrap_cgst_tax',
        'gift_wrap_sgst_tax',
        'gift_wrap_utgst_tax',
        'gift_wrap_igst_tax',
        'gift_wrap_compensatory_cess_tax',
        'item_promo_discount',
        'item_promo_discount_basis',
        'item_promo_tax',
        'shipping_promo_discount',
        'shipping_promo_discount_basis',
        'shipping_promo_tax',
        'gift_wrap_promo_discount',
        'gift_wrap_promo_discount_basis',
        'gift_wrap_promo_tax',
        'tcs_cgst_tax',
        'tcs_cgst_amount',
        'tcs_sgst_rate',
        'tcs_utgst_rate',
        'tcs_utgst_amount',
        'tcs_igst_rate',
        'tcs_igst_amount',
        'warehouse_id',
        'fulfillment_channel',
        'payment_method_code',
        'credit_note_no',
        'credit_note_date'
        
    )
    search_fields = ('sku', 'item_description')  # Fields to search in admin
    list_filter = ('invoice_date', 'sku')  # Filters for the admin

# This is "Selling Economics and Fees report" for the Amazon platform and covers all the CODB details
@admin.register(First_step_CODBFeesData_AMZ)
class First_step_CODBFeesData_AMZAdmin(admin.ModelAdmin):
    list_display = (
        'amazon_store',
        'start_date',
        'end_date',
        'parent_asin',
        'asin',
        'fnsku',
        'msku',
        'currency_code',
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
        'refund_commission_fee_total'
    )
    search_fields = ('asin', 'parent_asin')  # Fields to search in admin
    list_filter = ('start_date', 'end_date')  # Filters for the admin


@admin.register(First_step_SP_Ads_AMZ)
class First_step_SP_Ads_AMZAdmin(admin.ModelAdmin):
    list_display = (
        'date',
        'portfolio_name',
        'currency',
        'campaign_name',
        'ad_group_name',
        'targeting',
        'match_type',
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
        'day_14_conversion_rate'
    )

    search_fields = ('campaign_name', 'ad_group_name')
    list_filter = ('date', 'campaign_name')

@admin.register(First_step_SB_Ads_AMZ)
class First_step_SB_Ads_AMZ(admin.ModelAdmin):

    list_display = (
        'date',
        'portfolio_name',
        'currency',
        'campaign_name',
        'cost_type',
        'country',
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
        'long_term_roas'
    )

    search_fields = ('portfolio_name', 'campaign_name')
    list_filter = ('portfolio_name', 'campaign_name')


@admin.register(First_step_SD_Ads_AMZ)
class First_step_SD_Ads_AMZAdmin(admin.ModelAdmin):
    list_display = (
        'date',
        'portfolio_name',
        'currency',
        'campaign_name',
        'cost_type',
        'ad_group_name',
        'targeting',
        'bid_optimization',
        'impressions',
        'viewable_impressions',
        'clicks',
        'ctr',
        'day_14_detail_page_views',
        'spend',
        'cpc',
        'cost_per_1000_viewable_impressions',
        'total_advertising_cost_of_sales',
        'total_return_on_advertising_spend',
        'day_14_total_orders',
        'day_14_total_units',
        'day_14_total_sales',
        'day_14_new_to_brand_orders',
        'day_14_new_to_brand_sales',
        'day_14_new_to_brand_units',
        'total_advertising_cost_of_sales_clicks',
        'total_return_on_advertising_spend_click',
        'day_14_total_orders_click',
        'day_14_total_units_click',
        'day_14_total_sales_click',
        'day_14_new_to_brand_orders_click',
        'day_14_new_to_brand_sales_click',
        'day_14_new_to_brand_units_click'
    )

    search_fields = ('portfolio_name', 'campaign_name')
    list_filter = ('portfolio_name', 'campaign_name')

@admin.register(First_step_ReturnData_AMZ)
class First_step_ReturnData_AMZAdmin(admin.ModelAdmin):
    list_display = (
        'order_id',
        'order_date',
        'return_request_date',
        'return_request_status',
        'amazon_rma_id',
        'seller_rma_id',
        'label_type',
        'label_cost',
        'currency_code',
        'return_carrier',
        'tracking_id',
        'label_to_be_paid_by',
        'a_to_z_claim',
        'is_prime',
        'asin',
        'merchant_sku',
        'item_name',
        'return_quantity',
        'return_reason',
        'in_policy',
        'return_type',
        'resolution',
        'invoice_number',
        'return_delivery_date',
        'order_amount',
        'order_quantity',
        'safet_action_reason',
        'safet_claim_id',
        'safet_claim_status',
        'safet_claim_creation_time',
        'safet_claim_reimbursement_amount',
        'refund_amount',
        'category'
    )

    search_fields = ('order_id', 'order_date')
    list_filter = ('order_id', 'order_date')



"""Registering the models for Flipkart Platform"""

@admin.register(First_step_SalesData_FK)
class First_step_SalesData_FKAdmin(admin.ModelAdmin):
    list_display = (
        'seller_gstin',
        'order_id',
        'order_item_id',
        'product_title',
        'fsn',
        'sku',
        'hsn_code',
        'event_type',
        'event_sub_type',
        'order_type',
        'fulfilment_type',
        'order_date',
        'order_approval_date',
        'item_quantity',
        'order_shipped_from_state',
        'warehouse_id',
        'price_before_discount',
        'total_discount',
        'seller_share',
        'bank_offer_share',
        'price_after_discount',
        'shipping_charges',
        'final_invoice_amount',
        'type_of_tax',
        'taxable_value',
        'cst_rate',
        'cst_amount',
        'vat_rate',
        'vat_amount',
        'luxury_cess_rate',
        'luxury_cess_amount',
        'igst_rate',
        'igst_amount',
        'cgst_rate',
        'cgst_amount',
        'sgst_rate',
        'sgst_amount',
        'tcs_igst_rate',
        'tcs_igst_amount',
        'tcs_cgst_rate',
        'tcs_cgst_amount',
        'tcs_sgst_rate',
        'tcs_sgst_amount',
        'total_tcs_deducted',
        'buyer_invoice_id',
        'buyer_invoice_date',
        'buyer_invoive_amount',
        'customer_billing_pincode',
        'customer_billing_state',
        'customer_delivery_pincode',
        'customer_delivery_state',
        'usual_price',
        'is_shopsy_order',
        'tds_rate',
        'tds_amount'
    )
    search_fields = ('fsn', 'sku')
    list_filter = ('order_date', 'event_type')


@admin.register(First_step_cogs_vertical)
class First_step_cogs_verticalAdmin(admin.ModelAdmin):
    list_display = (
        'sku',
        'pid',
        'vertical',
        'mrp',
        'cogs'
    )
    search_fields = ('sku', 'vertical')
    list_filter = ('vertical', 'sku')


@admin.register(First_step_InvoiceData_FK)
class First_step_InvoiceData_FKAdmin(admin.ModelAdmin):
    list_display = (
        'service_type',
        'order_item_id',
        'recall_id',
        'warehouse_state_code',
        'fee_name',
        'total_fee_amount',
        'fee_amount',
        'fee_waiver_amount',
        'cgst_rate',
        'sgst_rate',
        'igst_rate',
        'cgst_amount',
        'sgst_amount',
        'igst_amount',
        'total_tax_amount',
        'date'
    )

    search_fields = ('fee_name', 'order_item_id')
    list_filter = ('fee_name', 'order_item_id')


@admin.register(First_step_AdsData_FK)
class First_step_AdsData_FKAdmin(admin.ModelAdmin):
    list_display = (
        'campaign_id',
        'campaign_name',
        'ad_group_id',
        'ad_group_name',
        'date',
        'views',
        'clicks',
        'ctr',
        'cvr',
        'ad_spend',
        'units_sold_direct',
        'units_sold_indirect',
        'direct_revenue',
        'indirect_revenue',
        'roi_direct',
        'roi_indirect'
    )

    search_fields = ('campaign_name', 'campaign_id')
    list_filter = ('campaign_name', 'ad_group_id')

@admin.register(First_step_Master_SKU)
class First_step_Master_SKUAdmin(admin.ModelAdmin):
    list_display = (
        'sku',
        'product_title',
        'ean',
        'length',
        'breadth',
        'height',
        'weight',
        'fk_platform_sku',
        'fk_fsn',
        'amazon_platform_sku',
        'amazon_asin',
        'first_cry_platform_sku',
        'first_cry_product_id',
        'myntra_platformsku',
        'myntra_product_id',
        'jiomart_platform_sku',
        'jiomart_product_id',
        'meesho_platform_sku',
        'meesho_product_id',
        'pharmeasy_platform_sku',
        'pharmeasy_product_id',
        'rk_world_platform_sku',
        'rk_world_product_id',
        'mrp',
        'gst',
        'hsn',
        'cogs',
        'product_vertical'
    )

    search_fields = ('sku', 'product_title')
    list_filter = ('product_title', 'product_vertical')


@admin.register(First_step_FK_Return_data)
class First_step_FK_Return_data_Admin(admin.ModelAdmin):
    list_display = (
        'return_id',
        'order_item_id',
        'fulfilment_type',
        # 'return_requested_date',
        # 'return_approval_date',
        'return_status',
        'return_reason',
        'return_sub_reason',
        'return_type',
        'return_result',
        'return_expectation',
        'reverse_logistics_tracking_id',
        'sku',
        'fsn',
        'product_title',
        'quantity',
        'return_completion_type',
        'primary_pv_output',
        'detailed_pv_output',
        'final_condition_of_returned_product',
        'tech_visit_sla',
        # 'tech_visit_by_date',
        # 'tech_visit_completion_datetime',
        'tech_visit_completion_breach',
        'return_completion_sla',
        # 'return_complete_by_date',
        # 'return_completion_date',
        'return_completion_breach',
        # 'return_cancellation_date',
        'return_cancellation_reason'
    )

    search_fields = ('order_item_id', 'sku')
    list_filter = ('order_item_id', 'return_status')



@admin.register(Jr_Sr_SalesData_FK)
class Jr_Sr_SalesData_FK_Admin(admin.ModelAdmin):
    list_display = (
        'seller_gstin',
        'order_id',
        'order_item_id',
        'product_title',
        'fsn',
        'sku',
        'hsn_code',
        'event_type',
        'event_sub_type',
        'order_type',
        'fulfilment_type',
        'order_date',
        'order_approval_date',
        'item_quantity',
        'order_shipped_from_state',
        'warehouse_id',
        'price_before_discount',
        'total_discount',
        'seller_share',
        'bank_offer_share',
        'price_after_discount',
        'shipping_charges',
        'final_invoice_amount',
        'type_of_tax',
        'taxable_value',
        'cst_rate',
        'cst_amount',
        'vat_rate',
        'vat_amount',
        'luxury_cess_rate',
        'luxury_cess_amount',
        'igst_rate',
        'igst_amount',
        'cgst_rate',
        'cgst_amount',
        'sgst_rate',
        'sgst_amount',
        'tcs_igst_rate',
        'tcs_igst_amount',
        'tcs_cgst_rate',
        'tcs_cgst_amount',
        'tcs_sgst_rate',
        'tcs_sgst_amount',
        'total_tcs_deducted',
        'buyer_invoice_id',
        'buyer_invoice_date',
        'buyer_invoive_amount',
        'customer_billing_pincode',
        'customer_billing_state',
        'customer_delivery_pincode',
        'customer_delivery_state',
        'usual_price',
        'is_shopsy_order',
        'tds_rate',
        'tds_amount'
    )
    search_fields = ('fsn', 'sku')
    list_filter = ('order_date', 'event_type')


@admin.register(Jr_Sr_AdsData_FK_MP)
class Jr_Sr_AdsData_FK_MP_Admin(admin.ModelAdmin):

    list_display = (
        'campaign_id',
        'campaign_name',
        'date',
        'ad_spend',
        'views',
        'clicks',
        'total_converted_units',
        'total_revenue'
    )

    search_fields = ('campaign_name', 'campaign_id')
    list_filter = ('campaign_name', 'campaign_id')


@admin.register(Jr_Sr_InvoiceData_FK)
class Jr_Sr_InvoiceData_FK_Admin(admin.ModelAdmin):
    list_display = (
        'service_type',
        'order_item_id',
        'recall_id',
        'warehouse_state_code',
        'fee_name',
        'total_fee_amount',
        'fee_amount',
        'fee_waiver_amount',
        'cgst_rate',
        'sgst_rate',
        'igst_rate',
        'cgst_amount',
        'sgst_amount',
        'igst_amount',
        'total_tax_amount',
        'date'
    )

    search_fields = ('fee_name', 'order_item_id')
    list_filter = ('fee_name', 'order_item_id')


@admin.register(Jr_Sr_cogs_master_sku)
class Jr_Sr_cogs_master_sku_Admin(admin.ModelAdmin):
    list_display = (
        'product_vertical',
        'size',
        'pack_size',
        'check_name',
        'product_title',
        'sku',
        'fsn',
        'lid',
        'mrp',
        'settlement_per_unit',
        'cogs'
    )

    search_fields = ('product_vertical', 'sku')
    list_filter = ('product_vertical', 'sku')

@admin.register(Jr_Sr_cogs)
class Jr_Sr_cogs_Admin(admin.ModelAdmin):
    
    list_display = (
        'product_title',
        'sku',
        'mrp',
        'settlement_per_unit',
        'cogs'
    )

    search_fields = ('sku', 'product_title')
    list_filter = ('sku', 'product_title')


@admin.register(Jr_Sr_FK_Return_data)
class Jr_Sr_FK_Return_data_Admin(admin.ModelAdmin):
    list_display = (
        'return_id',
        'order_item_id',
        'fulfilment_type',
        # 'return_requested_date',
        # 'return_approval_date',
        'return_status',
        'return_reason',
        'return_sub_reason',
        'return_type',
        'return_result',
        'return_expectation',
        'reverse_logistics_tracking_id',
        'sku',
        'fsn',
        'product_title',
        'quantity',
        'return_completion_type',
        'primary_pv_output',
        'detailed_pv_output',
        'final_condition_of_returned_product',
        'tech_visit_sla',
        # 'tech_visit_by_date',
        # 'tech_visit_completion_datetime',
        'tech_visit_completion_breach',
        'return_completion_sla',
        # 'return_complete_by_date',
        # 'return_completion_date',
        'return_completion_breach',
        # 'return_cancellation_date',
        'return_cancellation_reason'
    )

    search_fields = ('order_item_id', 'sku')
    list_filter = ('order_item_id', 'return_status')



"""NexTen Brands Database"""

@admin.register(NexTen_SalesData_FK)
class NexTen_SalesData_FK_Admin(admin.ModelAdmin):
    
    list_display = (
        'seller_gstin',
        'order_id',
        'order_item_id',
        'product_title',
        'fsn',
        'sku',
        'hsn_code',
        'event_type',
        'event_sub_type',
        'order_type',
        'fulfilment_type',
        'order_date',
        'order_approval_date',
        'item_quantity',
        'order_shipped_from_state',
        'warehouse_id',
        'price_before_discount',
        'total_discount',
        'seller_share',
        'bank_offer_share',
        'price_after_discount',
        'shipping_charges',
        'final_invoice_amount',
        'type_of_tax',
        'taxable_value',
        'cst_rate',
        'cst_amount',
        'vat_rate',
        'vat_amount',
        'luxury_cess_rate',
        'luxury_cess_amount',
        'igst_rate',
        'igst_amount',
        'cgst_rate',
        'cgst_amount',
        'sgst_rate',
        'sgst_amount',
        'tcs_igst_rate',
        'tcs_igst_amount',
        'tcs_cgst_rate',
        'tcs_cgst_amount',
        'tcs_sgst_rate',
        'tcs_sgst_amount',
        'total_tcs_deducted',
        'buyer_invoice_id',
        'buyer_invoice_date',
        'buyer_invoive_amount',
        'customer_billing_pincode',
        'customer_billing_state',
        'customer_delivery_pincode',
        'customer_delivery_state',
        'usual_price',
        'is_shopsy_order',
        'tds_rate',
        'tds_amount'
    )

    search_fields = ('fsn', 'sku')
    list_filter = ('order_date', 'event_type')

@admin.register(NexTen_AdsData_FK_MP)
class NexTen_AdsData_FK_MP_Admin(admin.ModelAdmin):
    
    list_display = (
        'campaign_id',
        'campaign_name',
        'date',
        'ad_spend',
        'views',
        'clicks',
        'total_converted_units',
        'total_revenue'
    )

    search_fields = ('campaign_name', 'campaign_id')
    list_filter = ('campaign_name', 'campaign_id')


@admin.register(NexTen_InvoiceData_FK)
class NexTen_InvoiceData_FK_Admin(admin.ModelAdmin):
    
    list_display = (
        'service_type',
        'order_item_id',
        'recall_id',
        'warehouse_state_code',
        'fee_name',
        'total_fee_amount',
        'fee_amount',
        'fee_waiver_amount',
        'cgst_rate',
        'sgst_rate',
        'igst_rate',
        'cgst_amount',
        'sgst_amount',
        'igst_amount',
        'total_tax_amount',
        'date'
    )

    search_fields = ('fee_name', 'order_item_id')
    list_filter = ('fee_name', 'order_item_id')

@admin.register(NexTen_COGS_Master_SKU)
class NexTen_COGS_Master_SKU_Admin(admin.ModelAdmin):
    list_display = (
        'product_title',
        'sku',
        'product_vertical',
        'fsn',
        'cogs',
        'brand',
        'seller'
    )

    search_fields = ('product_title', 'product_vertical')
    list_filter = ('product_title', 'product_vertical')

@admin.register(NexTen_Return_data)
class NexTen_Return_data_Admin(admin.ModelAdmin):
    list_display = (
        'return_id',
        'order_item_id',
        'fulfilment_type',
        # 'return_requested_date',
        # 'return_approval_date',
        'return_status',
        'return_reason',
        'return_sub_reason',
        'return_type',
        'return_result',
        'return_expectation',
        'reverse_logistics_tracking_id',
        'sku',
        'fsn',
        'product_title',
        'quantity',
        'return_completion_type',
        'primary_pv_output',
        'detailed_pv_output',
        'final_condition_of_returned_product',
        'tech_visit_sla',
        # 'tech_visit_by_date',
        # 'tech_visit_completion_datetime',
        'tech_visit_completion_breach',
        'return_completion_sla',
        # 'return_complete_by_date',
        # 'return_completion_date',
        'return_completion_breach',
        # 'return_cancellation_date',
        'return_cancellation_reason'
    )

    search_fields = ('order_item_id', 'sku')
    list_filter = ('order_item_id', 'return_status')


# Uploaded file tracker
@admin.register(UploadedFileTracker)
class UploadedFileTracker_Admin(admin.ModelAdmin):
    list_display = (
        'file_name',
        'uploaded_at'
    )

    search_fields = ('file_name', 'uploaded_at')
    list_filter = ('file_name', 'uploaded_at')