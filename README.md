# HTTP2SQL
A middleware to interface with storage drivers when you don't have any other solution. 
Or when you're lazy to use a database driver.
Or both.  
Works with regular HTTP(s) using GET/POST/PUT/DELETE requests

## Prerequisites
- Python 3.9 (using a venv is not required but recommended)
- ``pip install --upgrade pxyTools flask mysql.connector psycopg2-binary`` (last 2 are mandatory even if you don't use these drivers)

## Deploy
1. Install uWSGI: `pip install uwsgi`
2. Use the provided uWSGI sample config
3. Serve with ``uwsgi /path/to/uwsgi.ini``  
NOTA: If you plan to serve with flask's internal webserver to serve h2s, please set both uwsgi options in the config to false.

## uWSGI config
````ini
[uwsgi]
socket = 127.0.0.1:5050

; Note: A master process must be enabled for post-fork to work properly.
processes = 4
threads = 2
master = true

chdir = /path/to/your/app
venv = /path/to/your/app/venv/if/any
wsgi-file = app.py
callable = app

; Set to true for true multiprocessing. Please set use_uwsgi_forking to false in the config.json if using multiprocessing.
lazy-apps = false
````

## App config
````json
{
  "root_token": "root",
  "app_port": 5050,
  "app_fake_ssl": false,
  "use_uwsgi": true,
  "use_uwsgi_forking": true
}
````
``root_token``: Application token to reload profiles  
``app_port``: Webserver port  
``app_fake_ssl``: Whether to run the app in "adhoc" SSL (with no certificates). This makes the app available only using HTTPS. Not recommended for "production".  
``use_uwsgi``: *Whether to broadcast a profile reload signal to all uWSGI forks (WIP: currently not implemented.)*  
``use_uwsgi_forking``: Whether to load profiles using the `@postfork` decorator (if using pure uWSGI multiprocessing, this isn't required)

## Sample profile file explained
````json
{
  "friendly_name": "Default Driver",
  "driver": "file",
  "driver_config": {
    "relative_path": "data/default.data"
  },
  "tokens": {
    "sample_admin": ["@"],
    "sample_user": ["*"],
    "sample_restricted_user": ["table_name"]
  }
}
````
``friendly_name``: Driver Name  
``driver``: Driver file to load from /drivers  
``driver_config``: Config kwargs passed to the driver  
``tokens``: JSON array with the token as a key and a list of authorized tables.  
            @ means this user is a profile admin, * means the user can edit all tables. (@ > * > table_name > none)

To get other options for ``driver_config``, please go to the respective driver's code. JSON keys are passed as kwargs to the Driver class.  
Here's a sample code (from the postgres driver)
````python
class Driver:
    def __init__(self, host, user, password, database, port=5432)
````
JSON for this driver would be:
````json
"host": "sample_host"
"user": "sample_user"
"password": "sample_password"
"database": "sample_database"
"port": 5432  # Omittable
````

## Reload profiles
Endpoint: ``/reload``  
Method: ``GET``  
Headers: ``APIKey <rootkey>``  
Reload profiles in the /profiles directory.

## Create table for specified profile
Endpoint: ``/<profile>/<table>``  
Method: ``POST``  
Headers: ``APIKey <apikey>``  
Create a new table with the associated profile

## Remove table for specified profile
Endpoint: ``/<profile>/<table>``  
Method: ``DELETE``  
Headers: ``APIKey <apikey>``  
Remove a table from the associated profile (deleting all pool data with it)

## Store a key
Endpoint: ``/<profile>/<table>/<key>``  
Method: ``PUT``  
Headers: ``APIKey <apikey>``  
Optional headers: ``Pool <pool_name>``  
Body: ``<key_value>``  
Store a key in the database

## Get a key
Endpoint: ``/<profile>/<table>/<key>``  
Method: ``GET``  
Headers: ``APIKey <apikey>``  
Optional headers: ``Pool <pool_name>``  
Retrieve a key from the database

## Delete a key
Endpoint: ``/<profile>/<table>/<key>``  
Method: ``DELETE``  
Headers: ``APIKey <apikey>``  
Optional headers: ``Pool <pool_name>``  
Removes a key from the database

## Multi
Endpoint: ``/<profile>/_multi``  
Method: ``POST``  
Headers: ``APIKey <apikey>``  
Body: JSON  
Allows multiple GET, PUT and DELETE operations in a single request  
The format for this call must follow this JSON pattern:
````json
{
    "get": {
        "table_name": {
            "pool_name": ["key_name"],
            "default": ["default_is_the_default_pool"]
        }
    },
    "put": {
        "another_table": {
            "some_pool": {"key1": "modifiedValue1"},
            "another_pool": {"key2": "modifiedValue2"}
        }
    },
    "delete": {
        "employees": {
          "first_name": ["john.doe"],
          "last_name": ["john.doe"]
        }
  }
}
````
Response will be 204 if no content gets fetched, otherwise it will look like this:
````json
{
    "table_name": {
        "pool_name": {"key_name": "value"},
        "default": {"default_is_the_default_pool": "that's true"}
    }
}
````

## The "Pool" concept
Here's a sample diagram that speaks for itself
````
root (http2sql application)
??????  website (profile)
???   ?????? data (table)
???     ?????? default (pool)
???     ???  ?????? someKey: someValue (key-value pair) /website/data/someKey
???     ???  ?????? someKey2: someValue2 (key-value pair)
???     ?????? dev (pool)
???        ?????? someKey: someOtherValue (key-value pair) /website/data/someKey (Pool: dev)
???        ?????? someKey2: someOtherValue2 (key-value pair)
??????  discordbot (profile)
    ?????? server_preferences (table)
    ??? ?????? serverid_123456789 (pool)
    ??? ???  ?????? greetings: true (key-value pair): /discordbot/server_preferences/greetings (Pool: serverid_123456789)
    ??? ???  ?????? automod: false (key-value pair)
    ??? ?????? serverid_987654321 (pool)
    ???    ?????? greetings: false (key-value pair) /discordbot/server_preferences/greetings (Pool: serverid_987654321)
    ???    ?????? automod: true (key-value pair)
    ?????? server_notifications (table)
      ?????? serverid_123456789 (pool)
      ???  ?????? admin_infos: false (key-value pair) /discordbot/server_notifications/admin_infos (Pool: serverid_123456789)
      ???  ?????? useful_infos: false (key-value pair)
      ?????? serverid_987654321 (pool)
         ?????? admin_infos: true (key-value pair) /discordbot/server_notifications/admin_infos (Pool: serverid_987654321)
         ?????? useful_infos: true (key-value pair)
````
