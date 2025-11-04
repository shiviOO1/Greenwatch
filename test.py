import pandas as pd
import re
from difflib import SequenceMatcher

class TableQuestionAnswering:
    def __init__(self):
        self.table = None
        self.greetings = ['hi', 'hello', 'hey', 'hoi', 'greetings', 'good morning', 'good afternoon', 'good evening']
        self.thanks = ['thank', 'thanks', 'thank you', 'thx']
        self.help_keywords = ['help', 'what can you do', 'commands', 'options']
        self.list_keywords = ['list', 'show all', 'all diseases', 'what diseases']
        
    def load_table(self, table_path):
        # Try multiple encodings to handle different file formats
        encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252', 'windows-1252']
        
        for encoding in encodings:
            try:
                self.table = pd.read_csv(table_path, encoding=encoding)
                self.table = self.table.astype(str)
                print(f"Successfully loaded table with {encoding} encoding")
                break
            except (UnicodeDecodeError, UnicodeError):
                continue
        else:
            # If all encodings fail, try with error handling
            self.table = pd.read_csv(table_path, encoding='utf-8', errors='ignore')
            self.table = self.table.astype(str)
            print("Loaded table with utf-8 encoding (ignoring errors)")
    
    def similarity(self, a, b):
        """Calculate similarity between two strings"""
        return SequenceMatcher(None, a.lower(), b.lower()).ratio()
    
    def is_greeting(self, query):
        """Check if the query is a greeting"""
        query_lower = query.lower().strip()
        return any(greeting in query_lower for greeting in self.greetings)
    
    def is_thanks(self, query):
        """Check if the query is a thank you message"""
        query_lower = query.lower().strip()
        return any(thank in query_lower for thank in self.thanks)
    
    def is_help(self, query):
        """Check if the query is asking for help"""
        query_lower = query.lower().strip()
        return any(keyword in query_lower for keyword in self.help_keywords)
    
    def is_list_request(self, query):
        """Check if user wants to see all diseases"""
        query_lower = query.lower().strip()
        return any(keyword in query_lower for keyword in self.list_keywords)
    
    def get_all_diseases(self):
        """Get list of all diseases grouped by plant"""
        diseases_by_plant = {}
        for idx, row in self.table.iterrows():
            disease_name = row['disease_name']
            if ':' in disease_name:
                plant, disease = disease_name.split(':', 1)
                plant = plant.strip()
                disease = disease.strip()
                if plant not in diseases_by_plant:
                    diseases_by_plant[plant] = []
                diseases_by_plant[plant].append(disease)
        return diseases_by_plant
    
    def get_diseases_for_plant(self, plant_name):
        """Get all diseases for a specific plant"""
        plant_lower = plant_name.lower()
        diseases = []
        for idx, row in self.table.iterrows():
            disease_name = row['disease_name']
            if plant_lower in disease_name.lower():
                diseases.append(disease_name)
        return diseases
    
    def suggest_similar_diseases(self, query, top_n=5):
        """Suggest similar diseases based on query"""
        suggestions = []
        for idx, row in self.table.iterrows():
            disease_name = row['disease_name']
            score = self.similarity(query.lower(), disease_name.lower())
            suggestions.append((disease_name, score))
        
        # Sort by score and return top N
        suggestions.sort(key=lambda x: x[1], reverse=True)
        return [disease for disease, score in suggestions[:top_n] if score > 0.1]
    
    def find_best_match(self, query, column_name):
        """Find the best matching row based on query similarity"""
        query_lower = query.lower()
        best_match = None
        best_score = 0
        
        for idx, row in self.table.iterrows():
            value = str(row[column_name]).lower()
            # Calculate similarity score
            score = self.similarity(query_lower, value)
            
            # Also check if query words are in the value
            query_words = query_lower.split()
            word_matches = sum(1 for word in query_words if word in value)
            word_score = word_matches / len(query_words) if query_words else 0
            
            # Combined score
            combined_score = (score * 0.6) + (word_score * 0.4)
            
            if combined_score > best_score:
                best_score = combined_score
                best_match = idx
        
        return best_match, best_score
    
    def extract_disease_info(self, query):
        """Extract disease information from query"""
        # Keywords for different types of queries
        description_keywords = ['what is', 'tell me about', 'describe', 'information about', 'info about']
        treatment_keywords = ['how to treat', 'treatment', 'cure', 'prevent', 'prevention', 'steps', 'control', 'manage']
        supplement_keywords = ['supplement', 'fertilizer', 'product', 'buy', 'purchase', 'recommendation', 'recommend']
        
        query_lower = query.lower()
        
        # Check if asking about diseases for a specific plant
        plants = ['tomato', 'apple', 'grape', 'corn', 'potato', 'pepper', 'peach', 'cherry', 'strawberry', 
                  'blueberry', 'orange', 'raspberry', 'soybean', 'squash']
        
        for plant in plants:
            if plant in query_lower and ('disease' in query_lower or 'all' in query_lower or 'list' in query_lower):
                diseases = self.get_diseases_for_plant(plant)
                if diseases:
                    disease_list = '\n• '.join(diseases)
                    return f"Here are all the {plant.title()} diseases in my database:\n\n• {disease_list}\n\nYou can ask me about any of these for more details!"
        
        # Find the best matching disease
        disease_idx, disease_score = self.find_best_match(query, 'disease_name')
        
        if disease_score < 0.3:  # If no good match found
            suggestions = self.suggest_similar_diseases(query, top_n=5)
            suggestion_text = '\n• '.join(suggestions) if suggestions else 'Apple Scab, Tomato Early Blight, Grape Black Rot'
            return f"I'm sorry, I couldn't find information about that disease. \n\nDid you mean one of these?\n• {suggestion_text}\n\nOr type 'list all diseases' to see all available diseases."
        
        disease_row = self.table.iloc[disease_idx]
        disease_name = disease_row['disease_name']
        
        # Determine what type of information to return
        if any(keyword in query_lower for keyword in supplement_keywords):
            supplement = disease_row['supplement_name']
            buy_link = disease_row['buy_link']
            return f"💊 Supplement Recommendation for {disease_name}:\n\n{supplement}\n\n🛒 Purchase Link:\n{buy_link}"
        
        elif any(keyword in query_lower for keyword in treatment_keywords):
            steps = disease_row['Possible Steps']
            return f"🌿 Treatment for {disease_name}:\n\n{steps}"
        
        elif any(keyword in query_lower for keyword in description_keywords):
            description = disease_row['description']
            return f"📋 {disease_name}:\n\n{description}"
        
        else:
            # Return comprehensive information
            description = disease_row['description']
            steps = disease_row['Possible Steps']
            supplement = disease_row['supplement_name']
            return f"📋 {disease_name}\n\n📖 Description:\n{description}\n\n🌿 Treatment:\n{steps}\n\n💊 Recommended Supplement:\n{supplement}"
    
    def answer_query(self, query):
        if self.table is None:
            raise ValueError("Table data not loaded. Call load_table() first.")
        
        if not query or query.strip() == '':
            return "Please ask me something! I can help you with plant diseases, treatments, and supplements."
        
        # Handle greetings
        if self.is_greeting(query):
            return "Hello! 👋 I'm your plant disease assistant. I can help you with:\n\n• Information about plant diseases\n• Treatment and prevention methods\n• Supplement recommendations\n• List diseases by plant (e.g., 'tomato diseases')\n\nFeel free to ask me anything about plant health!\n\nTry asking: 'What are tomato diseases?' or 'How to treat apple scab?'"
        
        # Handle help requests
        if self.is_help(query):
            return "🌱 Here's what I can help you with:\n\n1️⃣ Get disease information: 'What is tomato early blight?'\n2️⃣ Treatment advice: 'How to treat grape black rot?'\n3️⃣ Supplement recommendations: 'Supplement for potato late blight'\n4️⃣ List diseases: 'Show all tomato diseases'\n5️⃣ List all diseases: 'List all diseases'\n\nJust ask naturally and I'll understand!"
        
        # Handle list all diseases
        if self.is_list_request(query):
            diseases_by_plant = self.get_all_diseases()
            result = "🌿 All Available Diseases by Plant:\n\n"
            for plant, diseases in sorted(diseases_by_plant.items()):
                result += f"\n{plant.upper()}:\n"
                for disease in diseases:
                    result += f"  • {disease}\n"
            result += "\n💡 Ask me about any disease for detailed information!"
            return result
        
        # Handle thanks
        if self.is_thanks(query):
            return "You're welcome! Feel free to ask if you have any more questions about plant diseases or treatments. Happy gardening! 🌱"
        
        # Handle disease/supplement queries
        return self.extract_disease_info(query)

if __name__ == "__main__":
    tqa_instance = TableQuestionAnswering()
    tqa_instance.load_table('Model/DiseaseChatbotData.csv')
    query = 'how to prevent apple scab disease'
    answer = tqa_instance.answer_query(query)
    print(answer)
