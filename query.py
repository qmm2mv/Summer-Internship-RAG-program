import os
import logging
import logging.handlers
from typing import Dict, List, Optional, Union
import faiss
from langchain_community.vectorstores import FAISS
from langchain.prompts import ChatPromptTemplate
from langchain_ollama import OllamaLLM
from get_embedding_function import get_embedding_function
import tiktoken
from cachetools import LRUCache

# --- CONFIGURATION ---
#setting base director and faiss path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FAISS_PATH = os.path.join(BASE_DIR, "faiss")
#allows us to use faiss
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

#what is sent to the llm prior to the question, important for best results
PROMPT_TEMPLATE = """
{question}
Assume you are a legal expert codifying central bank legislation. Answer the following question exclusively based on the set of legislative documents enacted up to and including YEAR. Documents relevant to this query follow the filename pattern ISO2CODE_CBL_YEAR-MONTH.
Instructions:
• Respond directly to the specific  question.
• Your first sentence must clearly state only the correct option from the provided multiple-choice answers.
• In one or two sentences following your initial choice, explicitly reference the precise law, amendment, chapter, article, or document from which the information was obtained.
• Maintain brevity: limit your total response to a maximum of three sentences.
• Do not include additional advice, explanations beyond necessary citations, or external information.
• If you do not have the explicit answer to the question provided in the context, answer "I don't know.

Context retrieved from relevant documents:

{context}

---

"""

logging.basicConfig(level=logging.WARNING, format="%(asctime)s - %(levelname)s - %(message)s")
handler = logging.handlers.MemoryHandler(capacity=100, target=logging.StreamHandler())
logging.getLogger().addHandler(handler)
DB_INSTANCE = None
query_cache = LRUCache(maxsize=100)
tokenizer = tiktoken.get_encoding("cl100k_base")

# Initialize FAISS index
try:
    if os.path.exists(FAISS_PATH):
        faiss.omp_set_num_threads(6)
        DB_INSTANCE = FAISS.load_local(
            FAISS_PATH,
            embeddings=get_embedding_function(),
            allow_dangerous_deserialization=True
        )
        logging.info("FAISS DB loaded successfully.")
    else:
        logging.error(f"FAISS DB not found at {FAISS_PATH}. Ensure populate_database.py has been run.")
except Exception as e:
    logging.error(f"Failed to load FAISS index: {e}")

# --- FUNCTIONS ---
#1. returns database, raises error if one not found
def get_db():
    if DB_INSTANCE is None:
        raise FileNotFoundError(f"FAISS DB not initialized. Ensure {FAISS_PATH} contains valid index files.")
    return DB_INSTANCE
#2 returns the number of tokens in a text for counting
def count_tokens(texts: List[str]) -> List[int]:
    return [len(tokenizer.encode(text)) for text in texts]  # Approximation
#3 query rag, main thing
#a. conducts search
#b. joins chunks into a single string
#c. sends prompt to llm
#d. gets response from llm
#e. prints output and sources
async def query_rag(query_text: str,
                    k: int = 5,
                    model_name: str = "phi3:mini",
                    max_context_length: int = 2000,
                    source_filter: Optional[str] = None,
                    show_chunks: bool = False) -> Optional[Dict[str, Union[str, List[Dict]]]]:
    try:
        #initialize db
        db = get_db()
        # Check cache to see if that question has been asked
        # if found time is reduced by 60-80%
        cache_key = f"{query_text}:{source_filter or ''}:{k}:{max_context_length}:{model_name}"
        if cache_key in query_cache:
            logging.info("Query result cache hit")
            return query_cache[cache_key]
        #creates filter
        if source_filter:
            filter_dict = {"source": source_filter}
        else:
            filter_dict = None
        # Perform similarity search
        #returns top k results and their scores
        results = db.similarity_search_with_score(query_text, k=k, filter=filter_dict)

        #something wrong with the search
        if not results:
            logging.warning("No chunks found. Either empty database or improper embeddings")
            return None

        #limits for max context length and number of chunks
        context_chunks, context_length = [], 0
        contents = [doc.page_content for doc, _ in results]
        token_lengths = count_tokens(contents)
        for (doc, score), token_len in zip(results, token_lengths):
            if context_length + token_len <= max_context_length:
                context_chunks.append((doc, score))
                context_length += token_len
            else:
                break

        #retrivesw chunk source metadata
        if show_chunks:
            for i, (doc, score) in enumerate(context_chunks, start=1):
                source = doc.metadata.get("source", "Unknown")
                page = doc.metadata.get("page", "Unknown")
                info_msg = f"Chunk {i} - Source: {source}, Page: {page}"
                logging.info(info_msg)
                if show_chunks:
                    print(f"\n{info_msg}")
                    print(f"Content: {doc.page_content[:200]}...")

        # Join context chunks into a single string for the LLM
        context_texts = []
        for doc, _ in context_chunks:
            context_texts.append(doc.page_content)
        # Format sources as a string and append to context
        sources = [
            {
                "id": doc.metadata.get("id", "Unknown"),
                "source": doc.metadata.get("source", "Unknown"),
                "page": doc.metadata.get("page", "Unknown"),
            }
            for doc, score in context_chunks
        ]
        # Create a formatted string for sources
        sources_text = "\n".join(
            f"Source {i}: {os.path.basename(s['source'])} (Page {s['page']})"
            for i, s in enumerate(sources, 1)
        )
        context_texts.append(f"\nSources:\n{sources_text}")
        full_context_text = "\n\n---\n\n".join(context_texts)

        # Create and send prompt to LLM
        prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
        prompt_string = prompt_template.format(context=full_context_text, question=query_text)
        model = OllamaLLM(model=model_name)
        #gets response from llm
        try:
            response_text = model.invoke(prompt_string)
        except Exception as e:
            logging.error(f"LLM invocation failed: {e}")
            return None

        if not response_text:
            logging.warning("Model returned no response.")
            return None
        #printing the output and sources
        #print("🧠 MODEL RESPONSE:\n", response_text)

        #print("\n📚 SOURCES:")
        #for i, s in enumerate(sources, 1):
        #    print(f"{i}. {s['source']} (Page {s['page']}")

        response = {"text": response_text, "sources": sources}
        query_cache[cache_key] = response
        return response

    except Exception as e:
        logging.error(f"Query failed: {e}")
        return None
