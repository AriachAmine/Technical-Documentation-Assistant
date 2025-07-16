"""
CLI interface for the Technical Documentation Assistant.
Useful for batch processing and automation.
"""

import argparse
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.document_processor import DocumentProcessor
from src.vector_database import VectorDatabase, DocumentChunker
from src.groq_client import GroqClient
from src.config import settings


def main():
    parser = argparse.ArgumentParser(description='Technical Documentation Assistant CLI')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Upload command
    upload_parser = subparsers.add_parser('upload', help='Upload and process documents')
    upload_parser.add_argument('--files', nargs='+', help='Files to process')
    upload_parser.add_argument('--directory', help='Directory to process')
    upload_parser.add_argument('--urls', nargs='+', help='URLs to process')
    
    # Query command
    query_parser = subparsers.add_parser('query', help='Query the documentation')
    query_parser.add_argument('question', help='Question to ask')
    query_parser.add_argument('--language', help='Programming language for code examples')
    query_parser.add_argument('--max-results', type=int, default=5, help='Maximum results to return')
    
    # Stats command
    subparsers.add_parser('stats', help='Show database statistics')
    
    # Reset command
    subparsers.add_parser('reset', help='Reset the database')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    if args.command == 'upload':
        upload_documents(args)
    elif args.command == 'query':
        query_documentation(args)
    elif args.command == 'stats':
        show_stats()
    elif args.command == 'reset':
        reset_database()


def upload_documents(args):
    """Upload and process documents."""
    processor = DocumentProcessor()
    vector_db = VectorDatabase()
    chunker = DocumentChunker()
    
    processed_count = 0
    total_chunks = 0
    
    # Process files
    if args.files:
        for file_path in args.files:
            if not os.path.exists(file_path):
                print(f"File not found: {file_path}")
                continue
            
            print(f"Processing file: {file_path}")
            result = processor.process_file(file_path)
            
            if result['content']:
                chunks = chunker.chunk_document(result)
                if chunks:
                    vector_db.add_documents(chunks)
                    processed_count += 1
                    total_chunks += len(chunks)
                    print(f"  Added {len(chunks)} chunks")
            else:
                print(f"  No content extracted from {file_path}")
    
    # Process directory
    if args.directory:
        if not os.path.exists(args.directory):
            print(f"Directory not found: {args.directory}")
            return
        
        print(f"Processing directory: {args.directory}")
        results = processor.process_directory(args.directory)
        
        for result in results:
            if result['content']:
                chunks = chunker.chunk_document(result)
                if chunks:
                    vector_db.add_documents(chunks)
                    processed_count += 1
                    total_chunks += len(chunks)
                    print(f"  Processed: {result['source']} ({len(chunks)} chunks)")
    
    # Process URLs
    if args.urls:
        for url in args.urls:
            print(f"Processing URL: {url}")
            result = processor.process_url(url)
            
            if result['content']:
                chunks = chunker.chunk_document(result)
                if chunks:
                    vector_db.add_documents(chunks)
                    processed_count += 1
                    total_chunks += len(chunks)
                    print(f"  Added {len(chunks)} chunks")
            else:
                print(f"  No content extracted from {url}")
    
    print(f"\nSummary: Processed {processed_count} documents with {total_chunks} total chunks")


def query_documentation(args):
    """Query the documentation."""
    vector_db = VectorDatabase()
    groq_client = GroqClient()
    
    print(f"Question: {args.question}")
    print("Searching for relevant documents...")
    
    # Search for relevant documents
    relevant_docs = vector_db.search(
        query=args.question,
        n_results=args.max_results
    )
    
    if not relevant_docs:
        print("No relevant documents found. Please upload some documentation first.")
        return
    
    print(f"Found {len(relevant_docs)} relevant documents")
    
    # Generate answer
    if args.language or "code" in args.question.lower() or "example" in args.question.lower():
        result = groq_client.generate_code_example(
            question=args.question,
            context_documents=relevant_docs,
            language=args.language
        )
        print(f"\nAnswer:\n{result['code_example']}")
    else:
        result = groq_client.generate_answer(
            question=args.question,
            context_documents=relevant_docs
        )
        print(f"\nAnswer:\n{result['answer']}")
    
    # Show sources
    if result.get('sources'):
        print(f"\nSources:")
        for source in result['sources'][:3]:
            print(f"  - {source}")
    
    print(f"\nTokens used: {result.get('tokens_used', 0)}")
    print(f"Model: {result.get('model', 'Unknown')}")


def show_stats():
    """Show database statistics."""
    vector_db = VectorDatabase()
    stats = vector_db.get_collection_stats()
    
    print("Database Statistics:")
    print(f"  Total documents: {stats.get('total_documents', 0)}")
    print(f"  Collection name: {stats.get('collection_name', 'Unknown')}")
    print(f"  Embedding model: {stats.get('embedding_model', 'Unknown')}")


def reset_database():
    """Reset the database."""
    confirm = input("Are you sure you want to reset the database? This cannot be undone. (y/N): ")
    if confirm.lower() != 'y':
        print("Reset cancelled.")
        return
    
    vector_db = VectorDatabase()
    success = vector_db.reset_database()
    
    if success:
        print("Database reset successfully.")
    else:
        print("Error resetting database.")


if __name__ == "__main__":
    main()
