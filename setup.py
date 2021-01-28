from distutils.core import setup
setup(
  name = 'fitutils',         # How you named your package folder (MyLib)
  packages = ['fitutils'],   # Chose the same as "name"
  version = '0.2.2',      # Start with a small number and increase it with every change you make
  license='BSD-3-Clause License',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  description = 'Utility function and classes for fitting',   # Give a short description about your library
  author = 'Marc-Antoine Verdier',
  author_email = 'marc-antoine.verdier@u-paris.fr',
  url = 'https://https://github.com/M-A-Verdier/Fitutils',
  download_url = 'https://github.com/M-A-Verdier/Fitutils/archive/v_0.2.2.tar.gz',
  keywords = ['LeastSquare', 'ErrorBars', 'Fitting'],
  install_requires=[
          'numpy',
          'scipy',
          'matplotlib'
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: BSD 3-Clause "New" or "Revised" License (BSD-3-Clause)',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
  ],
)
