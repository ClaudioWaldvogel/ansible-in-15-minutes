from setuptools import setup, find_packages

setup(
    name='ansible-in-15-minutes',
    python_requires='>3.5.2',
    version='0.1',
    description='Ansible in 15 minutes Demo',
    author='NovaTec Consulting GmbH',
    author_email='',
    url='',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'ansible',
        'boto3',
        'boto'
    ]
)
