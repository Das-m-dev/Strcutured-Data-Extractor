##Setup
- python -m venv .venv
- .venv\Scripts\Activate.ps1   
- pip install -r requirements.txt
- copy .env.example .env                           

##RUN
- python -m extractor.cli data/samples/invoice_001.txt 
- uvicorn extractor.api:app --reload                     
- streamlit run app/streamlit_app.py                    
- python -m evaluation.evaluate                          
- pytest                                                 
