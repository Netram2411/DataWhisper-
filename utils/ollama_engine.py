"""
Ollama AI Engine - Local, Free AI
"""

import streamlit as st
from langchain_ollama import ChatOllama
from config.settings import AI_TEMPERATURE


class OllamaEngine:
    """Handles all Ollama AI interactions (FREE!)"""
    
    def __init__(self):
        """Initialize Ollama client"""
        try:
            self.llm = ChatOllama(
                model="phi3",
                temperature=AI_TEMPERATURE,
            )
        except Exception as e:
            raise ValueError(f"Ollama not running! Make sure Ollama app is open. Error: {str(e)}")
    
    def generate_pandas_code(self, user_question, schema_summary):
        """Generates pandas code to answer user's question"""
        
        system_prompt = """You are an expert Python data analyst. 
Given a dataset schema and a user question, generate ONLY the pandas code needed to answer it.

IMPORTANT RULES:
1. The DataFrame variable is called 'df'
2. Return ONLY executable Python code, no explanations
3. Store the final result in a variable called 'result'
4. For visualizations, use plotly and store figure in 'result'
5. Keep code simple and efficient

Example:
User asks: "What's the average sales?"
Your code:
result = df['Sales'].mean()
"""
        
        user_prompt = f"""
Dataset Schema:
{schema_summary}

User Question: {user_question}

Generate the pandas code to answer this question.
"""
        
        try:
            # Combine system and user prompts for Ollama
            full_prompt = f"{system_prompt}\n\n{user_prompt}"
            
            response = self.llm.invoke(full_prompt)
            code = response.content
            
            # Clean up code - remove markdown formatting
            code = code.replace("```python", "").replace("```", "").strip()
            
            return code
            
        except Exception as e:
            st.error(f"Ollama Error: {str(e)}")
            return None
    
    def explain_result(self, user_question, result):
        """Generates natural language explanation"""
        
        prompt = f"""
User asked: "{user_question}"
The analysis result is: {result}

Provide a brief, clear explanation in 2-3 sentences.
"""
        
        try:
            response = self.llm.invoke(prompt)
            return response.content
            
        except Exception as e:
            return "Analysis complete!"