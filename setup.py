from setuptools import setup, find_packages

setup(name='repoze.who.plugins.tequila',
      version='0.1',
      author='Frederic Junod',
      author_email='frederic.junod@camptocamp.com',
      packages=find_packages(),
      zip_safe=False,
      install_requires=[
        'webob'
      ],
)


