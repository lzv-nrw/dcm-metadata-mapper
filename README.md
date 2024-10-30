# dcm-metadata-mapper
This package provides converter and mapper functions for the project [lzv.nrw](https://lzv.nrw/).

## Setup
Install this package and its (required) dependencies by issuing `pip install .`

## Package-Structure
```
dcm-metadata-mapper/                 
├── dcm-metadata-converter/          
│   ├── __init__.py                  
│   └── converter_interface.py       # This module contains an interface for the definition
│                                    # of a metadata-to-dict conversion class.
├── dcm-metadata-mapper/             
│   ├── __init__.py                  
│   ├── mapper_interface.py          # This module contains an interface for the definition
│   │                                # of a metadata-mapping.
│   ├── mapper_factory.py            # This module inherits from the mapper_interface and
│   │                                # defines a function factory to dynamically
│   │                                # create mapper-classes.
│   └── test_mapper_factory.py       # Test suite for the mapper factory
│
├── lzvnrw_converter/                
│   ├── __init__.py                  
│   ├── oaipmh_converter.py          # This module contains implementation of the source
│   │                                # metadata-to-dict converter based on the ConverterInterface.
│   └── test_oaipmh.py               # Test suite for the OAI-PMH-specific implementation
│                                    # of the source metadata converter
├── lzvnrw_mapper/                   
│   ├── __init__.py                  
│   ├── hbz_opus.py                  # This module contains implementations of the mapper classes
│   │   ...                          # for several repositories based on the mapper factory.
│   ├── miami.py                     
│   ├── test_hbz_opus.py             # Test suites for the specific implementations
│   │   ...                          # of the source metadata mapper
│   └── test_miami.py                
├── README.md/                       
└── ...

```

# Contributors
* Sven Haubold
* Orestis Kazasidis
* Stephan Lenartz
* Kayhan Ogan
* Michael Rahier
* Steffen Richters-Finger
* Malte Windrath
