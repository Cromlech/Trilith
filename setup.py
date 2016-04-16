1# -*- coding: utf-8 -*-

from os.path import join
from setuptools import setup, find_packages

name = 'Trilith'
version = '0.1'
readme = open('README.txt').read()
history = open(join('docs', 'HISTORY.txt')).read()


install_requires = [
    'webob',
    'mysql-python',
    'cromlech.sqlalchemy',
    ]

tests_require = [
    ]

setup(name=name,
      version=version,
      description=("Trilith: Oauth2 automated ticket machine"),
      long_description=readme + '\n\n' + history,
      keywords='Trilith Oauth2',
      author='Souheil Chelfouh',
      author_email='sch@treegital.fr',
      url='http://www.treegital.fr/',
      license='Proprietary',
      package_dir={'': 'src'},
      packages=find_packages('src', exclude=['ez_setup']),
      namespace_packages=[],
      include_package_data=True,
      zip_safe=False,
      tests_require=tests_require,
      install_requires=install_requires,
      extras_require={'test': tests_require},
      classifiers=[
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          ],
      entry_points="""
      # -*- Entry points: -*-
      [paste.app_factory]
      app = Trilith.wsgi:Application
      """,
      )
