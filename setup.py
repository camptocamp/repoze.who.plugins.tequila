from setuptools import setup, find_packages

setup(name='repoze.who.plugins.tequila',
      version='0.5.1',
      author='Frederic Junod',
      author_email='frederic.junod@camptocamp.com',
      url='https://github.com/camptocamp/repoze.who.plugins.tequila',
      description='A repoze.who challenger for http://tequila.epfl.ch/',
      packages=find_packages(),
      zip_safe=False,
      install_requires=[
        'Paste',
        'webob'
      ],
      classifiers=[
        'Development Status :: 2 - Pre-Alpha',
    ]

)


