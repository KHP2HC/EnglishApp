import os
import json
import ast

def get_node_type(filename):
    ext = os.path.splitext(filename)[1].lower()
    if filename in ['Dockerfile', 'docker-compose.yml']: return 'service'
    if filename in ['README.md', 'issue-mapping.md']: return 'document'
    if filename in ['requirements.txt', '.dockerignore']: return 'config'
    if ext in ['.py']: return 'file'
    if ext in ['.json', '.db', '.txt']: return 'data'
    return 'file'

def get_module_path(filepath):
    # e.g., 'core/ai_tutor.py' -> 'core.ai_tutor'
    if filepath.endswith('.py'):
        filepath = filepath[:-3]
    return filepath.replace(os.sep, '.')

file_nodes = []
import_edges = []
all_edges = []
root_dir = '.'
ignore_dirs = ['.git', '__pycache__', 'venv', 'env']

file_map = {}

# Discover files
for dirpath, dirnames, filenames in os.walk(root_dir):
    dirnames[:] = [d for d in dirnames if d not in ignore_dirs]
    for f in filenames:
        if f.endswith('.pyc') or f.endswith('.log') or f.endswith('.yaml'): continue
        if f == 'wordhoard_error.yaml': continue
        full_path = os.path.relpath(os.path.join(dirpath, f), root_dir)
        full_path = full_path.replace('\\', '/')
        node_type = get_node_type(f)
        node_id = f"{node_type}:{full_path}"
        
        node = {
            "id": node_id,
            "type": node_type,
            "name": f,
            "filePath": full_path,
            "summary": "...",
            "tags": []
        }
        file_nodes.append(node)
        
        if full_path.endswith('.py'):
            module_name = full_path[:-3].replace('/', '.')
            file_map[module_name] = node_id
            if full_path.endswith('__init__.py'):
                pkg_name = full_path[:-12].replace('/', '.')
                if pkg_name:
                    file_map[pkg_name] = node_id

# Find imports
for node in file_nodes:
    if node['type'] == 'file' and node['filePath'].endswith('.py'):
        try:
            with open(node['filePath'], 'r', encoding='utf-8') as f:
                content = f.read()
            tree = ast.parse(content)
            for stmt in tree.body:
                imports = []
                if isinstance(stmt, ast.Import):
                    for alias in stmt.names:
                        imports.append(alias.name)
                elif isinstance(stmt, ast.ImportFrom):
                    if stmt.module:
                        module = stmt.module
                        if stmt.level > 0:
                            parts = node['filePath'].split('/')[:-1]
                            for _ in range(stmt.level - 1):
                                if parts: parts.pop()
                            base = '.'.join(parts)
                            if base:
                                module = f"{base}.{module}"
                            else:
                                module = module
                        imports.append(module)
                        for alias in stmt.names:
                            imports.append(f"{module}.{alias.name}")
                
                for imp in imports:
                    target_id = None
                    if imp in file_map:
                        target_id = file_map[imp]
                    else:
                        # Try partial match
                        for k, v in file_map.items():
                            if imp.startswith(k):
                                target_id = v
                                break
                    if target_id:
                        edge = {
                            "source": node['id'],
                            "target": target_id,
                            "type": "imports"
                        }
                        import_edges.append(edge)
                        all_edges.append(edge)
        except Exception as e:
            pass

data = {
    "fileNodes": file_nodes,
    "importEdges": import_edges,
    "allEdges": all_edges
}

with open('.understand-anything/tmp/ua-arch-input.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2)
