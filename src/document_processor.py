"""
Document processing utilities for parsing various documentation formats.
"""

import os
import json
import yaml
from typing import List, Dict, Any, Optional
from pathlib import Path
import logging
from urllib.parse import urljoin, urlparse

# Import processing libraries
import markdown
from bs4 import BeautifulSoup
import PyPDF2
import requests
from openapi_parser import parse

from .config import settings

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Handles parsing and processing of various document formats."""
    
    def __init__(self):
        self.supported_formats = {
            '.md': self._process_markdown,
            '.markdown': self._process_markdown,
            '.html': self._process_html,
            '.htm': self._process_html,
            '.pdf': self._process_pdf,
            '.txt': self._process_text,
            '.json': self._process_json,
            '.yaml': self._process_yaml,
            '.yml': self._process_yaml
        }
    
    def process_file(self, file_path: str) -> Dict[str, Any]:
        """
        Process a single file and extract structured content.
        
        Args:
            file_path: Path to the file to process
            
        Returns:
            Dict containing extracted content and metadata
        """
        try:
            path = Path(file_path)
            if not path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            
            extension = path.suffix.lower()
            if extension not in self.supported_formats:
                logger.warning(f"Unsupported file format: {extension}")
                return self._create_result(file_path, "", f"Unsupported format: {extension}")
            
            processor = self.supported_formats[extension]
            content = processor(file_path)
            
            return self._create_result(file_path, content, "success")
            
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {str(e)}")
            return self._create_result(file_path, "", f"Error: {str(e)}")
    
    def process_directory(self, directory_path: str) -> List[Dict[str, Any]]:
        """
        Process all supported files in a directory recursively.
        
        Args:
            directory_path: Path to the directory to process
            
        Returns:
            List of processed document results
        """
        results = []
        directory = Path(directory_path)
        
        if not directory.exists() or not directory.is_dir():
            logger.error(f"Directory not found or not a directory: {directory_path}")
            return results
        
        for file_path in directory.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in self.supported_formats:
                result = self.process_file(str(file_path))
                if result['content']:  # Only add files with content
                    results.append(result)
        
        return results
    
    def process_url(self, url: str) -> Dict[str, Any]:
        """
        Process a web page or API documentation URL.
        
        Args:
            url: URL to process
            
        Returns:
            Dict containing extracted content and metadata
        """
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            content_type = response.headers.get('content-type', '').lower()
            
            if 'text/html' in content_type:
                content = self._process_html_content(response.text, url)
            elif 'application/json' in content_type:
                content = self._process_json_content(response.text)
            elif any(fmt in content_type for fmt in ['yaml', 'yml']):
                content = self._process_yaml_content(response.text)
            else:
                content = response.text
            
            return self._create_result(url, content, "success", {"url": url, "content_type": content_type})
            
        except Exception as e:
            logger.error(f"Error processing URL {url}: {str(e)}")
            return self._create_result(url, "", f"Error: {str(e)}")
    
    def _process_markdown(self, file_path: str) -> str:
        """Process Markdown files."""
        with open(file_path, 'r', encoding='utf-8') as file:
            md_content = file.read()
        
        # Convert to HTML first to extract clean text
        html = markdown.markdown(md_content)
        soup = BeautifulSoup(html, 'html.parser')
        
        # Extract code blocks separately
        code_blocks = []
        for code in soup.find_all(['code', 'pre']):
            code_blocks.append(code.get_text())
            code.decompose()
        
        # Get main text
        text_content = soup.get_text()
        
        # Combine text and code blocks
        if code_blocks:
            text_content += "\n\nCode Examples:\n" + "\n".join(code_blocks)
        
        return text_content
    
    def _process_html(self, file_path: str) -> str:
        """Process HTML files."""
        with open(file_path, 'r', encoding='utf-8') as file:
            html_content = file.read()
        return self._process_html_content(html_content)
    
    def _process_html_content(self, html_content: str, base_url: str = None) -> str:
        """Process HTML content."""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Extract code blocks
        code_blocks = []
        for code in soup.find_all(['code', 'pre']):
            code_blocks.append(code.get_text())
        
        # Get main text
        text_content = soup.get_text()
        
        # Clean up whitespace
        lines = (line.strip() for line in text_content.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text_content = ' '.join(chunk for chunk in chunks if chunk)
        
        # Add code blocks
        if code_blocks:
            text_content += "\n\nCode Examples:\n" + "\n".join(code_blocks)
        
        return text_content
    
    def _process_pdf(self, file_path: str) -> str:
        """Process PDF files."""
        text_content = ""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text_content += page.extract_text() + "\n"
        except Exception as e:
            logger.error(f"Error processing PDF {file_path}: {str(e)}")
            raise
        
        return text_content
    
    def _process_text(self, file_path: str) -> str:
        """Process plain text files."""
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    
    def _process_json(self, file_path: str) -> str:
        """Process JSON files (including OpenAPI specs)."""
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        return self._process_json_content(content)
    
    def _process_json_content(self, content: str) -> str:
        """Process JSON content."""
        try:
            data = json.loads(content)
            
            # Check if it's an OpenAPI specification
            if 'openapi' in data or 'swagger' in data:
                return self._process_openapi_spec(data)
            
            # For regular JSON, create a readable format
            return json.dumps(data, indent=2)
            
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON: {str(e)}")
            return content
    
    def _process_yaml(self, file_path: str) -> str:
        """Process YAML files."""
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        return self._process_yaml_content(content)
    
    def _process_yaml_content(self, content: str) -> str:
        """Process YAML content."""
        try:
            data = yaml.safe_load(content)
            
            # Check if it's an OpenAPI specification
            if isinstance(data, dict) and ('openapi' in data or 'swagger' in data):
                return self._process_openapi_spec(data)
            
            # For regular YAML, create a readable format
            return yaml.dump(data, default_flow_style=False)
            
        except yaml.YAMLError as e:
            logger.error(f"Error parsing YAML: {str(e)}")
            return content
    
    def _process_openapi_spec(self, spec_data: Dict[str, Any]) -> str:
        """Process OpenAPI/Swagger specifications."""
        try:
            result = []
            
            # Basic info
            info = spec_data.get('info', {})
            result.append(f"API: {info.get('title', 'Unknown API')}")
            result.append(f"Version: {info.get('version', 'Unknown')}")
            if 'description' in info:
                result.append(f"Description: {info['description']}")
            
            # Servers
            servers = spec_data.get('servers', [])
            if servers:
                result.append("\nServers:")
                for server in servers:
                    result.append(f"- {server.get('url', 'Unknown URL')}")
            
            # Paths and operations
            paths = spec_data.get('paths', {})
            if paths:
                result.append("\nAPI Endpoints:")
                for path, methods in paths.items():
                    result.append(f"\nPath: {path}")
                    for method, operation in methods.items():
                        if isinstance(operation, dict):
                            summary = operation.get('summary', method.upper())
                            result.append(f"  {method.upper()}: {summary}")
                            if 'description' in operation:
                                result.append(f"    Description: {operation['description']}")
            
            # Components/Schemas
            components = spec_data.get('components', {})
            schemas = components.get('schemas', {})
            if schemas:
                result.append("\nData Models:")
                for schema_name, schema_def in schemas.items():
                    result.append(f"- {schema_name}")
                    if isinstance(schema_def, dict) and 'description' in schema_def:
                        result.append(f"  Description: {schema_def['description']}")
            
            return "\n".join(result)
            
        except Exception as e:
            logger.error(f"Error processing OpenAPI spec: {str(e)}")
            return json.dumps(spec_data, indent=2)
    
    def _create_result(self, source: str, content: str, status: str, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """Create a standardized result dictionary."""
        return {
            'source': source,
            'content': content,
            'status': status,
            'metadata': metadata or {},
            'processed_at': str(Path().absolute())
        }
