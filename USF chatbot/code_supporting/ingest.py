# This file is used to load the available knowledge sources and split in to chunks and load the data with embeddings in to the pinecone.
# load the necessary environment variables
import openai
import langchain
from dotenv import load_dotenv,find_dotenv

from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain import PromptTemplate
from langchain.chains import LLMChain
from langchain.chains import SimpleSequentialChain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.agents.agent_toolkits import create_python_agent
from langchain.tools.python.tool import PythonREPLTool
from langchain.python import PythonREPL
#from langchain.llms.openai import OpenAI
from langchain.document_loaders import DirectoryLoader
from langchain.document_loaders import PyPDFDirectoryLoader
from langchain.document_loaders import PyPDFLoader
from langchain.document_loaders import JSONLoader
from langchain.document_loaders import Docx2txtLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

import json
from pathlib import Path
from pprint import pprint
import pinecone
from tqdm.notebook import tqdm # need this to stop warning

import os
import pinecone # pip3 install "pinecone-client[grpc]"
from langchain.vectorstores import Pinecone

from pprint import pprint # pretty print

# load environmnet variables
load_dotenv('.env')
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINCECONED_ENVIRONMENT = os.getenv("PINCECONED_ENVIRONMENT")

def load_text_docs(path, chunksize=1000, overlap=100):
    """ Load all text files from a given directory

    Args:
        path (str): This is the subfolder path - be sure that this is relative to where you start the program
        chunksize (int, optional): Size of text chunks. Defaults to 1000.
        overlap (int, optional): Overlap between text chunks. Defaults to 100.

    Returns:
        list(Document): Returns a list of LangChain Document types
    """
    documents =  DirectoryLoader(path,silent_errors=True).load() # look up text loader in LangChain documentation

    return documents # return a list of chunks of text

#################################################################################################
def load_pdf_docs(path, chunksize=1000, overlap=100):
    """Load documents will recursively load a all the pdfs in a given directory path 
    and return a list of documents. 

    Args:
        chunksize (int, optional): _description_. Defaults to 1000.
        overlap (int, optional): _description_. Defaults to 100.

    Returns:
        _type_: _description_
    """    

    from langchain.document_loaders import PyPDFLoader
    from langchain.document_loaders import DirectoryLoader
    
    # load all pdfs in the directory
    # Each document will be a list of pages
    loader = DirectoryLoader(
        r"pdfs", 
        use_multithreading=True,
        loader_cls=PyPDFLoader,
        show_progress=True,
        recursive=True
    )
    pages = loader.load() # this returns a list of pages as Document types
    return pages
#################################################################################################
def split_docs_into_chunks(docs, chunksize=1000, overlap=100):
    """Accepts a list of Documents (see LangChain Document type/schema) and splits them 
    into a list of smaller documents. 

    Args:
        docs (list[Document]): List of LangChain Document types
        chunksize (int, optional): What is the largest page_content size per document. Defaults to 1000.
        overlap (int, optional): How much overlap between chunks. Defaults to 100.

    Returns:
        list[Document]: List of LangChain Document types that are smaller than the original documents
    """
    
    from langchain.text_splitter import RecursiveCharacterTextSplitter

    # create a text splitter
    text_splitter = RecursiveCharacterTextSplitter(
       # Set a really small chunk size, just to show.
        chunk_size = chunksize,
        chunk_overlap  = overlap
    )        
    
    # return a list of documents that result from splitting the original documents    
    return text_splitter.split_documents(docs)
import tiktoken

def num_tokens_from_string(string: str, encoding_name: str) -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens
#################################################################################################
def get_pinecone_index(dimensions=1536, metric='cosine'):
    """Used for free pinecone service which allows only one index
    Connects to pinecone and creates an index if one does not exist. 
    Deletes all indexes if one does exist.
    
    Requires Environmnet Variables to bet set:
        PINECONE_INDEX_NAME
        PINECONE_API_KEY
        PINCECONED_ENV
    
    Args:
        dimensions (int, optional): Dimensions of the vectors. Defaults to 1536.
        metric (str, optional): Distrance metrics to calculate similarity. Defaults to 'cosine'.
    """
    import pinecone
    import time
    import os
    from dotenv import load_dotenv

    # initialize pinecone client to connect to account
    pinecone.init(api_key=PINECONE_API_KEY, environment=PINCECONED_ENVIRONMENT)
    
    # for free account, you can only have one index
    # Here we delete all indexes...
    index_list = pinecone.list_indexes()
    while len(index_list) > 0:
        pinecone.delete_index(index_list[-1])
        index_list = pinecone.list_indexes()
        
    if PINECONE_INDEX_NAME not in pinecone.list_indexes():
        pinecone.create_index(
            PINECONE_INDEX_NAME,
            dimension=1536,
            metric='cosine'
        )
        # wait for index to finish initialization
        while not pinecone.describe_index(PINECONE_INDEX_NAME).status['ready']:
            time.sleep(1)
    
    # return a pinecone index connection
    return pinecone.Index(PINECONE_INDEX_NAME)
def load_embeddings_into_pinecone(index, chunks):
    """Accepts an an open pinecone index and a list of documents (of type list[Docuement])

    Args:
        index (pinecode.index): Open index to Pinecone index
        chunks (list[Document]): List of LangChain Document types
    """
    from langchain.vectorstores import Pinecone
    from langchain.embeddings.openai import OpenAIEmbeddings
    import os
    from dotenv import load_dotenv
    
    # load the necessary environment variables
    load_dotenv()    
    OPEN_AI_API_KEY = os.getenv("OPEN_AI_API_KEY")
    PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")
    
    # load embeddings into pinecone
    Pinecone.from_documents(
        chunks, 
        embedding=OpenAIEmbeddings(openai_api_key=OPEN_AI_API_KEY, model="text-embedding-ada-002"),
        index_name=PINECONE_INDEX_NAME
    ) 


#################################################################################################
#################################################################################################
def main():
    """ Main function to load documents, split into chunks, and load into pinecone"""
    
    # load docuemnts, split into chunks, and embed
    print(">>>>>>> Loading documents...")
    text_docs = load_text_docs("texts")
    #print(type(text_docs))
    #print(len(text_docs))
    pdf_docs = load_pdf_docs("pdfs") 
    #print(type(pdf_docs))
    #print(len(pdf_docs))
    # split documents into chunks
    print(">>>>>>> Splitting documents into chunks...")
    docs = pdf_docs + text_docs 
    chunks = split_docs_into_chunks(docs, chunksize=750, overlap=20)
    #print(type(chunks))
    #print(len(chunks))
    #chunks_str=str(chunks)
    #chunk1=chunks[0:4500]
    #chunks1_str=str(chunk1)
    #chunk2=chunks[4501:9001]
    #chunk2_str=str(chunk2)
    #chunk3=chunks[9002:13501]
    #chunk3_str=str(chunk3)
    #chunk4=chunks[13502:18001]
    #chunk4_str=str(chunk4)
    #chunk5=chunks[18002:]
    #chunk5_str=str(chunk5)
    #n1=num_tokens_from_string(chunks1_str,"cl100k_base")
    #n2=num_tokens_from_string(chunk2_str,"cl100k_base")
    #n3=num_tokens_from_string(chunk3_str,"cl100k_base")
    #n4=num_tokens_from_string(chunk4_str,"cl100k_base")
    #n5=num_tokens_from_string(chunk5_str,"cl100k_base")
    #print(n1)
    #print(n2)
    #print(n3)
    #print(n4)
    #print(n5)
     # create pinecone index
    print(">>>>>>> Creating pinecone index...")
    index = get_pinecone_index()
    
    # load embeddings into pinecone
    print(">>>>>>> Loading embeddings into pinecone...")
    load_embeddings_into_pinecone(index, chunks) # embeddings are calculated in the function
    
    # print finished message
    print("All finished!")
    

    

#################################################################################################
if __name__ == "__main__":
    main()