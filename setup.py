from setuptools import setup, find_packages, Command
import os
import re


def read_version():
    path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'annotatee/__init__.py')
    with open(path, 'r') as fh:
        return re.search(r'__version__\s?=\s?[\'"](.+)[\'"]', fh.read()).group(1)


def readme():
    with open('README.md') as f:
        return f.read()


class CreateInitFile(Command):
    description = 'create __init__.py file in data directory'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        init_path = os.path.join('annotatee', 'data', '__init__.py')
        if not os.path.exists(init_path):
            with open(init_path, 'w') as f:
                f.write('# This file is automatically created during installation\n')
        print(f"Created {init_path}")


setup(name='annotatee',
      version=read_version(),
      description='',
      long_description=readme(),
      long_description_content_type='text/markdown',
      author='Ariane Mora',
      author_email='ariane.n.mora@gmail.com',
      url='https://github.com/ArianeMora/annotate-e',
      license='GPL3',
      project_urls={
          "Bug Tracker": "https://github.com/ArianeMora/annotate-e/issues",
          "Documentation": "https://github.com/ArianeMora/annotate-e",
          "Source Code": "https://github.com/ArianeMora/annotate-e",
      },
      classifiers=[
          'Intended Audience :: Science/Research',
          'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
          'Programming Language :: Python :: 3.8',
          'Topic :: Scientific/Engineering :: Bio-Informatics',
      ],
      cmdclass={
          'create_init': CreateInitFile,
      },
      include_package_data=True,
      package_data={
          'annotatee': ['data/CLEAN.zip', 'data/proteinfer.zip', 'data/install.sh'],
      },
      keywords=['gene-annotation', 'bioinformatics'],
      packages=['annotatee'],
      entry_points={
          'console_scripts': [
                'annotatee = annotatee.__main__:app',

          ]
      },
      install_requires=['pandas', 'numpy', 'enzymetk', 'sciutil>=1.0.3',
                        'sciviso', 'seaborn', 'typer'],
      python_requires='>=3.10',
      data_files=[("", ["LICENSE"])]
      )