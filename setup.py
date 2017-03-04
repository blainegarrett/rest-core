from setuptools import setup, find_packages


setup(
    name='rest-core',
    version='0.0.1',
    description='Simple Rest framework',
    url='https://github.com/blainegarrett/rest-core',
    author='Blaine Garrett',
    author_email='blaine@blainegarrett.com',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7'
    ],
    keywords='rest microservice',
    packages=find_packages(),
    install_requires=[],
)