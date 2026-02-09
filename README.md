# Summer-Internship-RAG-program
Retrieval Augmented Generation program that imports and embeds several different document types and embeds them into vector database. Uses vector space for semantic meaning search to feed to a local LLM via Ollama.


Getting started

Ollama
1.First we will need to download Ollama to run our local LLM. Head on over to https://ollama.com/download/windows
And download ollama. Installation next. This will take a lot of time so be patient.

2.Once you have downloaded ollama, go to your search bar and enter terminal. You should see a big box. Type ollama serve where your cursor already is. This will allow Ollama to be run on your computer.

3. Next, you need to enter ollama pull +name of your LLM in the terminal (See the full list of models here: https://ollama.com/search). This will download the LLM to be run locally. Since these are multiple gigabytes, it will take a few minutes. You can see which LLM’s you have downloaded by typing ollama list in the terminal.

I would recommend smollm:latest, phi3:mini, and qwen2.5:0.5b as they are the smallest. The LLM response is usually what takes the majority of time during the query.

Setting Directories
Downloading Documents
1.Download all of your documents and place them in the folder called “data” inside the RAG folder. Supported document types are .txt, .pdf, .xls, xlsx, .csv, and .docx. This is an important step because otherwise our RAG model will not have any context to give the LLM.

2. Open up wherever you run python and set up your working directory. You will need to install a few packages so open up python and install these packages

Install: pip install faiss-cpu (or faiss-gpu if GPU support is needed)
langchain_community (for FAISS vector store, document loaders, and text splitters)
Install: pip install langchain-community
langchain_huggingface (for HuggingFace embeddings)
Install: pip install langchain-huggingface
langchain_ollama (for interacting with Ollama LLM)
Install: pip install langchain-ollama
tiktoken (for token counting)
Install: pip install tiktoken
cachetools (for LRU cache)
Install: pip install cachetools
tqdm (for progress bars)
Install: pip install tqdm
unstructured (dependency for UnstructuredExcelLoader in langchain_community)
Install: pip install unstructured
docx2txt (for Docx2txtLoader to handle .docx files)
Install: pip install docx2txt
pandas (dependency for UnstructuredExcelLoader and CSVLoader)
Install: pip install pandas
PyPDF2 or pypdf (for PyPDFLoader to handle .pdf files)
Install: pip install pypdf
sentence-transformers (required for HuggingFaceEmbeddings with all-MiniLM-L6-v2)
Install: pip install sentence-transformers
concurrent.futures (standard library, no installation needed for ThreadPoolExecutor)

[for copy and paste]
pip install sentence-transformers
pip install pypdf
pip install pandas
pip install docx2txt
pip install tqdm
pip install cachetools
pip install langchain-ollama
pip install tiktoken
pip install langchain-huggingface
pip install langchain-community
pip install faiss-cpu
_____________


Steps for running the code manually:
Populating database
Computers can’t read words and tables like humans, and thus the documents need to be converted into embeddings for usage. Go over to populate_database.py and click run. There are a few different options, but I recommend the default ones. If you want to only upload a subfolder of data, enter that subfolder name. Everything in the data folder will be sent to the faiss database where we can properly use it. If you want to clear everything in the faiss database. Run python populate_database.py –”reset” in the python  terminal. This will clear everything out of the database and then add everything from data to it. One thing to note. If you populate the documents to the database, then add more documents to your data folder, and then run the populate database again without removing the old documents, you will have duplicates in the faiss database which will slow down performance and results. I would also recommend doing them in batches of several documents. I tried loading 25 and it took about 35 minutes, not a terrible amount of time but 3 took me about 30 seconds.

You should now be able to run query.py and feed your local LLM your prompts!

Entering Prompt/Parameters
There are going to be seven parameters you give the RAG model
Inputs 2-7 have presets and you can press enter to get the default argument.


1.Your prompt(required)
 self explanatory
Number of chunks that will be retrieved.(optional default =5)
 Each chunk is about 2000 characters long. The RAG model will find the number of chunks most relevant to your prompt. Think of it as a work cited for a book. A larger number of sources might have a more developed and intelligent answer but will take more time to gather. Best not to use too many. 10 would be the upper upper limit for the most advanced questions. Simpler responses might need as little as one or two.


2.Model name(default to phi3:mini)


3.Ouput file name Optional
-If you wish for response to be saved to a file, enter the name of the file

Max context-the max amount of words you want to send to your model(optional default=2000)
Source filter(optional, default=none)
If you have a specific file name you want to exclusively search on, then enter that name and it will only look on that file
Show chunks/true false(optional, default=false)
This will also print out the source content directly.


Go over to main and run main.py –interactive. Enter your inputs. Once you have entered your inputs it should take 1-2 minutes to run and output the prompt. Recommended to close other apps like browsers.

If you are running automated_run.py, this file will automatically run the main program several times based on the questions list variable and then save one file for every country in the countries list variable, every file will be named after its country and include the qwerty and response.

_____________


Steps for running the code automatically:

Running Automated

The automated_run.py combines the populate database and query steps and can run autonomously for as long as you want.

This code loops over two lists. The first is the list of subfolders in your data directory. The second is your list of questions. For each subfolder, the code will
1.reset the database and add the data from the subfolder to the index
2. Prompt the LLM with each question
3. Save the LLM’s response to a text file.


Output file
The file will be a .txt combined with the name of the folder. The format will be

Question #
–question–


Response:--response–

Sources:

