from distutils.core import setup

setup(
    name="libcloud-dnsimple-v2-driver",
    author="Adam Štrauch",
    author_email="as@niteo.co",
    url="https://github.com/niteoweb/libcloud-dnsimple-v2-driver",
    version="0.6-759b70a67cd2a743a891394b920cc4898a2913ae",
    packages=["libcloud_dnsimple_v2_driver",],
    license="Apache License 2.0",
    long_description=open("README.md").read(),
    install_requires=[
        "apache-libcloud==1.0.0-rc2-ef038d17092c0b6e99e9ac9870cbada1dcd5c782",
    ],
)
