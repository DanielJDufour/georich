from distutils.core import setup

setup(
  name = 'georich',
  packages = ['georich'],
  package_dir = {'georich': 'georich'},
  package_data = {'georich': ['api/*', 'api/scripts/*', 'core/*']},
  version = '0.1.0',
  description = 'Enrich your Geospatial Data!',
  author = 'Daniel J. Dufour',
  author_email = 'daniel.j.dufour@gmail.com',
  url = 'https://github.com/DanielJDufour/georich',
  download_url = 'https://github.com/DanielJDufour/georich/tarball/download',
  keywords = ['location','geo','python','enrich', 'enrichment', 'csv', 'tsv', 'shapefile'],
  classifiers = [],
  install_requires=["Django", "django-extensions", "freq", "numpy", "pandas", "scipy"]
)
