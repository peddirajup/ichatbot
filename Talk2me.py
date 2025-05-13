import streamlit as st
import os
import json
import requests
import uuid
from azure.storage.blob import BlobServiceClient
import openai
from streamlit_autorefresh import st_autorefresh

st.title("💬 Chatbot")
st.caption("🚀 A Streamlit chatbot powered by OpenAI")

# Final Version - API Information removed
# Step-4.3   Create Query Embeddings (created based on Step-3, option 2)
# Step-4.4   Retrieve chunks from Azure AI Search (0222/2025)
# Step-4.5   Connect to GPT Model  -COPY OF EMBEDDING MODEL (0223/2025)


embedding_model_api_key = "6PlwSfc5l90C5ZAYxvNTCQmrsUOcQVpe8I8oDntCT2fOyNdbTH1AJQQJ99BBACHYHv6XJ3w3AAAAACOGbHd8"
embedding_model_base_url = "https://usa-r-m74d4o8f-eastus2.openai.azure.com/openai/deployments/text-embedding-ada-002-2/embeddings?api-version=2023-05-15"

inputText = "How will my team be able to ask questions or provide feedback about the V4.x.x data file layout specification?"
INDEX_NAME = "documents4"

SEARCH_API_KEY = "qWxoLJwD58Yru3vtKlKeafgZWp8BQcANaR5lA6zW4DAzSeAXG7ov"

Azure_openAI_endpoint = "https://nc-openai-txamd-0304.openai.azure.com/openai/deployments/gpt-4/chat/completions?api-version=2025-01-01-preview"
Azure_openAI_key = "DJx1R53kLVd80faICe2UNVd1KFRSaPyJ3Q6dkO2fGeMa60sveCJnJQQJ99BCACYeBjFXJ3w3AAABACOGcD3l"
deployment_name_GPT = "gpt-4"


# openai.api_type = "azure"
# openai.api_base = Azure_openAI_endpoint
# openai.api_version = "2024-08-01"
# openai.api_key = Azure_openAI_key


def generate_embeddings(inputText, api_key=embedding_model_api_key, base_url=embedding_model_base_url):
    # Define your Azure OpenAI Service details
    # headers = { "Content-Type": "application/json", "api-key": api_key }

    headers = {
        "Content-Type": "application/json",
        "api-key": api_key
    }

    embeddings = []

    # response = requests.post(f"{endpoint}/v1/embeddings", headers=headers, json=data)
    payload = {"input": inputText}
    response = requests.post(base_url, headers=headers, json=payload)

    # Print the response status code and content for debugging
    # print(f"Response Status Code: {response.status_code}")
    # print(f"Response Content: {response.content}")

    # Check if the response is successful
    if response.status_code == 200:
        response_data = response.json()
        # Check if 'data' key is in the response
        if 'data' in response_data and len(response_data['data']) > 0:
            # print(f"Response data: {response_data['data']}")
            embeddings = response_data['data']
        # print('test')
        else:
            print(f"Unexpected response structure: {response_data}")
    else:
        print(f"Error: Received status code {response.status_code}")
        print(f"Error details: {response.json()}")

    return embeddings


def hybrid_search(query, query_embedding, top_k=4):
    """

    Convert query to embedding and perform hybrid search in Azure AI Search.

    """

    # Step 3.2: Perform Hybrid Search

    url = f"https://0215-txamd-chatbot.search.windows.net/indexes/documents4/docs/search?api-version=2024-11-01-Preview"

    headers = {

        "Content-Type": "application/json",

        "api-key": SEARCH_API_KEY

    }

    # print (query_embedding[0]['embedding'])
    # print (query)
    search_payload = {
        "select": "id,Content",
        "vectorQueries": [{
            "kind": "vector",
            "fields": "embedding",
            "vector": query_embedding[0]['embedding'],
            "k": top_k
        }]
    }

    response = requests.post(url, headers=headers, json=search_payload)

    if response.status_code == 200:
        print("Chunks: ", response.json()["value"])
        return response.json()["value"]

    else:

        print(f"Error: {response.status_code} - {response.text}")

        return None


# function to generate response from GPT model
def retrieve_and_generate_response(query_text, retrieved_documents):
    # extract only content from retrieved documents
    retrieved_documents = [result["Content"] for result in retrieved_documents]
    context = "\n\n".join(retrieved_documents)

    # Step 2: Send to GPT for Answer Generation
    prompt = f"""
    You are an AI assistant that helps users learn from the information found in the source material.
    Answer the query using only the sources provided below.
    Use bullets if the answer has multiple points.
    Answer ONLY with the facts listed in the list of sources below. Cite your source when you answer the question
    If there isn't enough information below, say you don't know.
    Do not generate answers that don't use the sources below.


    Context:
    {context}

    Question:
    {query_text}

    Answer:
    """
    headers = {
        "Content-Type": "application/json",
        "api-key": Azure_openAI_key
    }

    payload = {
        "messages": [
            {"role": "system", "content": "You are a helpful AI assistant."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 700
    }

    # """ response = client.chat.completions.create(
    #     model= deployment_name_GPT,
    #     messages=[
    #         {"role": "system", "content": "You are a helpful AI assistant."},
    #         {"role": "user", "content": prompt}
    #     ],
    #     temperature=0.7,
    #     max_tokens=500
    # ) """

    # Step 3: Return GPT's Response
    response = requests.post(Azure_openAI_endpoint, headers=headers, json=payload)
    content = response.json()['choices'][0]['message']['content']
    # print(content)
    return content
    # print("\n response.json ================== \n",response.json())

    # return response["choices"][0]["message"]["content"]


# Example Usage GPT Model
# query = "What are the benefits of Azure AI Search?"
# response = retrieve_and_generate_response(query)
# print(response)

# Example Usage

def main():
   # st.title("ChatBot")

    # Generate embeddings for each chunk
    metadata = generate_embeddings(inputText)

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # React to user input
    if prompt := st.chat_input("Enter your question:"):
        # Display user message in chat message container
        st.chat_message("user").markdown(prompt)
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        retrieved_documents = hybrid_search(prompt, metadata)
        response = retrieve_and_generate_response(prompt, retrieved_documents)
        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            st.markdown(response)
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})


if __name__ == "__main__":
    main()
