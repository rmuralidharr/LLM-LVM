import streamlit as st
import os
import pinecone
from langchain.prompts.prompt import PromptTemplate
from langchain.chains import ConversationChain
from langchain.memory import ConversationSummaryMemory, ConversationKGMemory, ConversationSummaryBufferMemory
from langchain.memory import  ConversationBufferWindowMemory, ConversationBufferMemory, ConversationEntityMemory
from langchain.callbacks import get_openai_callback
from langchain.vectorstores import Pinecone
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from dataclasses import dataclass
from langchain.chains import ConversationalRetrievalChain
from typing import Literal
from dotenv import load_dotenv
from langchain.memory.prompt import ENTITY_MEMORY_CONVERSATION_TEMPLATE
from langchain.schema.messages import messages_from_dict, messages_to_dict
from langchain.callbacks import get_openai_callback
import sqlite3
from langchain_helpers import extract_messages_from_buffer_mem
import json
import mail
from langchain.callbacks import get_openai_callback
from dataclasses import dataclass
from typing import Literal
from datetime import datetime
from streamlit_modal import Modal
import streamlit.components.v1 as components
from chat_history_db import is_email_in_database, fetch_u_number_from_database, fetch_name_from_database, insert_new_user_into_database, fetch_user_from_database, insert_conversation, fetch_conersations_from_database

def load_css():
    """Load the CSS to allow for styles.css to affect the look and feel of the Streamlit interface."""
    with open("static/styles.css", "r") as f:
        css = f"<style>{f.read()}</style>"
        st.markdown(css, unsafe_allow_html=True)

def initialize_vector_store():
    """Initialize a Pinecone vector store for similarity search."""
    pinecone.init(api_key=os.getenv('PINECONE_API_KEY'), environment=os.getenv('PINECONE_ENVIRONMENT'))
    index = pinecone.Index(os.getenv('PINECONE_INDEX_NAME'))
    embed_model = OpenAIEmbeddings(model="text-embedding-ada-002")
    vectorstore = Pinecone(index, embed_model, "text")
    return vectorstore

def initialize_session_state():
    """Initialize the session state variables for Streamlit."""
    if "history" not in st.session_state:
        st.session_state.history = []
    if "token_count" not in st.session_state:
        st.session_state.token_count = 0
    if "llm" not in st.session_state:
        st.session_state.llm = ChatOpenAI(
            temperature=0,
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            model_name="gpt-3.5-turbo-16k",
            max_tokens=10000,
            
        )
    if "conversation" not in st.session_state:
        # create a connection to OpenAI text-generation API
        st.session_state.buffer_memory = ConversationSummaryMemory(llm=st.session_state.llm, max_token_limit=10000)
        st.session_state.conversation = ConversationChain(
            llm=st.session_state.llm,
            memory= st.session_state.buffer_memory,
            verbose=True,              
        )
    if "email" not in st.session_state:
        st.session_state.email = ""
    if "u_number" not in st.session_state:
        st.session_state.u_number = ""
    if "name" not in st.session_state:
        st.session_state.name = ""
    if "status" not in st.session_state:
        st.session_state.status = ""
    if "initial_prompt" not in st.session_state:
        st.session_state.initial_prompt = ""


@dataclass
class Message:
    """Class for keeping track of a chat message."""
    origin: Literal['human', 'ai']
    message: str

def on_click_callback():
    """Function to handle the submit button click event."""
    with get_openai_callback() as cb:
        # Get the human prompt in session state (read from the text field)
        print(">>>> ONCLICK CALLBACK<<<<", datetime.now())
        human_prompt = st.session_state.human_prompt
        
        st.session_state.history.append(
        Message("human", human_prompt) 
    )
    
    print(f">>>> NAME: {st.session_state.name} <<<<")
    
    with get_openai_callback() as cb:
        
        ######################################################################################        
        # if no email, then process prompt to get email 
        # check if email exists in database, if so, populate name, email and status from database
        ######################################################################################
        if st.session_state.email == "": 
            # get the human prompt in session state (read from text field)
            print(">>>> CHECKING EMAIL, U-NUMBER, AND NAME <<<<", datetime.now())
            
            # get the user's email
            
            # call llm to extract email, 
            response = st.session_state.llm.predict(
                f"""[INST]Extract an email address this from this message.
                For any missing value, return the word missing[/INST]
                
                Human:
                    {human_prompt}
                """,
                max_tokens=10000, 
                stop=["\n"]
            )
                        
            if response == "missing":
                st.session_state.history.append(
                    Message("ai", f"Pardon me, I was unable to extract your deatils. Please try again!") 
                )
            else:
                st.session_state.email = response
                try:
                    mail.welcome_send_mail(response)
                    print("Mail send successfully!!")
                except Exception as e:
                    print(f"An error occurred: {str(e)}")

                if is_email_in_database(st.session_state.email):
                    (st.session_state.email, st.session_state.u_number, st.session_state.name, st.session_state.previous_conversation) = fetch_user_from_database(st.session_state.email)
                    if st.session_state.previous_conversation != "": # if the user has chatted with the bot before
                        # will need to reinitialize the conversation chain with the new buffer memory
                        st.session_state.buffer_memory.predict_new_summary(messages_from_dict(json.loads(st.session_state.previous_conversation)), f"{st.session_state.conversation.memory.buffer}")
                        st.session_state.conversation = ConversationChain(
                            llm=st.session_state.llm,
                            memory=st.session_state.buffer_memory,
                            verbose=True,              
                        )
                    st.session_state.history.append(                        
                        Message("ai", f"Welcome back {st.session_state.name}!\n\n\nI see that you have interacted with me before.\n\nI am loading your conversation history '{st.session_state.previous_conversation}'.\n\nWhat can I assist you with today?")
                        #Message("ai", f"Welcome back {st.session_state.name}!\n\n\nI see that you have interacted with me before.\n\n What can I assist you with today?")
                    )
                else:
                    st.session_state.history.append(
                        Message("ai", f"Thank you. I have recorded your email as {st.session_state.email}. Before I can answer your questions, please provide me with your name and U-Number.")
                    )
                    
        ###################################################        
        # if no name, then this email wasn't in the database
        ###################################################
        elif st.session_state.name == "": # if the user has not provided their name
                
            # let's get the name, and then create the record for this user in the database
                
            # call llm to extract ename, 
            response_name = st.session_state.llm.predict(
                f"""[INST]Extract a human name from this from this message.
                    For any missing value, return the word missing[/INST]
                
                    Human:
                        {human_prompt}
                """,
                max_tokens=10000, 
                stop=["\n"]
            )

            # Call llm to extract the email
            response_u_number = st.session_state.llm.predict(
                f"""[INST]Extract an u_number from this message.
                    For any missing value, return the word missing[/INST]

                    Human:
                        {human_prompt}
                """,
                max_tokens=10000, 
                stop=["\n"]
            )
                        
            if response_name == "missing":
                st.session_state.history.append(
                    Message("ai", f"Sorry, I was not able to extract your name. Please try again!") 
                )
            else: 
                #response_email=''            
                st.session_state.status = "Unregistered"
                st.session_state.name = response_name
                st.session_state.u_number = response_u_number
                


                    
                 # if we made it here, we have an u_number
                insert_new_user_into_database( st.session_state.u_number,st.session_state.email, st.session_state.name, "")
                st.session_state.history.append(
                    Message("ai", f"Thank you. I have recorded your name as {st.session_state.name}, U-Number as {st.session_state.u_number} and email address as {st.session_state.email}. How can I help you today?")
                )
                
        else:
    
            print(">>>> REGULAR RESPONSE WITH VECTOR STORE LOOKUP <<<<", datetime.now())

            # conduct a similarity search on our vector database
            vectorstore = initialize_vector_store()
            similar_docs = vectorstore.similarity_search(
                human_prompt,  # our search query
                k=7  # return relevant docs
            )
            print(">>>> FINISHED VECTOR STORE LOOKUP <<<<", datetime.now())
            
            # create a prompt with the human prompt and the context from the most similar documents
            prompt = f"""[INST]Your are a University of South Florida chatbot. The name of the human is {st.session_state.name}, their U_Number is {st.session_state.u_number} and their email address is {st.session_state.email}. Based on the question give the appropriate detailed response based on the knowledge base. Only if the questions are related to MS BAIS program mention that for further inquiries please drop a mail to muma-msbais@usf.edu along with your U-number.\n\n
            When someone asks a question other than MS BAIS program do not ask them to drop mail to muma-msbais@usf.edu since this mail id is not for other things like housing, employment, immigration related information.
            Always structure your answers in point-wise with appropriate details. Also, when someone asks question about other universities or things unrelated to University of South Florida please tell them that you do not have information about it and this is very important! \n\n[/INST]\n\n
        
            Context:" \n
            "{' '.join([doc.page_content for doc in similar_docs])}" \n
            
            
            Human:\n
            "{human_prompt}" \n\n                        
        
            """
        
            # get the llm response from prompt
            llm_response = st.session_state.conversation.run(
                prompt
            )
            print(">>>> FINISHED CONVERSATION RUN <<<<", datetime.now())

            #store the ai response
            st.session_state.history.append(
                Message("ai", llm_response) 
            )
            
            #insert_conversation(email=st.session_state.email, conversation= json.dumps(extract_messages_from_buffer_mem(st.session_state.buffer_memory)))
            
                        
            print(">>>> FINISHED REGULAR RESPONSE WITH VECTOR STORE LOOKUP <<<<", datetime.now())
        
        # keep track of the number of tokens used
        st.session_state.token_count += cb.total_tokens
        print(">>>> EXITING ONCLICK <<<<", datetime.now())


#############################
# MAIN PROGRAM

# initializations
print(">>>> INITIALIZE DOTEV <<<<", datetime.now())
load_dotenv() # load environment variables from .env file
print(">>>> INITIALIZE CSS <<<<", datetime.now())
load_css() # need to load the css to allow for styles.css to affect look and feel
print(">>>> INITIALIZE SESSION STATE <<<<", datetime.now())
initialize_session_state() # initialize the history buffer that is stored in UI  

# this posts the first AI message to the user, but we need to put this in an if statement, as 
# streamlit will run this code every time the page is refreshed. We check to see if the user's 
# email address is blank, if so, then we are chatting with the user for the first time
if st.session_state.email == "" and st.session_state.email!="missing": # if this is the first time the user is chatting with the bot
    st.session_state.history.append(
        Message("ai", "Hello! I am Rocky the Bull, the chatbot for the MS BAIS program at the University of South Florida. Before I can assist you, please provide your email address.") 
    )

# create the Streamlit UI
st.markdown("<img src='https://raw.githubusercontent.com/AkshayRamesh23/Chatbot/main/usf_muma_logo.png' width=250 height=60>", unsafe_allow_html=True)
st.markdown("<strong style='font-size: 30px;'>LangChain based ChatBot 🦜🔗</strong>", unsafe_allow_html=True)
#st.title("LangChain based MSBAIS Student Chatbot 🦜🔗")
chat_placeholder = st.container() # container for chat history
prompt_placeholder = st.form("chat-form") # chat-form is the key for this form. This is used to reference this form in other parts of the code
debug_placeholder = st.empty() # container for debugging information
label="feed back"
close_bot=st.expander(label, expanded=True)


# below is the code that describes how each of the three containers are displayed

with chat_placeholder:  # Container for chat history
    for chat in st.session_state.history:
        div = f"""
            <div class="chat-row {'row-reverse' if chat.origin == 'human' else ''}">
                <img class="chat-icon" src="{'https://raw.githubusercontent.com/AkshayRamesh23/Chatbot/main/user_logo.png' if chat.origin == 'human' else 'https://raw.githubusercontent.com/AkshayRamesh23/Chatbot/main/rocky_the_bull.png'}" width=40 height=55>
                <div class="chat-bubble {'human-bubble' if chat.origin == 'human' else 'ai-bubble'}">
                    &#8203;{chat.message}
                </div>
            </div>
        """
        st.markdown(div, unsafe_allow_html=True)
    for _ in range(3):  # Add blank lines between chat history and input field
        st.markdown("")

with prompt_placeholder:
     # this is the container for the chat input field
    col1, col2 = st.columns((6,1)) # col1 is 6 wide, and col2 is 1 wide
    col1.text_input(
        "Chat",
        placeholder="Please enter your email address here",
        label_visibility="collapsed",
        key="human_prompt",  # this is the key, which allows us to read the value of this text field later in the callback function
    )
    col2.form_submit_button(
        "Submit",
        type="primary",
        on_click=on_click_callback,  # important! this set's the callback function for the submit button
    )


#chat_list=' '.join([abcd for abcd in st.session_state.history])
chat_list=[]

with st.expander("feed back"):
    modal = Modal(key="Demo Modal",title="Feedback")
    open_modal = st.button("Stop the bot")
    st.write('''Contact information: Han Reichgelt\n
Graduate Coordinator, MS in Business Analytics & Information Systems\n
School of Information Systems and Management\n
Muma College of Business\n
Phone: (727) 873-4786\n
muma-msbais@usf.edu  ''')

    print(st.session_state.history)
    print(type(st.session_state.history))
 
    if open_modal:

        #insert_conversation(email=st.session_state.email, conversation= json.dumps(extract_messages_from_buffer_mem(st.session_state.buffer_memory)))
        insert_conversation(email=st.session_state.email, conversation= json.dumps(messages_to_dict(st.session_state.conversation.memory.chat_memory.messages)))
        mail.end_send_mail(st.session_state.email)
           
 
        html_string = '''
            <h3>Please provide Your valubale feedback</h3>
            <script language="javascript">
            document.querySelector("h3").style.color = "#baf8ba";
            </script>
            '''
        components.html(html_string)
        poor=st.button("poor")
        medium=st.button("medium")
        good=st.button("good")
        st.write(f"Checkbox checked: {good}")
        print(good)
        if good:
            """close the pop and now update the database and send mail"""
            feedback_score='good'
            modal.close()
        elif medium:
            """close the pop and now update the database and send mail"""
            feedback_score='medium'
            modal.close()
        elif poor:
            """close the pop and now update the database and send mail"""
            feedback_score='poor'
            modal.close()

        st.stop()
# Use the function to collect feedback
#collect_feedback_and_insert_conversation()

                
#debug_placeholder.caption(  # display debugging information
    ## THERE IS A BUG IN THE CURRENT IMPLEMENTATION. THE SUMMARY IS NOT BEING UPDATED WHEN LOADING FROM PREVIOUS CONVERSATION
    ## FROM THE DATABASE. THE MESSSAGES ARE THERE IN THE ConversationalSummaryMemory, BUT THE SUMMARY IS NOT BEING UPDATED
    ## with past conversational data. Need to explore this more. I've used predict_new_summary, which should address this
    ### but it is not.
#    f"""
    # Used {st.session_state.token_count} tokens \n
    # Debug Langchain.coversation:
    # {st.session_state.conversation.memory.buffer}
    # """)
