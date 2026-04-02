"""
Groq AI Engine - Free Cloud Compatible Version
"""

import streamlit as st
from config.settings import AI_TEMPERATURE
from groq import Groq


class GroqEngine:
    """Handles all Groq AI interactions (FREE + CLOUD READY)"""

    def __init__(self):
        """Initialize Groq client"""
        try:
            self.client = Groq(api_key=st.secrets["GROQ_API_KEY"])
            self.model = "llama3-8b-8192"
        except Exception as e:
            raise ValueError(f"Groq API Error: {str(e)}")

    def _ask_groq(self, prompt):
        """Internal helper to send a prompt to Groq"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                temperature=AI_TEMPERATURE,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.choices[0].message.content   # ✅ FIX
        except Exception as e:
            st.error(f"Groq Error: {str(e)}")
            return None

    def generate_pandas_code(self, user_question, schema_summary):
        """Generates pandas code to answer user's question"""

        system_prompt = """You are an expert Python data analyst. 
Given a dataset schema and a user question, generate ONLY the pandas code needed to answer it.

RULES:
1. The DataFrame variable is 'df'
2. Return ONLY Python code — no explanation
3. Store final answer in 'result'
4. For charts, use plotly and store figure in 'result'
5. Keep code efficient and clean
"""

        user_prompt = f"""
Dataset Schema:
{schema_summary}

User Question: {user_question}

Generate the pandas code ONLY.
"""

        full_prompt = f"{system_prompt}\n\n{user_prompt}"

        code = self._ask_groq(full_prompt)

        if not code:
            return None

        # Clean code from unwanted markdown formatting
        code = code.replace("```python", "").replace("```", "").strip()
        return code

    def explain_result(self, user_question, result):
        """Generates natural language explanation"""

        prompt = f"""
User asked: "{user_question}"
Result obtained: {result}

Explain the result clearly in 2–3 sentences.
"""

        return self._ask_groq(prompt)
