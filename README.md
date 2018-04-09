# georich
Enrich your Geospatial Data!

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

### API Usage
coming soon!

### Users
[FirstDraftGIS](https://firstdraftgis.com)
[TweetGeoLocator](https://tweetgeolocator.com)
