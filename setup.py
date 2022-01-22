import setuptools

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

description = "A wrapper over MavSDK to control a UAV through a high-level interface."

setuptools.setup(
    name="Moonlander",
    version="0.1.1",
    author="Jane Lewis",
    author_email="lewijack@oregonstate.edu",
    description=description,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/OSURoboticsClub/Moonlander",
    project_urls= {
        "Issues": "https://github.com/OSURoboticsClub/Moonlander/issues"
    },
    packages=['moonlander'],
    install_requires=['mavsdk'],
)