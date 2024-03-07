import json
import os,sys,boto3
from langchain.embeddings import BedrockEmbeddings
from langchain.llms.bedrock import Bedrock
import numpy as np
from langchain.text_splitter import RecursiveCharacterTextSplitter  # split the pdf content data into  chunck ysing  Recursive character text Splitter
from langchain.document_loaders import PyPDFDirectoryLoader
import streamlit as st
#using titan embeddings model to generate embedding in aws  Titaan embedding model is provided by AWS

##data ingestion & vector embedding and vectore store
from langchain.vectorstores import faiss
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA

bedrock=boto3.client(service_name="bedrock-runtime")
bedrock_embeddings=BedrockEmbeddings(model_id="amazon.titan-embed-text-v1",Cleint=bedrock)

#data ingestion
def data_ingestion():
    loader=PyPDFDirectoryLoader("data")
    documents=loader.load()

    #split the content
    text_splitter=RecursiveCharacterTextSplitter(chunk_size=10000,chunk_overlap=1000)
    docs=text_splitter.split_documents(documents)
    return docs

# VETORE EMBEDDING AND VECTORE STORE
def get_vectore_store(docs):
    vectorestore_faiss=faiss.FAISS.from_documents(docs,bedrock_embeddings)

    vectorestore_faiss.save_local("faiss_index")

def get_claude_llm():
    #creating antropic model
    llm=Bedrock(model='ai21.j2-mid-v1',client=bedrock,model_kwargs={'maxToken':512})

    return llm

def get_llama2_llm():
    #creating antropic model
    llm=Bedrock(model='meta.llama2-70b-chat-v1',client=bedrock,model_kwargs={'maxToken':512})

    return llm

prompt_template="""
Human: use the following pieaces of content to provide a concise answer to the question at the end but use at least summarized with 250 words with .

<content>
{content}
</content>
question : {question}
Assistant:
"""

prompt =PromptTemplate(
    template=prompt_template,input_variables=["context","question"]

)

def get_response_llm(llm,vectorstore_faiss,query):
    qa=RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vectorstore_faiss.as_retriever(
            search_type="similarity", search_kwargs={"k":3}

        ),
        retrun_score_documnets=True,
        chain_type_kwargs={"prompt":PROMPT} 

    )
    answer=qa({"query":query})
    return answer['result']



def main():
    st.set_page_config("Chat PDF"
                       )
    st.header("Chat with PDF using AWS Bedrock")
    user_question=st.text_input("please ask a question from the PDF files"
                                )
    with st.sidebar:
        st.title("updat or craete vector store:")

        if st.button("Vectore Update"):
            with st.spinner("Processing .."):
                docs=data_ingestion()
                get_vectore_store(docs)
                st.success("done")

        if st.button("claude Update"):
            with st.spinner("Processing .."):
                faiss_index=faiss.FAISS.load_local("faiss_index",bedrock_embeddings)
                llm=get_claude_llm()
                st.write(get_response_llm(llm,faiss_index,user_question ))
                st.success("done")

if __name__=="__main__":
    main()
