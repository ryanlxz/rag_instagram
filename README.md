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
2. Make setup script executable by running `chmod +x scripts/setup.sh`
3. Run bash script with `bash scripts/run.sh` which
- Creates a new conda venv and installs the required packages
4. Install Ollama for running LLM models
- Go to https://ollama.com/download and follow the instructions.
4. Run `instagram_scraper.py`, which will scrape the instagram posts which may include text files, images, and videos. This process may take a while depending on the amount of posts and files associated with each post, due to the query limit even though you are logged into your account. 
These scraped files are saved in a folder named as the instagram username. Transfer this folder into the `data` folder. 
3. Run `rag_chroma.py` to create a vector database and query the instagram posts. 
4. Run `conda install pytorch torchvision`

## Start-up
Run backend server: `python -m src.server.main`
Run streamlit frontend: `streamlit run src/server/streamlit_frontend.py`



