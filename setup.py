import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="CHAMPBattleBox",
    version="0.0.1",
    author="Somebody",
    author_email="info@champmakerspace.org",
    description="This is the Raspberry Pi 4, and Arduino interface for our battlebox.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bbartman/CHAMP_Battlebox",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)