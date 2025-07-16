<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# Technical Documentation Assistant - Copilot Instructions

This is a Python-based AI-driven technical documentation assistant that helps developers understand APIs, SDKs, and software products by parsing documentation and providing contextual answers with code examples.

## Project Structure
- `src/` - Main application code
  - `main.py` - FastAPI application with REST endpoints
  - `config.py` - Configuration management with Pydantic
  - `document_processor.py` - Document parsing (MD, HTML, PDF, OpenAPI, etc.)
  - `vector_database.py` - ChromaDB integration for semantic search
  - `groq_client.py` - Groq API integration for LLM capabilities
- `templates/` - Jinja2 HTML templates
- `static/` - CSS and client-side assets

## Key Technologies
- **FastAPI** - Modern web framework for building APIs
- **ChromaDB** - Vector database for semantic search
- **Groq API** - LLM for natural language processing
- **Sentence Transformers** - For creating embeddings
- **Beautiful Soup, PyPDF2** - Document parsing
- **Tailwind CSS** - Frontend styling

## Coding Guidelines
1. Use async/await patterns for FastAPI endpoints
2. Include comprehensive error handling and logging
3. Follow Pydantic models for request/response validation
4. Use environment variables for configuration
5. Include type hints for all functions
6. Write docstrings for all classes and methods
7. Handle file uploads securely
8. Implement proper cleanup for temporary files

## API Endpoints
- `POST /api/query` - Query documentation with natural language
- `POST /api/upload` - Upload files and URLs for processing
- `POST /api/upload-directory` - Process entire directories
- `GET /api/stats` - Get database statistics
- `DELETE /api/reset` - Reset the knowledge base

## Environment Setup
- Copy `.env.example` to `.env` and configure Groq API key
- Install dependencies with `pip install -r requirements.txt`
- Run with `uvicorn src.main:app --reload`

When working on this project:
- Prioritize code quality and error handling
- Consider chunking strategies for large documents
- Optimize vector search performance
- Ensure responsive web interface
- Follow RESTful API design principles
