from setuptools import setup

setup(
    name='HiveMind-cli',
    version='0.4',
    packages=['cli_satellite'],
    url='https://github.com/OpenJarbas/HiveMind-cli',
    license='MIT',
    author='jarbasAI',
    author_email='jarbasai@mailfence.com',
    description='Mycroft Remote Cli',
    entry_points={
        'console_scripts': [
            'HiveMind-cli=cli_satellite.__main__:main'
        ]
    }
)
