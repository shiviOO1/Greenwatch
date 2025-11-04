"""
Test script to demonstrate the enhanced chatbot capabilities
"""
from test import TableQuestionAnswering

# Initialize chatbot
print("Initializing chatbot...")
tqa = TableQuestionAnswering()
tqa.load_table('Model_assest/DiseaseChatbotData.csv')
print("Chatbot ready!\n")
print("=" * 80)

# Test cases
test_queries = [
    "hi",
    "hoi",
    "what are tomato diseases?",
    "show all tomato diseases",
    "tomato early blight",
    "how to treat tomato late blight?",
    "supplement for tomato mosaic virus",
    "what is tomato septoria leaf spot?",
    "help",
    "list all diseases",
    "thank you"
]

for query in test_queries:
    print(f"\n🔹 USER: {query}")
    print(f"🤖 BOT: {tqa.answer_query(query)}")
    print("-" * 80)
