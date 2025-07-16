# Technical Documentation Assistant 🤖📚

An intelligent AI-driven system that parses technical documentation and provides contextual answers to developer questions with relevant code examples. Built for freelance portfolio demonstration, showcasing practical AI application in technical processes.

![Technical Documentation Assistant](https://img.shields.io/badge/AI-Documentation%20Assistant-blue)
![Python](https://img.shields.io/badge/Python-3.8+-green)
![FastAPI](https://img.shields.io/badge/FastAPI-Modern%20API-red)
![Groq](https://img.shields.io/badge/Groq-LLM%20API-purple)

## 🚀 Features

### Core Functionality
- **Multi-Format Document Processing**: Supports Markdown, HTML, PDF, OpenAPI/Swagger, JSON, YAML
- **Intelligent Chunking**: Smart document segmentation for optimal retrieval
- **Semantic Search**: Vector-based search using ChromaDB and sentence transformers
- **Natural Language Querying**: Ask questions in plain English
- **Contextual Code Generation**: Generates functional code examples in multiple languages
- **Real-time Web Interface**: Modern, responsive UI built with Tailwind CSS

### Supported Document Types
- 📄 **Markdown** (.md, .markdown) - Documentation files
- 🌐 **HTML** (.html, .htm) - Web-based documentation
- 📋 **PDF** (.pdf) - Technical manuals and guides
- 📝 **Text** (.txt) - Plain text documentation
- 🔧 **API Specifications** (.json, .yaml, .yml) - OpenAPI/Swagger files
- 🌍 **Web URLs** - Live documentation websites

### Programming Languages Supported
- Python, JavaScript, TypeScript, Java, C#, Go, Rust, PHP, Ruby, and more

## 🛠 Technology Stack

- **Backend**: FastAPI (Python)
- **LLM**: Groq API (llama-3.3-70b-versatile)
- **Vector Database**: ChromaDB
- **Embeddings**: Sentence Transformers (all-MiniLM-L6-v2)
- **Document Processing**: BeautifulSoup, PyPDF2, OpenAPI Parser
- **Frontend**: HTML5, Tailwind CSS, Vanilla JavaScript
- **Configuration**: Pydantic Settings

## 📋 Prerequisites

- Python 3.8 or higher
- Groq API key (free from [console.groq.com](https://console.groq.com/keys))

## ⚡ Quick Start

### 1. Clone and Setup
```bash
# Navigate to project directory
cd "Technical Documentation Assistant"

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration
```bash
# Copy environment template
copy .env.example .env  # Windows
# cp .env.example .env  # Linux/Mac

# Edit .env file and add your Groq API key
GROQ_API_KEY=your_groq_api_key_here
```

### 3. Run the Application
```bash
# Start the server
python -m uvicorn src.main:app --reload

# Or run directly
cd src
python main.py
```

### 4. Access the Interface
Open your browser and navigate to: `http://localhost:8000`

## 📖 Usage Guide

### Upload Documentation
1. **File Upload**: Select multiple files (MD, HTML, PDF, etc.)
2. **URL Processing**: Enter documentation URLs, one per line
3. **Directory Processing**: Specify a local directory path to process all supported files

### Query the System
1. Type your question in natural language
2. Optionally select a programming language for code examples
3. Get contextual answers with relevant code snippets

### Example Queries
- "How do I authenticate with this API?"
- "Show me a Python example of creating a user"
- "What are the available endpoints in this API?"
- "How do I handle errors in JavaScript?"

## 🏗 Project Structure

```
Technical Documentation Assistant/
├── src/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── config.py              # Configuration management
│   ├── document_processor.py   # Document parsing logic
│   ├── vector_database.py     # ChromaDB integration
│   └── groq_client.py         # Groq API client
├── templates/
│   └── index.html             # Web interface
├── static/
│   └── style.css              # Custom styles
├── requirements.txt           # Python dependencies
├── .env.example              # Environment template
├── .gitignore                # Git ignore rules
└── README.md                 # This file
```

## 🔧 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Web interface |
| `POST` | `/api/query` | Query documentation |
| `POST` | `/api/upload` | Upload files/URLs |
| `POST` | `/api/upload-directory` | Process directory |
| `GET` | `/api/stats` | Database statistics |
| `GET` | `/api/search` | Search documents |
| `DELETE` | `/api/reset` | Reset database |
| `GET` | `/health` | Health check |

## 🧪 Example API Usage

### Query Documentation
```bash
curl -X POST "http://localhost:8000/api/query" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "How do I authenticate with the API?",
    "language": "python",
    "max_results": 5
  }'
```

### Upload Files
```bash
curl -X POST "http://localhost:8000/api/upload" \
  -F "files=@documentation.md" \
  -F "urls=https://api.example.com/docs"
```

## ⚙️ Configuration Options

Key settings in `.env`:

```env
# Groq API
GROQ_API_KEY=your_key_here
GROQ_MODEL=llama-3.3-70b-versatile
TEMPERATURE=0.1

# Processing
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
MAX_TOKENS=4000

# Database
CHROMA_PERSIST_DIRECTORY=./chroma_db
EMBEDDING_MODEL=all-MiniLM-L6-v2
```

## 🎯 Key Benefits for Clients

### For Development Teams
- **Faster Onboarding**: New developers can quickly understand complex APIs
- **Reduced Documentation Debt**: Makes existing docs more accessible
- **Improved Developer Experience**: Natural language interface to technical content

### For Product Managers
- **Better Documentation ROI**: Makes documentation more valuable and usable
- **Reduced Support Tickets**: Self-service answers to common questions
- **Faster Feature Adoption**: Easier discovery of API capabilities

## 🚀 Deployment Options

### Local Development
```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

### Production Deployment
- Deploy with Docker, Heroku, or cloud platforms
- Configure production environment variables
- Use production-grade ASGI server (uvicorn with workers)

## 🔒 Security Considerations

- API keys stored in environment variables
- File upload validation and sanitization
- Temporary file cleanup
- CORS configuration for production
- Input validation with Pydantic

## 📊 Performance Optimization

- **Chunking Strategy**: Optimized for semantic coherence
- **Vector Search**: Efficient similarity search with ChromaDB
- **Caching**: Persistent vector database storage
- **Async Processing**: Non-blocking file uploads and processing

## 🐛 Troubleshooting

### Common Issues

1. **"Module not found" errors**
   ```bash
   pip install -r requirements.txt
   ```

2. **Groq API errors**
   - Verify API key in `.env` file
   - Check API key validity at console.groq.com

3. **ChromaDB issues**
   - Delete `chroma_db/` directory to reset
   - Ensure sufficient disk space

4. **File processing errors**
   - Check file permissions
   - Verify supported file formats

## 🤝 Contributing

This is a portfolio project, but suggestions are welcome:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🎓 Portfolio Notes

This project demonstrates:

- **AI Integration**: Practical LLM application with Groq API
- **Full-Stack Development**: FastAPI backend + modern frontend
- **Document Processing**: Multi-format parsing and chunking
- **Vector Databases**: Semantic search implementation
- **API Design**: RESTful endpoints with proper validation
- **User Experience**: Intuitive web interface
- **Production Readiness**: Error handling, logging, configuration

Perfect for showcasing AI-driven automation capabilities to potential clients requiring intelligent solutions for technical processes.

---

**Built with ❤️ for demonstrating practical AI applications in technical documentation workflows.**
