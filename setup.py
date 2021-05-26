from setuptools import setup, find_packages

VERSION = '0.0.1' 
DESCRIPTION = 'Control the pumps'
LONG_DESCRIPTION = 'Python code to control the New Era pumps through a serial port'

# Setting up
setup(
       # the name must match the folder name 'verysimplemodule'
        name="Pumps", 
        version=VERSION,
        author="Svilen Kolev and Erel LEveine",
        author_email="<kolev.s@northeastern.edu>",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        packages=find_packages(),
        install_requires=[], # add any additional packages that 
        # needs to be installed along with your package. Eg: 'caer'
        
        keywords=['python', 'pump', 'New Era'],
        classifiers= [
            "Intended Audience :: Education",
            "Programming Language :: Python :: 3",
            "Operating System :: MacOS :: MacOS X",
            "Operating System :: Microsoft :: Windows",
        ]
)