# RAG instagram 

Contents:
1. Project Overview
2. Methodology
3. Code, Notebook examples

## Project overview
RAG on your instagram profile. This requires the user to log into their personal instagram account.  

## Quick-start
In the root project folder:
1. Create a file called `credentials.yml` and set the `Username` and `Password` of the target instagram profile in the example below:
    - USERNAME: user_name
    - PASSWORD: password
2. Run `instagram_scraper.py`, which will scrape the instagram posts which may include text files, images, and videos. This process may take a while depending on the amount of posts and files associated with each post, due to the query limit even though you are logged into your account. 
These scraped files are saved in a folder named as the instagram username. Transfer this folder into the `data` folder. 



