import pkg_resources

requirements = [
    "anyio==4.10.0",
    "argon2-cffi==25.1.0",
    "argon2-cffi-bindings==25.1.0",
    "arrow==1.3.0",
    "asttokens==3.0.0",
    "async-lru==2.0.5",
    "attrs==25.3.0",
    "audioread==3.0.1",
    "babel==2.17.0",
    "beautifulsoup4==4.13.5",
    "bleach==6.2.0",
    "certifi==2025.8.3",
    "cffi==1.17.1",
    "charset-normalizer==3.4.3",
    "colorama==0.4.6",
    "comm==0.2.3",
    "contourpy==1.3.2",
    "cycler==0.12.1",
    "debugpy==1.8.16",
    "decorator==5.2.1",
    "defusedxml==0.7.1",
    "exceptiongroup==1.3.0",
    "executing==2.2.0",
    "fastjsonschema==2.21.2",
    "ffmpeg==1.4",
    "fonttools==4.59.2",
    "fqdn==1.5.1",
    "h11==0.16.0",
    "httpcore==1.0.9",
    "httpx==0.28.1",
    "idna==3.10",
    "imageio==2.37.0",
    "imageio-ffmpeg==0.6.0",
    "ipykernel==6.30.1",
    "ipython==8.37.0",
    "ipywidgets==8.1.7",
    "isoduration==20.11.0",
    "jedi==0.19.2",
    "jinja2==3.1.6",
    "joblib==1.5.2",
    "json5==0.12.1",
    "jsonpointer==3.0.0",
    "jsonschema==4.25.1",
    "jsonschema-specifications==2025.4.1",
    "jupyter==1.1.1",
    "jupyter-client==8.6.3",
    "jupyter-console==6.6.3",
    "jupyter-core==5.8.1",
    "jupyter-events==0.12.0",
    "jupyter-lsp==2.3.0",
    "jupyter-server==2.17.0",
    "jupyter-server-terminals==0.5.3",
    "jupyterlab==4.4.6",
    "jupyterlab-pygments==0.3.0",
    "jupyterlab-server==2.27.3",
    "jupyterlab-widgets==3.0.15",
    "kiwisolver==1.4.9",
    "lark==1.2.2",
    "lazy-loader==0.4",
    "librosa==0.11.0",
    "llvmlite==0.44.0",
    "markupsafe==3.0.2",
    "matplotlib==3.10.5",
    "matplotlib-inline==0.1.7",
    "mistune==3.1.3",
    "moviepy==2.2.1",
    "msgpack==1.1.1",
    "nbclient==0.10.2",
    "nbconvert==7.16.6",
    "nbformat==5.10.4",
    "nest-asyncio==1.6.0",
    "networkx==3.4.2",
    "notebook==7.4.5",
    "notebook-shim==0.2.4",
    "numba==0.61.2",
    "numpy==2.2.6",
    "opencv-python==4.12.0.88",
    "overrides==7.7.0",
    "packaging==25.0",
    "pandas==2.3.2",
    "pandocfilters==1.5.1",
    "parso==0.8.5",
    "pillow==11.3.0",
    "platformdirs==4.4.0",
    "pooch==1.8.2",
    "proglog==0.1.12",
    "prometheus-client==0.22.1",
    "prompt-toolkit==3.0.52",
    "psutil==7.0.0",
    "pure-eval==0.2.3",
    "pycparser==2.22",
    "pygments==2.19.2",
    "pyparsing==3.2.3",
    "python-dateutil==2.9.0.post0",
    "python-dotenv==1.1.1",
    "python-json-logger==3.3.0",
    "pytz==2025.2",
    "pywin32==311",
    "pywinpty==3.0.0",
    "pyyaml==6.0.2",
    "pyzmq==27.0.2",
    "referencing==0.36.2",
    "requests==2.32.5",
    "rfc3339-validator==0.1.4",
    "rfc3986-validator==0.1.1",
    "rfc3987-syntax==1.1.0",
    "rpds-py==0.27.1",
    "scikit-image==0.25.2",
    "scikit-learn==1.7.1",
    "scipy==1.15.3",
    "send2trash==1.8.3",
    "setuptools==80.9.0",
    "six==1.17.0",
    "sniffio==1.3.1",
    "soundfile==0.13.1",
    "soupsieve==2.8",
    "soxr==0.5.0.post1",
    "stack-data==0.6.3",
    "terminado==0.18.1",
    "threadpoolctl==3.6.0",
    "tifffile==2025.5.10",
    "tinycss2==1.4.0",
    "tomli==2.2.1",
    "tornado==6.5.2",
    "tqdm==4.67.1",
    "traitlets==5.14.3",
    "types-python-dateutil==2.9.0.20250822",
    "typing-extensions==4.15.0",
    "tzdata==2025.2",
    "uri-template==1.3.0",
    "urllib3==2.5.0",
    "wcwidth==0.2.13",
    "webcolors==24.11.1",
    "webencodings==0.5.1",
    "websocket-client==1.8.0",
    "widgetsnbextension==4.0.14",
]

def check_requirements(reqs):
    installed_packages = {pkg.key: pkg.version for pkg in pkg_resources.working_set}

    print(f"{'Package':30} {'Required':15} {'Installed':15} Status")
    print("="*80)

    for req in reqs:
        try:
            req_pkg = pkg_resources.Requirement.parse(req)
            name = req_pkg.key
            required_version = str(req_pkg.specifier) if req_pkg.specifier else "Any"
        except Exception as e:
            print(f"{req:30} {'-':15} {'-':15} Error parsing")
            continue

        if name in installed_packages:
            installed_version = installed_packages[name]
            if req_pkg.specifier and installed_version not in req_pkg.specifier:
                status = "Version mismatch"
            else:
                status = "OK"
        else:
            installed_version = "-"
            status = "Missing"

        print(f"{name:30} {required_version:15} {installed_version:15} {status}")

if __name__ == "__main__":
    check_requirements(requirements)
