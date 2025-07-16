"""
Groq API integration for natural language processing and code generation.
"""

import logging
from typing import List, Dict, Any, Optional
from groq import Groq

from .config import settings

logger = logging.getLogger(__name__)


class GroqClient:
    """Handles interactions with the Groq API for LLM capabilities."""
    
    def __init__(self):
        self.client = Groq(api_key=settings.groq_api_key)
        self.model = settings.groq_model
        self.temperature = settings.temperature
        self.max_tokens = settings.max_completion_tokens
    
    def generate_answer(self, question: str, context_documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate an answer to a question based on provided context documents.
        
        Args:
            question: User's question
            context_documents: Relevant documents from vector search
            
        Returns:
            Dict containing the answer and metadata
        """
        try:
            # Prepare context from documents
            context = self._prepare_context(context_documents)
            
            # Create system prompt
            system_prompt = self._create_system_prompt()
            
            # Create user prompt with context and question
            user_prompt = self._create_user_prompt(question, context)
            
            # Generate response
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            answer = response.choices[0].message.content
            
            return {
                "answer": answer,
                "sources": [doc.get('metadata', {}).get('source', 'Unknown') for doc in context_documents],
                "confidence": self._calculate_confidence(context_documents),
                "tokens_used": response.usage.total_tokens if hasattr(response, 'usage') else 0,
                "model": self.model
            }
            
        except Exception as e:
            logger.error(f"Error generating answer: {str(e)}")
            return {
                "answer": f"I apologize, but I encountered an error while processing your question: {str(e)}",
                "sources": [],
                "confidence": 0.0,
                "tokens_used": 0,
                "model": self.model
            }
    
    def generate_code_example(self, question: str, context_documents: List[Dict[str, Any]], 
                            language: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a code example based on the question and context.
        
        Args:
            question: User's question requesting code
            context_documents: Relevant documents from vector search
            language: Optional programming language specification
            
        Returns:
            Dict containing code example and explanation
        """
        try:
            context = self._prepare_context(context_documents)
            
            system_prompt = self._create_code_system_prompt(language)
            user_prompt = self._create_code_user_prompt(question, context, language)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,  # Lower temperature for code generation
                max_tokens=self.max_tokens
            )
            
            answer = response.choices[0].message.content
            
            return {
                "code_example": answer,
                "sources": [doc.get('metadata', {}).get('source', 'Unknown') for doc in context_documents],
                "language": language,
                "tokens_used": response.usage.total_tokens if hasattr(response, 'usage') else 0,
                "model": self.model
            }
            
        except Exception as e:
            logger.error(f"Error generating code example: {str(e)}")
            return {
                "code_example": f"// Error generating code example: {str(e)}",
                "sources": [],
                "language": language,
                "tokens_used": 0,
                "model": self.model
            }
    
    def summarize_documents(self, documents: List[Dict[str, Any]]) -> str:
        """
        Create a summary of multiple documents.
        
        Args:
            documents: List of documents to summarize
            
        Returns:
            Summary text
        """
        try:
            if not documents:
                return "No documents provided for summary."
            
            # Combine document contents
            combined_content = "\n\n".join([
                f"Document: {doc.get('metadata', {}).get('source', 'Unknown')}\n{doc.get('content', '')}"
                for doc in documents[:5]  # Limit to first 5 documents
            ])
            
            system_prompt = """You are a technical documentation summarizer. 
            Create concise, informative summaries that highlight key concepts, 
            APIs, and important technical details."""
            
            user_prompt = f"Please provide a comprehensive summary of the following technical documentation:\n\n{combined_content}"
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error summarizing documents: {str(e)}")
            return f"Error creating summary: {str(e)}"
    
    def _prepare_context(self, documents: List[Dict[str, Any]]) -> str:
        """Prepare context text from documents."""
        if not documents:
            return "No relevant documentation found."
        
        context_parts = []
        for i, doc in enumerate(documents[:5], 1):  # Limit to top 5 documents
            content = doc.get('content', '')
            source = doc.get('metadata', {}).get('source', 'Unknown')
            
            context_parts.append(f"[Document {i} - {source}]\n{content}")
        
        return "\n\n".join(context_parts)
    
    def _create_system_prompt(self) -> str:
        """Create the system prompt for general Q&A."""
        return """You are a Technical Documentation Assistant, an expert AI that helps developers understand APIs, SDKs, and software products by analyzing their documentation.

Your capabilities:
- Analyze technical documentation and provide accurate, contextual answers
- Generate relevant code examples when appropriate
- Explain complex technical concepts clearly
- Reference specific parts of the documentation when answering

Guidelines:
1. Base your answers strictly on the provided documentation context
2. If information is not available in the context, clearly state this limitation
3. Provide specific, actionable answers with code examples when relevant
4. Include references to the source documents when possible
5. If asked about code, provide functional, well-commented examples
6. Explain technical concepts in a clear, developer-friendly manner

Always prioritize accuracy and cite your sources from the provided documentation."""
    
    def _create_user_prompt(self, question: str, context: str) -> str:
        """Create user prompt with question and context."""
        return f"""Based on the following technical documentation, please answer this question:

Question: {question}

Documentation Context:
{context}

Please provide a comprehensive answer based on the documentation provided. If you include code examples, make sure they are functional and well-commented."""
    
    def _create_code_system_prompt(self, language: Optional[str] = None) -> str:
        """Create system prompt for code generation."""
        lang_instruction = f" in {language}" if language else ""
        
        return f"""You are a Technical Documentation Assistant specialized in generating code examples{lang_instruction}.

Your responsibilities:
1. Generate functional, well-commented code examples based on documentation
2. Ensure code follows best practices and conventions
3. Include error handling where appropriate
4. Provide clear explanations of what the code does
5. Reference the relevant documentation sections

Guidelines for code generation:
- Write production-ready code that actually works
- Include necessary imports and dependencies
- Add comments explaining key concepts
- Follow language-specific conventions and best practices
- Provide complete, runnable examples when possible"""
    
    def _create_code_user_prompt(self, question: str, context: str, language: Optional[str] = None) -> str:
        """Create user prompt for code generation."""
        lang_instruction = f" in {language}" if language else ""
        
        return f"""Based on the following technical documentation, please generate a code example{lang_instruction} that demonstrates:

Request: {question}

Documentation Context:
{context}

Please provide:
1. A complete, functional code example
2. Clear comments explaining each step
3. Any necessary setup or dependencies
4. A brief explanation of how the code works

Make sure the code is production-ready and follows best practices."""
    
    def _calculate_confidence(self, documents: List[Dict[str, Any]]) -> float:
        """Calculate confidence score based on document relevance."""
        if not documents:
            return 0.0
        
        # Average the similarity scores
        scores = [doc.get('score', 0.0) for doc in documents]
        return sum(scores) / len(scores) if scores else 0.0
