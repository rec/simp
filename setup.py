__version__ = '2.0.0'

_classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Topic :: Software Development :: Libraries',
    'Topic :: Utilities',
]

if __name__ == '__main__':
    from setuptools import setup

    with open('requirements.txt') as f:
        REQUIRED = f.read().splitlines()

    setup(
        name='simp',
        version=__version__,
        author='Tom Ritchford',
        author_email='tom@swirly.com',
        url='https://github.com/rec/simp',
        tests_require=['pytest'],
        py_modules=['simp'],
        description='Sort imports simply',
        long_description=open('README.rst').read(),
        license='MIT',
        classifiers=_classifiers,
        keywords=['documentation'],
        scripts=['simp'],
        install_requires=REQUIRED,
    )
