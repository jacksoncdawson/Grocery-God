from scraper import write_safeway_scrape
from parser import run_clean_data

def main():
  
  write_safeway_scrape()
  
  run_clean_data()


if __name__ == "__main__":
  
  main()
