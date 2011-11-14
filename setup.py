from setuptools import setup, find_packages

requires = ['setuptools', 'jinja2', 'lazy']

setup(
    name='serverzen_fabric',
    version='0.1',
    url='http://www.serverzen.com',
    author='Rocky Burt',
    author_email='rocky@serverzen.com',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=True,
    install_requires=requires,
    tests_require=requires + ['applib'],
    test_suite='serverzen_fabric',
    entry_points={
        'serverzen_fabric_os': [
            'ubuntu = serverzen_fabric.ubuntu:UbuntuSupport',
            ]
        },
    )
