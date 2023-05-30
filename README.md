# panda

## Running the App

### Running Using Docker (preferred method)
- This is the preferred method as it eliminates the risk of polluting any existing software
- Commands to run in **bold**
- Download and install if you don't have it: [Docker](https://www.docker.com/get-started)
- Open a terminal and change directory to the root of this project
- Build the container, make sure you get the dot at the end: 
- **docker build --tag panda-stevet-docker .**
- The build will probably take a few minutes
- Once that's finished you should be able to run the container with:
- **docker run -i -t -p 8090:8090 --name panda panda-stevet-docker**
- To change the port on your local machine change the first value of **-p *8090*:8090**
- You can stop the container with ctrl-c
- To run again (after the first time) you just need:
- **docker run -i -t -p 8090:8090 panda-stevet-docker**

### Running With Local Python
- Commands to run in **bold**
- This App was developed using python 3.10, so I recommend that as a minimum
- Installation of python will be different depending upon your operating system
- Python installs can be found here: https://www.python.org/downloads/release/python-3100/
- Once python is installed, create a python virtual environment:
- **python -m venv /path/to/panda/venv**
- Install the required python libraries with this command:
- **/path/to/panda/venv/bin/python3 -m pip install -r /path/to/panda/requirements.txt**
- CD to /path/to/panda
- Type **cwd**, you should see: /path/to/panda
- Run the server with this command:
- **/path/to/panda/venv/bin/python3 -m main**
- The default port is 8090, if you need to change it just add it to the command line:
- **/path/to/panda/venv/bin/python3 -m main *8091***
- If successful, you should see some logging, followed by this in the console:
```
 * Serving Flask app 'main'
 * Debug mode: off
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:8090
 * Running on http://192.168.0.41:8090
Press CTRL+C to quit
```
---
## Evaluating the App
- An auto-generated UI for evaluating and testing the app is available at:
- http://localhost:8090/panda-api/ui/
- The first time the app starts it checks to see if the database is empty and, if this is the case, populates it with sample data
- A test utility endpoint for generating NHS numbers is available at:
- http://localhost:8090/panda-api/ui/#/test%20tool/dev_tools.generate_test_nhs_num
- To try a HTTP method it is necessary to click on the button on the right-hand side with the label "Try it out"
- Most fields are populated with example data
- App accepts dates formatted like so: 2023-01-01

### Example Manual Test
- Generate a new NHS Number using http://localhost:8090/panda-api/ui/#/test%20tool/dev_tools.generate_test_nhs_num
- Copy the generated number which appears in the response body
- Use it to create a new patient 

## Front End Clients
- The API is defined according to the OpenAPI 3 specification and can be found in YAML file: apidef/patient-app.yml
- One of the benefits of this is that client libraries for most programming languages can be auto-generated.
- Details of how to do this can be found here: https://swagger.io/tools/swagger-codegen/
- The auto-generated test UI also contains details of the json responses from the server

## Database Configuration
- The app uses ORM library SQLAlchemy
- This allows the app to support databases from multiple vendors without the need for source code changes (with the exception of the DB URL constant)
- The default database is sqlite as this is included with the python distribution
- The database used can changed by modifying constant `DB_URL` in main.py

## Application Details
- The API specification is located in YAML file: apidef/patient-app.yml
- In addition to method parameters and return types it also contains mappings to python handler functions
- The majority of these functions are located in operations.py
- The functions in operations.py perform parameter validation
- The same functions also handle application exceptions and handle the return of appropriate messages to the user
- The business logic is contained in `class PatientAppointmentsApp` in file application.py
- There is a single instance of this class
- The functions in operations.py call into this class
- PatientAppointmentsApp in turn handles queries and, updates by making calls to the Data Store
- The data store is completely abstracted from PatientAppointmentsApp by `class DataStore(Protocol):` in datastore.py 
- In addition to making unit testing free of the need for a live database, it also allows alternate storage implementations, NOSQL for example
- There is no internationalisation but all string returned to the user are defined as constants in messages.py to make this easier in the future
- All incoming datetimes are converted to UTC


## Development Notes

- I decided to concentrate on setting up a framework that is relatively quick and simple to modify by changing the business logic in class PatientAppointmentsApp (application.py).
- I chose to not create separate tables for clinicians and departments because in the example appointments they are not uniquely identifiable and tests showed that there weren't many in the sample data.  For that reason I've added them as enums in the API def for the time being, as it will make evaluation of the API a bit nicer in the auto-generated UI.   
- I assume that for audit reasons the customer does not want the facility to delete appointments to be provided.
- Haven't done anything special for appointments postcode, assuming FE gets that from elsewhere
- I've returned 400's in some cases where I probably wouldn't in production but I've done it to signal to the user that the result is probably not what was expected.
- I've not had time to add code to check for time wasted in unattended appointments but I've stored the appointment duration time as and integer representing minutes so that it should be relatively simple to add this functionality.

### TODO:

- Add date ranges to patient/clinician appointment queries
- Add links to responses where appropriate
- Store patient name parts separately 
- Exception fields and messages probably need tweaking to provide better info
- You can create duplicate appointments, stop this happening
- Check for appointment availability?
- Paging of results
- Sort out use of name "id" in Appointment (currently used for compatibility with sample data)
- At the moment it fails fast i.e. aborts when it detects the first invalid field, would be nicer if it reported all invalid fields at once
- App needs to check patient exists when creating an appointment
