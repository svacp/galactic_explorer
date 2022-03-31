# PREREQUISITES  
  
### 1 Packages installation  
  
* Packages installed into virtualenv  
  
  
		 pip install -r requirements.txt 

### 1 Packages installation  

* Migrate the DB


		 source venv/bin/activate
         python manage.py migrate
		 
# RUNNING   
  
### 1 Activate virtual enviroment

		$ source venv/bin/activate

### 2 Run the test server

		python manage.py runserver

After server starting, the application is available on http://127.0.0.1:8000
  
 # NOTES
 
- `sqlite3` is used for sake of simplicity. I would prefer using `postgresql` in production.
- I would recommend an admin interface for managing the collections.
- UI could be more pleasant with the use of gradients (`Saas`).
- Headers of data fields are now displayed as it comes from SWAPI. It would be better to show it in defined order.
 - Items in header (as well as items in statistics form) could be in more "human readable" form. E.g. "Hair color" instead of "hair_color".
- API responses are logged. Long messages might be shortened using `textwrap` module  
- Type hinting is used just on non-standard-django scripts. E.g. script for communicating with SWAPI.
- Some tests within test_views are redundant. It would be nice to use a base class with common tests.
- Loading data from API is nice example for using shared / asynchronous tasks.
- "Pagination" is really simple. Standard simple pagination should have at leas possibilities to move forward and backward and number of pages.
- Loading next page could be done without reloading of the page using `ajax` and `jQuery`, for example.
- Planets processing is nice example for using cache.