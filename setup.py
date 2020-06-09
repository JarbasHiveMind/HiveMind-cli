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
    install_requires=["jarbas_hive_mind>=0.10.1"],
    entry_points={
        'console_scripts': [
            'HiveMind-cli=cli_satellite.__main__:main'
        ]
    }
)
