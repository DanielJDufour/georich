# NOTE: HIGHLY EXPERIMENTAL AND NOT READY FOR PRODUCTION USE

# georich
Enrich your Geospatial Data!

# installation
```
pip install georich
```

# usage
You can use georich by importing Python methods or hitting the API.

### Importing Enrich
```
from georich import enrich
from pandas import read_csv

df = read_csv("/tmp/survey_locations.csv")

# adds country_code column
enriched_df = enrich(df, country_code=True)
```

### Run API Server
```
from georich import run_server

run_server()
```
```
Performing system checks...

System check identified no issues (0 silenced).
April 17, 2018 - 03:59:10
Django version 2.0.4, using settings 'georich.core.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```

### Users
- [FirstDraftGIS](https://firstdraftgis.com)
- [TweetGeoLocator](https://tweetgeolocator.com)
