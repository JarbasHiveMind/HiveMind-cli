from setuptools import setup

setup(
    name='HiveMind-cli',
    version='0.5.0a1',
    packages=['hivemind_cli_terminal'],
    url='https://github.com/OpenJarbas/HiveMind-cli',
    license='MIT',
    author='jarbasAI',
    author_email='jarbasai@mailfence.com',
    description='Mycroft Remote Cli',
    install_requires=["hivemind_bus_client~=0.0.3a2",
                      "HiveMind_presence~=0.0.2a1"],
    entry_points={
        'console_scripts': [
            'HiveMind-cli=cli_satellite.__main__:main'
        ]
    }
)
