"""
code_chunker.py

Advanced code chunking for Elixir using AST-aware parsing.
Better than naive sliding window - preserves semantic meaning.

Features:
- Preserves module boundaries
- Keeps functions intact
- Includes relevant context (module docs, type specs)
- Overlaps intelligently at semantic boundaries
"""

from pathlib import Path
from typing import List, Dict
import re


class ElixirCodeChunker:
    """
    Chunks Elixir code intelligently:
    - Preserves module boundaries
    - Keeps functions intact
    - Includes relevant context (module docs, type specs)
    - Overlaps intelligently at semantic boundaries
    """
    
    def __init__(self, max_chunk_size: int = 1000, overlap: int = 200):
        self.max_chunk_size = max_chunk_size
        self.overlap = overlap
    
    def extract_modules(self, code: str) -> List[Dict]:
        """Extract all modules from Elixir file"""
        modules = []
        
        # Pattern to find defmodule blocks
        module_pattern = r'defmodule\s+([A-Z][A-Za-z0-9_.]*)\s+do(.*?)(?=\ndefmodule|\Z)'
        
        matches = re.finditer(module_pattern, code, re.DOTALL)
        
        for match in matches:
            module_name = match.group(1)
            module_content = match.group(2)
            
            modules.append({
                'name': module_name,
                'content': match.group(0),
                'start': match.start(),
                'end': match.end()
            })
        
        return modules
    
    def extract_functions(self, module_content: str) -> List[Dict]:
        """Extract functions from module"""
        functions = []
        
        # Patterns for different function types
        patterns = [
            r'(def\s+\w+[^)]*\).*?(?=\n\s*def|\n\s*defp|\n\s*end|\Z))',
            r'(defp\s+\w+[^)]*\).*?(?=\n\s*def|\n\s*defp|\n\s*end|\Z))',
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, module_content, re.DOTALL)
            for match in matches:
                functions.append({
                    'content': match.group(0),
                    'start': match.start(),
                    'end': match.end()
                })
        
        return functions
    
    def chunk_file(self, file_path: str, repo_name: str = "") -> List[Dict]:
        """
        Main chunking method - creates semantic chunks from Elixir file
        """
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            code = f.read()
        
        chunks = []
        
        # Extract file-level docs
        file_docs = self._extract_moduledoc(code)
        
        # Extract modules
        modules = self.extract_modules(code)
        
        if not modules:
            # No modules found, chunk by lines with overlap
            return self._chunk_by_lines(code, file_path, repo_name)
        
        for module in modules:
            module_name = module['name']
            module_content = module['content']
            
            # Get module documentation
            module_doc = self._extract_moduledoc(module_content)
            
            # Extract functions from module
            functions = self.extract_functions(module_content)
            
            # Strategy: Create chunks that include:
            # 1. Module context (name + doc)
            # 2. Related functions grouped together
            # 3. Overlap between chunks for context
            
            if len(module_content) <= self.max_chunk_size:
                # Small module - one chunk
                chunks.append({
                    'text': module_content,
                    'module': module_name,
                    'file': file_path,
                    'repo': repo_name,
                    'type': 'module',
                    'metadata': {
                        'has_docs': bool(module_doc),
                        'function_count': len(functions)
                    }
                })
            else:
                # Large module - chunk by functions with module context
                module_header = self._get_module_header(module_content)
                
                current_chunk = module_header
                current_functions = []
                
                for func in functions:
                    func_content = func['content']
                    
                    # Check if adding this function exceeds chunk size
                    if len(current_chunk) + len(func_content) > self.max_chunk_size:
                        # Save current chunk
                        if current_functions:
                            chunks.append({
                                'text': current_chunk,
                                'module': module_name,
                                'file': file_path,
                                'repo': repo_name,
                                'type': 'module_section',
                                'functions': current_functions,
                                'metadata': {
                                    'has_docs': bool(module_doc),
                                    'function_count': len(current_functions)
                                }
                            })
                        
                        # Start new chunk with module header + overlap
                        current_chunk = module_header
                        # Add last function from previous chunk for context
                        if current_functions:
                            last_func = current_functions[-1]
                            current_chunk += f"\n\n  # ... (previous function: {last_func})\n\n"
                        
                        current_functions = []
                    
                    current_chunk += "\n\n" + func_content
                    func_name = self._extract_function_name(func_content)
                    if func_name:
                        current_functions.append(func_name)
                
                # Add remaining chunk
                if current_functions:
                    chunks.append({
                        'text': current_chunk,
                        'module': module_name,
                        'file': file_path,
                        'repo': repo_name,
                        'type': 'module_section',
                        'functions': current_functions,
                        'metadata': {
                            'has_docs': bool(module_doc),
                            'function_count': len(current_functions)
                        }
                    })
        
        return chunks
    
    def _extract_moduledoc(self, content: str) -> str:
        """Extract @moduledoc"""
        match = re.search(r'@moduledoc\s+"""(.*?)"""', content, re.DOTALL)
        return match.group(1).strip() if match else ""
    
    def _get_module_header(self, module_content: str) -> str:
        """Get module definition + docs + use/import/alias"""
        lines = module_content.split('\n')
        header_lines = []
        
        in_header = True
        for line in lines:
            if in_header:
                header_lines.append(line)
                # Stop at first def/defp
                if re.match(r'\s*(def|defp)\s+', line):
                    in_header = False
                    break
        
        return '\n'.join(header_lines[:50])  # Max 50 lines for header
    
    def _extract_function_name(self, func_content: str) -> str:
        """Extract function name from def/defp"""
        match = re.match(r'\s*(?:def|defp)\s+(\w+)', func_content)
        return match.group(1) if match else None
    
    def _chunk_by_lines(self, code: str, file_path: str, repo_name: str) -> List[Dict]:
        """Fallback: chunk by lines with overlap"""
        lines = code.split('\n')
        chunks = []
        
        step = self.max_chunk_size - self.overlap
        
        for i in range(0, len(lines), step):
            chunk_lines = lines[i:i + self.max_chunk_size]
            chunk_text = '\n'.join(chunk_lines)
            
            if chunk_text.strip():
                chunks.append({
                    'text': chunk_text,
                    'file': file_path,
                    'repo': repo_name,
                    'type': 'text_chunk',
                    'line_start': i,
                    'line_end': min(i + self.max_chunk_size, len(lines))
                })
        
        return chunks


def chunk_repository(repo_path: str, repo_name: str = None) -> List[Dict]:
    """
    Chunk entire repository
    
    Args:
        repo_path: Path to repository
        repo_name: Name of repository (optional, will use directory name)
    
    Returns:
        List of code chunks with metadata
    """
    if repo_name is None:
        repo_name = Path(repo_path).name
    
    chunker = ElixirCodeChunker(max_chunk_size=1000, overlap=200)
    all_chunks = []
    
    # Find all Elixir files
    elixir_files = list(Path(repo_path).rglob('*.ex')) + list(Path(repo_path).rglob('*.exs'))
    
    # Skip test files for now (optional - comment out if you want tests)
    elixir_files = [f for f in elixir_files if '/test/' not in str(f)]
    
    print(f"Found {len(elixir_files)} Elixir files in {repo_name}")
    
    for file_path in elixir_files:
        try:
            chunks = chunker.chunk_file(str(file_path), repo_name)
            all_chunks.extend(chunks)
        except Exception as e:
            print(f"Error chunking {file_path}: {e}")
            continue
    
    print(f"Created {len(all_chunks)} chunks from {repo_name}")
    return all_chunks
