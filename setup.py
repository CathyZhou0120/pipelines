from setuptools import setup, find_packages

data = dict(
    name="/",
    packages=find_packages(),
)

if __name__ == '__main__':
    setup(**data)
