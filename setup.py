import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="buildor",
    version="0.1.0",
    author="Jones Maxime Murphy III",
    author_email="jones.murphy@onsight.ga",
description="Civilization simulation/RPG",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords='game rpg simulation civilization magic city builder onsight tech repair',
    url="onsight.ga",
    packages=setuptools.find_packages(),
    license=None,
    classifiers=[
        "Programming Language :: Python :: 3",
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        "License :: OSI Approved :: MIT License",
    ],
    python_requires='>=3.7',
    install_requires=[
        "names",
        "numpy",
        "pygame",
        "sqlalchemy"
    ],
    entry_points={
        'console_scripts': [
            'buildor=buildor.__main__:main'
        ]
    },
    include_package_data=True
)