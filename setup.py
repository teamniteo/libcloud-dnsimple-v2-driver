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
        "apache-libcloud @ git+https://github.com/niteoweb/libcloud.git@niteoweb_internal_release",
    ],
)
