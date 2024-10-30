from setuptools import setup

setup(
    version="1.0.0",
    name="dcm-metadata-mapper",
    description="metadata mapper interface and classes for dcm",
    author="LZV.nrw",
    install_requires=[
        "xmltodict==0.*",
        "dcm-common>=3.0.0,<4.0.0",
    ],
    packages=[
        "dcm_metadata_mapper",
        "dcm_metadata_converter",
        "lzvnrw_mapper",
        "lzvnrw_converter"
    ],
    setuptools_git_versioning={
        "enabled": True,
        "version_file": "VERSION",
        "count_commits_from_version_file": True,
        "dev_template": "{tag}.dev{ccount}",
    },
)
