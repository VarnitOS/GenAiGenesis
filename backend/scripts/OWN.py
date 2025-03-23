import requests
import json

BASE_URL = "http://localhost:5000/api/research"

def test_research_query():
    url = f"{BASE_URL}/query"
    payload = {
        "query": "What is the standard for a reasonable search under the Fourth Amendment?",
        "collections": ["case_law", "statutes"],
        "use_web_search": True,
        "max_web_results": 5
    }
    response = requests.post(url, json=payload)
    print("\n=== Research Query Results ===\n")
    print(response.json())
    return response.json().get("conversation_id")

def test_research_chat(conversation_id):
    url = f"{BASE_URL}/chat"
    payload = {
        "message": "What are the exceptions to the exclusionary rule?",
        "conversation_id": conversation_id,
        "include_context": True
    }
    response = requests.post(url, json=payload)
    print("\n=== Research Chat Results ===\n")
    print(response.json())

def test_get_conversation(conversation_id):
    url = f"{BASE_URL}/conversation/{conversation_id}"
    response = requests.get(url)
    print("\n=== Get Conversation Results ===\n")
    print(response.json())

def test_clear_conversation(conversation_id):
    url = f"{BASE_URL}/conversation/{conversation_id}"
    response = requests.delete(url)
    print("\n=== Clear Conversation Results ===\n")
    print(response.json())

def test_add_research_context(conversation_id):
    url = f"{BASE_URL}/context"
    payload = {
        "context": "Additional context about the query",
        "conversation_id": conversation_id
    }
    response = requests.post(url, json=payload)
    print("\n=== Add Research Context Results ===\n")
    print(response.json())

def test_clear_research_context(conversation_id):
    url = f"{BASE_URL}/context"
    payload = {
        "conversation_id": conversation_id
    }
    response = requests.delete(url, json=payload)
    print("\n=== Clear Research Context Results ===\n")
    print(response.json())

def main():
    conversation_id = test_research_query()
    if conversation_id:
        test_research_chat(conversation_id)
        test_get_conversation(conversation_id)
        test_add_research_context(conversation_id)
        test_clear_research_context(conversation_id)
        test_clear_conversation(conversation_id)
    else:
        print("Failed to obtain conversation_id from research query.")

if __name__ == "__main__":
    main()