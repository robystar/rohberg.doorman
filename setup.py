from setuptools import setup, find_packages
import os

version = '0.1'

setup(name='rohberg.doorman',
      version=version,
      description="Password: Set strength and duration.",
      long_description=open("README.rst").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='',
      author='Katja Suess',
      author_email='k.suess@rohberg.ch',
      url='http://github.com/ksuess',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['rohberg'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'Plone',
          'Products.PlonePAS',
      ],
      extras_require={
          'test': ['plone.app.testing',]
      },
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
