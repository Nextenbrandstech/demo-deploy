'''
The "command" folder is for calling the required functions(that are logic based) 
which are present in the "service" folder 

This file simply calls the function which are defined in the data_loader.py file.
So that means you have to run this file "python manage.py upload_files.py"
'''


from django.core.management.base import BaseCommand
from backend.services.data_loader import (load_sales_Amazon, load_CODBfees_data_AMZ, load_SP_Ads_AMZ, load_SB_Ads_AMZ, load_SD_Ads_AMZ, load_Return_AMZ, load_sales_FK, 
                                        load_First_step_cogs_vertical, load_Invoice_FK, load_Ads_FK, load_First_step_Master_SKU, load_Jr_Sr_cogs_Master_SKU, 
                                          load_Ads_FK_MP, load_Jr_Sr_cogs, load_NexTen_COGS_Master_SKU, load_Return_FK)

from backend.models import (UploadedFileTracker, First_step_SalesData_AMZ, First_step_CODBFeesData_AMZ, First_step_SP_Ads_AMZ, First_step_SB_Ads_AMZ, 
                            First_step_SD_Ads_AMZ, First_step_ReturnData_AMZ, First_step_AdsData_FK, First_step_InvoiceData_FK, First_step_SalesData_FK, First_step_cogs_vertical, First_step_Master_SKU,
                            First_step_FK_Return_data, 
                            Jr_Sr_AdsData_FK_MP, Jr_Sr_InvoiceData_FK, Jr_Sr_SalesData_FK, Jr_Sr_cogs_master_sku, Jr_Sr_cogs, Jr_Sr_FK_Return_data,
                            NexTen_AdsData_FK_MP, NexTen_COGS_Master_SKU, NexTen_InvoiceData_FK, NexTen_SalesData_FK, NexTen_Return_data)

import os
from django.db import models

def upload_files_to_database(folder_path, tracking_database, process_function, data_model):
    
    # Iterate through all files in the folder
    for file_name in os.listdir(folder_path):
        
        # Create the full file path
        file_path = os.path.join(folder_path, file_name)

        # Check if the file is an Excel file
        if file_name.endswith('.xlsx') or file_name.endswith('.xls'):
            # Check if the file is already uploaded
            if not tracking_database.objects.filter(file_name=file_name).exists():
                try:
                    # Process and upload the file
                    process_function(file_path, data_model)

                    # Log the file as uploaded
                    tracking_database.objects.create(file_name=file_name)

                    print(f"{file_name} uploaded successfully!")
                except Exception as e:
                    print(f"Failed to upload {file_name}: {str(e)}")
            else:
                print(f"{file_name} already uploaded, skipping.")



class Command(BaseCommand):
    help = 'Upload the data from Excel file inro SQLite'

    def handle(self, *args, **kwargs):

        """For First Step"""

        # # specifying the path to the excel file
        
        # file_path_cogs_vertical_1st_step = r"C:\Users\Satyam\Documents\Excel files\1st step\COGS TRI.xlsx"
        # file_path_1st_step_master_sku = r"C:\Users\Satyam\Documents\Excel files\1st step\First_step_master_sku.xlsx"


        # # load the cogs file in the database of First Step
        # load_First_step_cogs_vertical(file_path_cogs_vertical_1st_step, First_step_cogs_vertical)
        # self.stdout.write(self.style.SUCCESS('COGS data of 1st Step is uploaded successfully!'))
        
        # # load the master sku file of First step in the database
        # load_First_step_Master_SKU(file_path_1st_step_master_sku, First_step_Master_SKU)
        # self.stdout.write(self.style.SUCCESS('Master SKU of 1st Step is uploaded successfully!'))
        
        # # uploading the Sales data to the Sales database of First Step FK
        # First_Step_sales_folder_path = r"C:\Users\Satyam\Documents\Excel files\1st step\sales"
        # upload_files_to_database(First_Step_sales_folder_path, UploadedFileTracker, load_sales_FK, First_step_SalesData_FK)
        
        # # uploading the Ads data to the Ads database of First Step FK
        # First_Step_ads_folder_path = r"C:\Users\Satyam\Documents\Excel files\1st step\ads"
        # upload_files_to_database(First_Step_ads_folder_path, UploadedFileTracker, load_Ads_FK, First_step_AdsData_FK)

        # # uploading the Invoice data into Invoice database of First Step FK
        # First_Step_invoice_folder_path = r"C:\Users\Satyam\Documents\Excel files\1st step\invoice"
        # upload_files_to_database(First_Step_invoice_folder_path, UploadedFileTracker, load_Invoice_FK, First_step_InvoiceData_FK)
        
        # # uploading the Return data into Return database of First Step FK
        # First_Step_return_folder_path = r"C:\Users\Satyam\Documents\Excel files\1st step\return"
        # upload_files_to_database(First_Step_return_folder_path, UploadedFileTracker, load_Return_FK, First_step_FK_Return_data)

        # For Deleting the entire database

        # First_step_AdsData_FK.objects.all().delete()
        # First_step_InvoiceData_FK.objects.all().delete()
        # First_step_SalesData_FK.objects.all().delete()
        # First_step_FK_Return_data.objects.all().delete()

        # # For Amazon's Platform
        # First_step_sales_AMZ_folder_path = r"C:\Users\Satyam\Documents\Excel files\1st step\amazon\sales"
        # upload_files_to_database(First_step_sales_AMZ_folder_path, UploadedFileTracker, load_sales_Amazon, First_step_SalesData_AMZ)

        # First_step_codb_AMZ_folder_path = r"C:\Users\Satyam\Documents\Excel files\1st step\amazon\codb"
        # upload_files_to_database(First_step_codb_AMZ_folder_path, UploadedFileTracker, load_CODBfees_data_AMZ, First_step_CODBFeesData_AMZ)

        # First_step_SP_Ads_AMZ_folder_path = r"C:\Users\Satyam\Documents\Excel files\1st step\amazon\ads\SP"
        # upload_files_to_database(First_step_SP_Ads_AMZ_folder_path, UploadedFileTracker, load_SP_Ads_AMZ, First_step_SP_Ads_AMZ)

        # First_step_SB_Ads_AMZ_folder_path = r"C:\Users\Satyam\Documents\Excel files\1st step\amazon\ads\SB"
        # upload_files_to_database(First_step_SB_Ads_AMZ_folder_path, UploadedFileTracker, load_SB_Ads_AMZ, First_step_SB_Ads_AMZ)

        # First_step_SD_Ads_AMZ_folder_path = r"C:\Users\Satyam\Documents\Excel files\1st step\amazon\ads\SD"
        # upload_files_to_database(First_step_SD_Ads_AMZ_folder_path, UploadedFileTracker, load_SD_Ads_AMZ, First_step_SD_Ads_AMZ)

        # First_step_Return_AMZ_folder_path = r"C:\Users\Satyam\Documents\Excel files\1st step\amazon\return"
        # upload_files_to_database(First_step_Return_AMZ_folder_path, UploadedFileTracker, load_Return_AMZ, First_step_ReturnData_AMZ)


        # For Deleting the entire database

        # First_step_SalesData_AMZ.objects.all().delete()
        # First_step_CODBFeesData_AMZ.objects.all().delete()
        # First_step_SP_Ads_AMZ.objects.all().delete()
        # First_step_SB_Ads_AMZ.objects.all().delete()
        # First_step_SD_Ads_AMZ.objects.all().delete()
        # First_step_ReturnData_AMZ.objects.all().delete()



        """For Jr Sr"""

        # # uploading the Master SKU files of Jr Sr in the database
        file_path_cogs_master_sku_jr_sr = r"C:\Users\Satyam\Documents\Excel files\Jr Sr\master sku jrsr.xlsx"
        # load_Jr_Sr_cogs_Master_SKU(file_path_cogs_master_sku_jr_sr, Jr_Sr_cogs_master_sku)
        # self.stdout.write(self.style.SUCCESS('Jr Sr Master SKU file is uploaded successfully!'))

        # # uploading the COGS file of Jr Sr in the database
        file_path_cogs_jr_sr = r"C:\Users\Satyam\Documents\Excel files\Jr Sr\cogs jrsr.xlsx"
        # load_Jr_Sr_cogs(file_path_cogs_jr_sr, Jr_Sr_cogs)
        # self.stdout.write(self.style.SUCCESS('Jr Sr COGS file is uploaded successfully!'))


        # # uploading the Sales data into Jr Sr database FK
        # Jr_Sr_sales_folder_path = r"C:\Users\Satyam\Documents\Excel files\Jr Sr\Sales"
        # upload_files_to_database(Jr_Sr_sales_folder_path, UploadedFileTracker, load_sales_FK, Jr_Sr_SalesData_FK)

        # # uploading the Ads data into Ads database of Jr Sr FK MP
        # Jr_Sr_Ads_folder_path = r"C:\Users\Satyam\Documents\Excel files\Jr Sr\Ads"
        # upload_files_to_database(Jr_Sr_Ads_folder_path, UploadedFileTracker, load_Ads_FK_MP, Jr_Sr_AdsData_FK_MP)

        # # uploading the Invoice data into the Invoice database of Jr Sr FK
        # Jr_Sr_Invoice_folder_path = r"C:\Users\Satyam\Documents\Excel files\Jr Sr\Invoice"
        # upload_files_to_database(Jr_Sr_Invoice_folder_path, UploadedFileTracker, load_Invoice_FK, Jr_Sr_InvoiceData_FK)
       
        # # uploading the Return data into the Return database of Jr Sr FK
        # Jr_Sr_Return_folder_path = r"C:\Users\Satyam\Documents\Excel files\Jr Sr\return"
        # upload_files_to_database(Jr_Sr_Return_folder_path, UploadedFileTracker, load_Return_FK, Jr_Sr_FK_Return_data)

        # Jr_Sr_SalesData_FK.objects.all().delete()
        # Jr_Sr_AdsData_FK_MP.objects.all().delete()
        # Jr_Sr_InvoiceData_FK.objects.all().delete()
        # Jr_Sr_FK_Return_data.objects.all().delete()

        """Nexten Brands file uploads"""

        # # uploading the COGS and Master SKU file of NexTen Brands in the database
        # file_path_cogs_master_sku_NexTen = r"C:\Users\Satyam\Documents\Excel files\NexTen\Nexten cogs and master sheet.xlsx"
        # load_NexTen_COGS_Master_SKU(file_path_cogs_master_sku_NexTen, NexTen_COGS_Master_SKU)
        # self.stdout.write(self.style.SUCCESS('NexTen COGS and Master file is uploaded successfully!'))


        # # uploading the Sales data into NexTen Brands database FK
        # NexTen_sales_folder_path = r"C:\Users\Satyam\Documents\Excel files\NexTen\sales"
        # upload_files_to_database(NexTen_sales_folder_path, UploadedFileTracker, load_sales_FK, NexTen_SalesData_FK)

        # # uploading the Ads data into Ads database of NexTen Brands FK MP
        # NexTen_Ads_folder_path = r"C:\Users\Satyam\Documents\Excel files\NexTen\ads"
        # upload_files_to_database(NexTen_Ads_folder_path, UploadedFileTracker, load_Ads_FK_MP, NexTen_AdsData_FK_MP)
        
        # # uploading the Invoice data into the Invoice database of Nexten Brands FK
        # NexTen_Invoice_folder_path = r"C:\Users\Satyam\Documents\Excel files\NexTen\invoice"
        # upload_files_to_database(NexTen_Invoice_folder_path, UploadedFileTracker, load_Invoice_FK, NexTen_InvoiceData_FK)

        # # uploading the Return data into the Return database of Nexten Brands FK
        # NexTen_Return_folder_path = r"C:\Users\Satyam\Documents\Excel files\NexTen\return"
        # upload_files_to_database(NexTen_Return_folder_path, UploadedFileTracker, load_Return_FK, NexTen_Return_data)

        # NexTen_SalesData_FK.objects.all().delete()
        # NexTen_AdsData_FK_MP.objects.all().delete()
        # NexTen_InvoiceData_FK.objects.all().delete()
        # NexTen_Return_data.objects.all().delete()