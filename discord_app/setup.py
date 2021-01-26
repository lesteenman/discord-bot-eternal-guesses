from setuptools import setup, find_packages

setup(
    name='eternal_guesses',
    version='0.1.0',
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    url='https://github.com/lesteenman/discord-bot-eternal-guesses',
    license='',
    author='lesteenman',
    author_email='',
    description='',
    setup_requires=['lambda_setuptools'],
    install_requires=[
        'discord-interactions',
        'discord.py',
        'aioboto3',
    ],
)
