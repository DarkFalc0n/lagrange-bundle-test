import PyInstaller.__main__
import os
import shutil
import platform

def build_bundle():
    # Clean previous builds
    if os.path.exists('dist'):
        shutil.rmtree('dist')
    if os.path.exists('build'):
        shutil.rmtree('build')

    # Determine platform-specific options
    if platform.system().lower() == 'windows':
        python_path = '--add-data=python/python.exe;python'
    else:
    # For Linux, we don't need to include Python explicitly
        python_path = ''

    options = [
        'launcher.py',
        '--name=YourApp',
        '--onefile',
        '--windowed',
        '--add-data=backend/server.py:backend',
        '--add-data=frontend/build/linux/x64/release/bundle/frontend:frontend/build/linux/x64/release/bundle',
        '--hidden-import=flask',
        '--hidden-import=flask_cors',
        '--collect-all=werkzeug',
    ]

    # Add platform-specific options
    if python_path:
        options.append(python_path)

    # Create spec file for PyInstaller
    PyInstaller.__main__.run(options)

if __name__ == "__main__":
    build_bundle()