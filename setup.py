from setuptools import setup, find_packages

setup(
    name="meraki_webhook_service",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "meraki_acr_framework==0.1.0"
    ],
)
