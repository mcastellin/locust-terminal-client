import setuptools

setuptools.setup(
    name="locust-terminal-client",
    version="0.0.1",
    py_modules=["lcli"],
    packages=setuptools.find_packages(include=["lcli"]),
    install_requires=[
        "click",
        "plotille",
        "requests",
        "BeautifulSoup4",
    ],
    entry_points={
        "console_scripts": [
            "lcli = lcli.main:cli",
        ],
    },
)
