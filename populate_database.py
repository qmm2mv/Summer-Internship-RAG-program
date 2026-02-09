import asyncio
import os
import argparse
import shutil
import time
import logging
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
from langchain_community.document_loaders import TextLoader, UnstructuredExcelLoader, PyPDFLoader, CSVLoader, \
    Docx2txtLoader

# Configure logging
logging.basicConfig(level=logging.ERROR, format="%(asctime)s - %(levelname)s - %(message)s")

# use absolute paths to ensure it works no matter where you run the script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
#set paths for database and data within our current directory
FAISS_PATH = os.path.join(BASE_DIR, "faiss")
DATA_PATH = os.path.join(BASE_DIR, "data")

#this dictionary sets mapping for file extensions to the loader class name
LOADER_MAPPING = {
    ".txt": "TextLoader",
    ".pdf": "PyPDFLoader",
    ".xlsx": "UnstructuredExcelLoader",
    ".xls": "UnstructuredExcelLoader",
    ".csv": "CSVLoader",
    ".docx": "Docx2txtLoader",
}

def get_user_inputs():
    #inputting chunk sizes with checks for only valid responses
    while True:
        user_chunk_size = input("What size do you want your chunks to be? Default is 200: ") or "200"
        try:
            chunk_size = int(user_chunk_size)
            if chunk_size <= 0:
                raise ValueError("Chunk size must be positive")
            break
        except ValueError:
            print("Please enter a valid positive integer")
#takes overlaps with checks for only valid responses
    while True:
        user_chunk_overlap = input("What overlap do you like your chunks to have? Default is 80: ") or "80"
        try:
            chunk_overlap = int(user_chunk_overlap)
            if chunk_overlap < 0 or chunk_overlap >= chunk_size:
                raise ValueError("Chunk overlap must be non-negative and less than chunk size")
            break
        except ValueError:
            print(f"Please enter a valid integer between 0 and {chunk_size - 1}")

    while True:
        splitter_type = input(
            "What type of splitter do you want? Recursive (narrative text), Character (short paragraphs), Token (LLM-optimized). Default is token: ").lower() or "token"
        if splitter_type in ["token", "character", "recursive"]:
            break
        print("Please enter a valid splitter type (recursive, character, token).")
    user_folder=input("Enter folder filter (optional): ") or None
    folder_filter=user_folder
#print statements for user confirmation
    print(f"✅ Using chunk size: {chunk_size}")
    print(f"✅ Using chunk overlap: {chunk_overlap}")
    print(f"✅ Using splitter type: {splitter_type.capitalize()}")
    print(f"✅ Using folder filter: {folder_filter}")
    return chunk_size, chunk_overlap, splitter_type, folder_filter

def main(cli_args=None):
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Populate FAISS vector store with document chunks")
    parser.add_argument("--reset", action="store_true", help="Reset the database.", default=True)
    parser.add_argument("--chunk-size", type=int, default=None,
                       help="Chunk size for text splitting (default: prompt user or 200)")
    parser.add_argument("--chunk-overlap", type=int, default=None,
                       help="Chunk overlap for text splitting (default: prompt user or 80)")
    parser.add_argument("--splitter-type", type=str, default=None, choices=["recursive", "character", "token"],
                       help="Type of text splitter (default: prompt user or token)")
    parser.add_argument("--folder-filter", type=str, default=None,
                       help="Subfolder within data directory to load files from (e.g., 'uae'). Default: load all files in data directory.")
    args = parser.parse_args(cli_args)
    chunk_size = args.chunk_size
    chunk_overlap = args.chunk_overlap
    splitter_type = args.splitter_type
    folder_filter = args.folder_filter
    if chunk_size is None or chunk_overlap is None or splitter_type is None or folder_filter is None:
        chunk_size, chunk_overlap, splitter_type, folder_filter = get_user_inputs()

    # Reset database if requested
    if args.reset:
        #print("🔄 Resetting database...")
        logging.info("Clearing database")
        clear_database()
        #print("✅ Database reset.")

#loading documents
    print("📄 Loading documents...")
    start = time.time()
    documents = load_documents_parallel(folder_filter)
    print(f"✅ Loaded {len(documents)} documents in {time.time() - start:.2f}s.")

    #if documents is an empty list, exit the program
    if not documents:
        print("⚠️ No documents found in the specified folder. Exiting.")
        return

#splitting documents
    print("✂️ Splitting documents into chunks...")
    chunks = split_documents(documents, chunk_size=chunk_size, chunk_overlap=chunk_overlap, splitter_type=splitter_type)
    print(f"✅ Split into {len(chunks)} chunks.")

#adding chunks to database
    print("📦 Adding chunks to database. This may take a while...")
    start = time.time()
    add_to_db(chunks)
    print(f"✅ Database updated in {time.time() - start:.2f}s.")
#Finished

#main function for loading, calls helper functions,
#1.load_file_batch-processing batches of size 10
#2.load_single_file-processing single files
#3.async_load_documents_parallel-parallel processing of batches
async def async_load_documents_parallel(folder_filter=None):
    #if the filter exists use that
    if folder_filter:
        target_path = os.path.join(DATA_PATH, folder_filter)
        logging.info(f"Loading documents from '{folder_filter}' folder in '{DATA_PATH}'...")
    else:#otherwise use data path
        logging.info("No folder filter provided. Loading all files in data directory.")
        target_path = DATA_PATH
    if not os.path.exists(target_path) or not os.path.isdir(target_path):
        logging.error(f"Data directory '{target_path}' is not a valid directory.")
        return []

    #files variable stores all files found in target path
    files = [(f, os.path.getsize(os.path.join(target_path, f)))
             for f in os.listdir(target_path)
             if os.path.isfile(os.path.join(target_path, f))]
    if not files:
        logging.warning(f"No files found in {target_path}.")
        return []


    # Sort files by size and extension to prioritize smaller/simpler files
    files.sort(key=lambda x: (x[1], os.path.splitext(x[0])[1]))

    batch_size = 10  # Adjust based on testing
    file_batches = [files[i:i + batch_size] for i in range(0, len(files), batch_size)]
    documents = []
    #setting up threadpool executor object for parallel processing
    #max workers is set to 4 times the number of CPUs
    #defaults to 1 if less than 4 CPUs are available
    max_workers = min(os.cpu_count() * 4, len(files)) or 1
    executor = ThreadPoolExecutor(max_workers=max_workers)

    try:
        # for each batch, we call load_file_batch helper function
        tasks=[]
        for batch in file_batches:
            tasks.append(load_file_batch(batch, executor, target_path))

        #.gather method runs all tasks concurrently and returns a list of results
        results = await asyncio.gather(*tasks, return_exceptions=True)

        #we iterate over the list of results and see if there is an exception
        #otherwise, we add them to the documents list
        #single bad file will raise error, but not suspend whole process
        for result in results:
            if isinstance(result, Exception):
                logging.error(f"Error processing batch: {str(result)}")
            elif result:
                documents.extend(result)
    finally:
        executor.shutdown(wait=True)
    return documents

#our helper function for load documents parallel
async def load_file_batch(batch, executor, target_path):
    batch_documents = []

#calls the single file loader helper function for each file in the batch
    for file, _ in batch:
        docs = await load_single_file(os.path.join(target_path, file), executor)
        if docs:
            batch_documents.extend(docs)
    return batch_documents

#other helper function for loading a single document in a batch
#takes data folder and executor object as arguments
async def load_single_file(file_path, executor):
    """
    Load a single file using loader classes defined in LOADER_MAPPING.
    Always offloads to executor to avoid blocking the event loop.
    """
    filename = os.path.basename(file_path)
    ext = os.path.splitext(filename)[1].lower()
    loader_class_name = LOADER_MAPPING.get(ext)

    # Loader classes lookup
    loader_classes = {
        "TextLoader": TextLoader,
        "PyPDFLoader": PyPDFLoader,
        "UnstructuredExcelLoader": UnstructuredExcelLoader,
        "CSVLoader": CSVLoader,
        "Docx2txtLoader": Docx2txtLoader,
    }
    #if loader_mapping.get returns nothing warns of unsupported file type
    if not loader_class_name:
        logging.warning(f"Unsupported file type: {filename}")
        return []
    loader_class = loader_classes.get(loader_class_name)
    if not loader_class:
        logging.warning(f"Loader class not found for: {filename}")
        return []

    #creates running loop
    loop = asyncio.get_running_loop()

#uses designated loader class
    #logs success or failure
    try:
        logging.info(f"Loading: {filename}")
        loader = loader_class(file_path)
        documents = await loop.run_in_executor(executor, loader.load)
        logging.info(f"Loaded {filename}")
        return documents
    except Exception as e:
        logging.error(f"Error loading {file_path}: {str(e)}")
        await asyncio.sleep(1)  # wait before retrying
    return []

#synchronous function for loading documents in parallel
def load_documents_parallel(folder_filter):
    start = time.time()
    if folder_filter:
        logging.info(f"Loading documents from '{folder_filter}' folder in '{DATA_PATH}'...")
    logging.info("Running load_documents_parallel. This may take a while...")
    documents = asyncio.run(async_load_documents_parallel(folder_filter))
    logging.info(f"Loaded {len(documents)} documents in {time.time() - start:.2f}s")
    return documents

#splitting into chunks
def split_documents(documents, chunk_size, chunk_overlap, splitter_type):
    from langchain_text_splitters import RecursiveCharacterTextSplitter, CharacterTextSplitter, TokenTextSplitter
    try:
        if splitter_type == "recursive":
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                length_function=len,
                is_separator_regex=False,
            )
        elif splitter_type == "character":
            text_splitter = CharacterTextSplitter(
                separator="\n\n",
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                length_function=len,
                is_separator_regex=False,
            )
        elif splitter_type == "token":
            text_splitter = TokenTextSplitter(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
            )
        chunks = text_splitter.split_documents(documents)
        logging.info(f"Created {len(chunks)} document chunks")
        return chunks
    except Exception as e:
        logging.error(f"Error splitting documents: {e}")
        return documents

#adding chunks to database
#longest step
def add_to_db(chunks):
    from langchain_community.vectorstores import FAISS
    from get_embedding_function import get_embedding_function
    import faiss
    #if split_documents returns empty list, exit the program
    try:
        if not chunks:
            logging.error("No chunks to add. Error in splitting documents.")
            return
#call the embedding function from get_embedding_function.py
        logging.info(f"Adding {len(chunks)} documents")
        embedding_function = get_embedding_function()

#batch size of 500 chunks each about 200 long
        batch_size = 500
        first_batch = chunks[:batch_size]
        #initializees database
        vectorstore = FAISS.from_documents(first_batch, embedding_function)

#uses tpdm as a progress bar to watch
        for i in tqdm(range(batch_size, len(chunks), batch_size), desc="Adding batches to FAISS"):
            batch = chunks[i:i + batch_size]
            try:
                #aqdds chunks to vector store object
                vectorstore.add_documents(batch)
            except Exception as e:
                logging.error(f"Error adding batch {i // batch_size + 1}: {e}")

        #creates folder for database if it doesn't exist
        os.makedirs(FAISS_PATH, exist_ok=True)
        faiss.write_index(vectorstore.index, os.path.join(FAISS_PATH, "faiss.index"))
        vectorstore.save_local(FAISS_PATH)
        logging.info("Database updated successfully")
    except Exception as e:
        logging.error(f"Error in add_to_db: {e}")

def clear_database():
    try:
        if os.path.exists(FAISS_PATH):
            shutil.rmtree(FAISS_PATH)
            logging.info(f"Deleted database at {FAISS_PATH}")
            print(f"🗑️ Deleted existing database at '{FAISS_PATH}'.")
    except Exception as e:
        logging.error(f"Error clearing database: {e}")

if __name__ == "__main__":
    main()
