import os
from github import Github
from tqdm import tqdm

# Set your GitHub token here
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN', 'YOUR TOKEN HERE')

def get_readme_content(repo):
    """
    Retrieve the content of the README file.
    """
    try:
        readme = repo.get_contents("README.md")
        return readme.decoded_content.decode('utf-8')
    except:
        return "README not found."

def traverse_repo_iteratively(repo):
    """
    Traverse the repository iteratively to avoid recursion limits for large repositories.
    """
    structure = ""
    dirs_to_visit = [("", repo.get_contents(""))]
    dirs_visited = set()

    while dirs_to_visit:
        path, contents = dirs_to_visit.pop()
        dirs_visited.add(path)
        for content in tqdm(contents, desc=f"Processing {path}", leave=False):
            if content.type == "dir":
                if content.path not in dirs_visited:
                    structure += f"{path}/{content.name}/\n"
                    dirs_to_visit.append((f"{path}/{content.name}", repo.get_contents(content.path)))
            else:
                structure += f"{path}/{content.name}\n"
    return structure

def get_file_contents_iteratively(repo):
    file_contents = ""
    dirs_to_visit = [("", repo.get_contents(""))]
    dirs_visited = set()
    binary_extensions = [
        # Compiled executables and libraries
        '.exe', '.dll', '.so', '.a', '.lib', '.dylib', '.o', '.obj',
        # Compressed archives
        '.zip', '.tar', '.tar.gz', '.tgz', '.rar', '.7z', '.bz2', '.gz', '.xz', '.z', '.lz', '.lzma', '.lzo', '.rz', '.sz', '.dz',
        # Application-specific files
        '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.odt', '.ods', '.odp',
        # Media files (less common)
        '.png', '.jpg', '.jpeg', '.gif', '.mp3', '.mp4', '.wav', '.flac', '.ogg', '.avi', '.mkv', '.mov', '.webm', '.wmv', '.m4a', '.aac',
        # Virtual machine and container images
        '.iso', '.vmdk', '.qcow2', '.vdi', '.vhd', '.vhdx', '.ova', '.ovf',
        # Database files
        '.db', '.sqlite', '.mdb', '.accdb', '.frm', '.ibd', '.dbf',
        # Java-related files
        '.jar', '.class', '.war', '.ear', '.jpi',
        # Python bytecode and packages
        '.pyc', '.pyo', '.pyd', '.egg', '.whl',
        # Other potentially important extensions
        '.deb', '.rpm', '.apk', '.msi', '.dmg', '.pkg', '.bin', '.dat', '.data',
        '.dump', '.img', '.toast', '.vcd', '.crx', '.xpi',
        '.eot', '.otf', '.ttf', '.woff', '.woff2',
        '.ico', '.icns', '.cur',
        '.cab', '.dmp', '.msp', '.msm',
        '.keystore', '.jks', '.truststore', '.cer', '.crt', '.der', '.p7b', '.p7c', '.p12', '.pfx', '.pem', '.csr',
        '.key', '.pub', '.sig', '.pgp', '.gpg',
        '.nupkg', '.snupkg', '.appx', '.msix', '.msp', '.msu',
        '.deb', '.rpm', '.snap', '.flatpak', '.appimage',
        '.ko', '.sys', '.elf',
        '.swf', '.fla', '.swc',
        '.rlib', '.pdb', '.idb', '.pdb', '.dbg',
        '.sdf', '.bak', '.tmp', '.temp', '.log', '.tlog', '.ilk',
        '.bpl', '.dcu', '.dcp', '.dcpil', '.drc',
        '.aps', '.res', '.rsrc', '.rc', '.resx',
        '.prefs', '.properties', '.ini', '.cfg', '.config', '.conf',
        '.DS_Store', '.localized', '.svn', '.git', '.gitignore', '.gitkeep',
    ]

    while dirs_to_visit:
        path, contents = dirs_to_visit.pop()
        dirs_visited.add(path)
        for content in tqdm(contents, desc=f"Downloading {path}", leave=False):
            if content.type == "dir":
                if content.path not in dirs_visited:
                    dirs_to_visit.append((f"{path}/{content.name}", repo.get_contents(content.path)))
            else:
                # Check if the file extension suggests it's a binary file
                if any(content.name.endswith(ext) for ext in binary_extensions):
                    file_contents += f"File: {path}/{content.name}\nContent: Skipped binary file\n\n"
                else:
                    file_contents += f"File: {path}/{content.name}\n"
                    try:
                        if content.encoding is None or content.encoding == 'none':
                            file_contents += "Content: Skipped due to missing encoding\n\n"
                        else:
                            try:
                                decoded_content = content.decoded_content.decode('utf-8')
                                file_contents += f"Content:\n{decoded_content}\n\n"
                            except UnicodeDecodeError:
                                try:
                                    decoded_content = content.decoded_content.decode('latin-1')
                                    file_contents += f"Content (Latin-1 Decoded):\n{decoded_content}\n\n"
                                except UnicodeDecodeError:
                                    file_contents += "Content: Skipped due to unsupported encoding\n\n"
                    except (AttributeError, UnicodeDecodeError):
                        file_contents += "Content: Skipped due to decoding error or missing decoded_content\n\n"
    return file_contents

def get_repo_contents(repo_url):
    """
    Main function to get repository contents.
    """
    repo_name = repo_url.split('/')[-1]
    if not GITHUB_TOKEN:
        raise ValueError("Please set the 'GITHUB_TOKEN' environment variable or the 'GITHUB_TOKEN' in the script.")
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(repo_url.replace('https://github.com/', ''))

    print(f"Fetching README for: {repo_name}")
    readme_content = get_readme_content(repo)

    print(f"\nFetching repository structure for: {repo_name}")
    repo_structure = f"Repository Structure: {repo_name}\n"
    repo_structure += traverse_repo_iteratively(repo)

    print(f"\nFetching file contents for: {repo_name}")
    file_contents = get_file_contents_iteratively(repo)

    instructions = f"Prompt: Analyze the {repo_name} repository to understand its structure, purpose, and functionality. Follow these steps to study the codebase:\n\n"
    instructions += "1. Read the README file to gain an overview of the project, its goals, and any setup instructions.\n\n"
    instructions += "2. Examine the repository structure to understand how the files and directories are organized.\n\n"
    instructions += "3. Identify the main entry point of the application (e.g., main.py, app.py, index.js) and start analyzing the code flow from there.\n\n"
    instructions += "4. Study the dependencies and libraries used in the project to understand the external tools and frameworks being utilized.\n\n"
    instructions += "5. Analyze the core functionality of the project by examining the key modules, classes, and functions.\n\n"
    instructions += "6. Look for any configuration files (e.g., config.py, .env) to understand how the project is configured and what settings are available.\n\n"
    instructions += "7. Investigate any tests or test directories to see how the project ensures code quality and handles different scenarios.\n\n"
    instructions += "8. Review any documentation or inline comments to gather insights into the codebase and its intended behavior.\n\n"
    instructions += "9. Identify any potential areas for improvement, optimization, or further exploration based on your analysis.\n\n"
    instructions += "10. Provide a summary of your findings, including the project's purpose, key features, and any notable observations or recommendations.\n\n"
    instructions += "Use the files and contents provided below to complete this analysis:\n\n"

    return repo_name, instructions, readme_content, repo_structure, file_contents

if __name__ == '__main__':
    repo_url = input("Please enter the GitHub repository URL: ")
    try:
        repo_name, instructions, readme_content, repo_structure, file_contents = get_repo_contents(repo_url)
        output_filename = f'{repo_name}_contents.txt'
        with open(output_filename, 'w', encoding='utf-8') as f:
            f.write(instructions)
            f.write(f"README:\n{readme_content}\n\n")
            f.write(repo_structure)
            f.write('\n\n')
            f.write(file_contents)
        print(f"Repository contents saved to '{output_filename}'.")
    except ValueError as ve:
        print(f"Error: {ve}")
    except Exception as e:
        print(f"An error occurred: {e}")
        print("Please check the repository URL and try again.")