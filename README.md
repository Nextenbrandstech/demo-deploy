
----------------------------------------Backend Readme--------------------------------------------

This is the file structure we are following for the backend related tasks

backend/
├── migrations/
├── management/
│   └── commands/
│       ├── upload_files.py  # use to call the data loading logic that is in data_loader.py for 
│       └── run_analysis.py  # use to call the func that are present in data_analysis file
├── services/
│   ├── data_loader.py  # it has the data loading logic
│   ├── data_analysis.py  # it has data pre-processing logic
├── models.py  # Your models for the database
├── admin.py  # Admin interface configuration
└── apps.py
└── tests.py
└── views.py

In order to make the database and uplaod it into database, follow these steps
1. Make the class of the database that includes the data type of the fields and further conditions, in the models.py file.
2. In the service folder create a file that defines the logic to upload the data as well as handeling the bottle-neck cases.
3. In the management/commands folder make a file that will call the function defined in the file which is in service folder (that has the logic to upload the data).
4. Now register that model in the admin.py file of the backend.


----- Important commands -----

Whenever you make changes in the database architecture make sure to migrate those changes in this manner
1. python manage.py makemigrations
2. python manage.py migrate
3. python manage.py upload_files (upload_files is defined in the management/commands folder)

Similarly, when you run you analysis file to get the sales and maketing matrics use this command
1. python manage.py run_analysis (run_analysis file is defined in the management/commands folder) 


---------------------------------------Frontend Readme---------------------------------------------

This is the file structure we are following for the frontend related tasks

1. Backend Preparation:

Data Analysis Logic: Implement functions in data_analysis.py (or similar) to calculate the required insights.
Backend View:
Create a function in views.py that calls the analysis functions and returns the data as JSON using JsonResponse.

2. URL Configuration (Backend App):

Create a urls.py file in the backend app and include a path for the view that returns the insights as JSON.
Ensure the main project's urls.py includes this backend app's URL patterns.

3. Frontend App Setup:

Template Creation:
Create an HTML file (e.g., fk_page.html) in frontend/templates/frontend/.
Static Files (Optional for custom styling):
Set up CSS and JavaScript files in frontend/static/frontend/.

4. Frontend View:

Create a view function (fk_insights_page) in frontend/views.py to render the fk_page.html template.

5. URL Configuration (Frontend App):

Create or update frontend/urls.py to map a URL path (e.g., fk_insights/) to insights_page.
Include the frontend app's URLs in the main project’s urls.py.

6. AJAX/JavaScript Integration:

Write JavaScript code in fk_pages.html or a linked script to fetch data from the backend API endpoint (/backend/api/fk_insights/).
Use JavaScript to display this data dynamically on the page, formatting it into cards or other desired layouts.

7. Run and Test:

Start the Django server and navigate to /fk_insights/ to ensure the page loads and displays data as expected.
