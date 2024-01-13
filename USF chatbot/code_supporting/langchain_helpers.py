from langchain.schema.messages import messages_to_dict
import json
'''
def messages_to_dict(messages):
    message_dicts = []
    for message in messages:
        message_dict = {
            "type": message.type,
            "data": message.data
        }
        message_dicts.append(message_dict)
    return message_dicts
'''

def extract_messages_from_buffer_mem(messages): # input something like st.session_state.conversation
    """
    Returns a json string of the messages in the conversation
    INPUT is something like 'st.session_state.conversation'
    """
    extracted_messages = messages.memory.chat_memory.messages
    ingest_to_db = messages_to_dict(extracted_messages)
    return json.dumps(ingest_to_db)
   