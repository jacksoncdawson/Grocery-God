class ScraperError(Exception):
  """Exception raised for errors in the scraping process."""
  pass

class CleanerError(Exception):
  """Exception raised for errors in the data cleaning process."""
  pass

class DatabaseError(Exception):
  """Exception raised for errors in the database operations."""
  pass