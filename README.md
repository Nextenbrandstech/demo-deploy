
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



/* Center the table on the screen */
.mt-4 {
  max-height: 500px;
  overflow-y: auto;
  margin: 10px auto;
  width: 90%;
}

#consolidated-data-table th {
  background-color: #eeff00;
  font-weight: bold;
}

.header-title {
  margin-top: 15px;
  text-align: center;
}


/* Overall Container & Page Styles */
body {
  background: linear-gradient(to right, #fbbebe, #f99f9f);
  font-family: Arial, sans-serif;
  color: #000000;
}

.container {
  background: rgb(248, 253, 252);
  padding: 2rem;
  border-radius: 14px;
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
}

/* Header */
h1 {
  font-size: 2.5rem;
  font-weight: bold;
  color: #000000;
  background: -webkit-linear-gradient(45deg, #f50505, #e6d705);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  text-align: center;
  margin-bottom: 20px;
}

/* Date Range Selection Section */
.form-label {
  font-weight: bold;
  color: #1605ff;
}

.form-control {
  border: 2px solid #66b3ff;
  border-radius: 8px;
  transition: box-shadow 0.2s ease-in-out;
}

.form-control:focus {
  box-shadow: 0 0 8px rgba(102, 179, 255, 0.6);
}

#fetch-insights {
  background-color: #012549;
  color: rgb(255, 182, 182);
  font-weight: bold;
  border-radius: 8px;
  transition: background-color 0.3s;
}

#fetch-insights:hover {
  background-color: #aad1f9;
}

/* Insight Cards */
.card {
  background-color: #d7e8f9;
  border: 1px solid #dee2e6;
  border-radius: 10px;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100px;
  padding: 5px;
  text-align: center;
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
}

.card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.15);
  background-color: #82b9f4;
}

.card-title {
  font-size: 1.2rem;
  font-weight: bold;
  color: #0919f8;
}

.card-text {
  font-size: 1.5rem;
  color: #080808;
}


#current-date-range,
#previous-date-range {
  font-size: 12px;
  /* Smaller font size */
  padding: 4px;
  /* Reduced padding */
  height: auto;
  /* Adjust height to fit smaller size */
  width: 100%;
  /* Make it fit nicely in the column */
}

.hidden {
  display: none;
}

/* sticky header for product table */
#table-container {
  width: 100%;
  max-height: 600px; /* Maximum height for scrolling */
  overflow-y: auto; /* Enable vertical scrolling */
  border-radius: 12px; /* Rounded corners for container */
  border: 1px solid #ccc; /* Border for container */
  display: block;
}

#return-consolidated-data-table {
  width: 100%; /* Full width of the table */
  border-collapse: collapse; /* Ensure clean table layout */
}

#return-consolidated-data-table thead {
  position: sticky; /* Makes the header sticky */
  top: 0; /* Sticks the header at the top of the container */
  background-color: #fff706; /* Background color for the header */
  z-index: 1; /* Ensures the header stays on top of scrolling rows */
  box-shadow: 0px 2px 5px rgba(0, 0, 0, 0.1); /* Adds shadow for better visibility */
}

#return-consolidated-data-table th,
#return-consolidated-data-table td {
  padding: 10px; /* Padding for table cells */
  border: 1px solid #ddd; /* Border for cells */
  text-align: left; /* Align text to the left */
}

#return-consolidated-data-table th {
  font-weight: bold; /* Bold font for header cells */
  text-align: center; /* Center-align header text */
}

#return-consolidated-data-table tr:hover {
  background-color: #4ea6ed;
}

/* freeze the headers of the pnl */
#container {
  width: 100%;
  max-height: 500px; /* Maximum height for scrolling */
  overflow-y: auto; /* Enable vertical scrolling */
  overflow-x: auto; /* Enable vertical scrolling */
  border-radius: 10px; /* Rounded corners */
  border: 1px solid #ccc; /* Add a border for better visibility */
}

#insights-table {
  width: 100%; /* Ensure the table spans the container width */
  border-collapse: collapse; /* Make the table layout clean */
}

#insights-table thead {
  position: sticky; /* Makes the header sticky */
  top: 0; /* Sticks the header to the top of the container */
  left: 0; /* Sticks the header to the top of the container */
  background-color: #fff706; /* Background color for the header */
  z-index: 2; /* Ensures the header stays above table rows */
  box-shadow: 0px 2px 5px rgba(0, 0, 0, 0.1); /* Adds a shadow for better separation */
}

#insights-table th,
#insights-table td {
  padding: 10px; /* Padding inside cells */
  border: 1px solid #ddd; /* Border for cells */
  text-align: center; /* Center-align content */
}

#insights-table th {
  font-weight: bold; /* Bold font for header cells */
  text-align: center; /* Center-align header text */
}
#insights-table tr:hover {
  background-color: #4ea6ed;
}




