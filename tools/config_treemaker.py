def get_config():
    return {
        'ignore_dirs': ['.FoxWorldRPG','python3.10','node_modules','tools', 'venv','.git', '.vscode', '__pycache__'],
        'ignore_exts': ['.log', '.tmp','.cfg', '.gitignore'],
         'ignore_files': ['tree.py','showtree.md', 'teste.py', 'treemaker.py', 'config_treemaker.py', '.gitignore'],  # Adicionado nova chave para ignorar nomes de arquivos específicos
        'icons': {
            '📟': ['Programming', ['.c', '.cpp', '.cs', '.ts', '.go', '.rb', '.php']],
            '🐍': ['Python', ['.py']],
            '☕': ['Javascript', ['.java', '.js']],
            '🌐': ['Web', ['.html', '.htm', '.xhtml', '.jhtml', '.shtml', '.asp', '.aspx', '.jsp', '.jspx']],
            '🎨': ['Styles', ['.css', '.scss', '.sass', '.less', '.styl']],
            '📝': ['Documents', ['.md', '.txt', '.rtf', '.doc', '.docx', '.odt', '.pdf', '.tex']],
            '🎥': ['Videos', ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv']],
            '🎵': ['Audio', ['.mp3', '.wav', '.wma', '.aac', '.flac', '.ogg', '.m4a', '.aiff', '.au']],
            '📄': ['Data & Sheets', ['.csv', '.xls', '.xlsx', '.ods', '.ppt', '.pptx', '.odp', '.xml']],
            '⚙️': ['Configuration', ['.ini', '.cfg', '.json', '.yml', '.yaml', '.properties']],
            '📚': ['Dev_Space', ['.code-workspace']],
            '📊': ['Charts', ['.csv', '.xls', '.xlsx', '.ods']],
            '📦': ['Compressed', ['.zip', '.rar', '.tar', '.gz', '.7z']],
            '🖥️': ['Executables', ['.exe', '.bat', '.sh']],
            '🖼️': ['Images', ['.tiff', '.bmp', '.gif', '.jpg', '.jpeg', '.png']],
            '📘': ['eBooks', ['.epub', '.mobi', '.azw']],
            '🔒': ['Security', ['.pem', '.cer', '.key']],
            '🗄️': ['Libraries', ['.db', '.mdb', '.bak', '.sql', '.sql3', '.mdf']],
            '🔵': ['Standard', ['']]
        },
        'indent_spaces': 2
    }

def get_icon_for_extension(extension):
    config = get_config()
    for icon, (description, extensions) in config['icons'].items():
        if extension in extensions:
            return icon
    return '🔵'  # Retorna o ícone padrão se a extensão não for encontrada

def get_folder_icon(directory_info, root=False):
    # Ícones específicos para tipos de pasta
    special_folders = {
        'assets': '🗺️',
        'asset': '🗺️',
        'modules': '🛠️',
        'module': '🛠️',
    }
    # Pasta raiz
    if root:
        return '🗃️'
    # Pasta com nomes específicos
    lower_name = directory_info["name"].lower()
    for key, icon in special_folders.items():
        if key in lower_name:
            return icon
    # Pasta vazia
    if not directory_info["files"]:
        return '📁'
    # Pasta com arquivos
    return '🗂️'

    """
    Lista de emojis:
    """