# libcloud-dnsimple-v2-driver

This is temporary repository for our DNSSimple APIv2 driver for Apache Libcloud library.
It's inspired by other 3rd party libcloud drivers and the code is based on the old
DNSSimple API implementation in current version of libcloud.

Right now the master branch contains our custom connection class which uses requests
module instead of internal connection handler in libcloud. It's nasty hack and you
should check *compatible_with_libcloud* branch where the code closer to libcloud is.
It uses libcloud's internal connection classes and the tests are based on their
own mocking technique.

The reason for this was we needed support for SNI - DNSimple APIv2 requires it -
and we are still on custom version of libcloud 1.0 where SNI is not supported.
New version of libcloud doesn't have this issue and you should use the other branch.

## Quick start

Installation:

    pip install git+https://github.com/niteoweb/libcloud@niteoweb_internal_release
    pip install git+https://github.com/niteoweb/libcloud-dnsimple-v2-driver@master

The driver doesn't require anything special and you can use this like this:

    from libcloud_dnsimple_v2_driver import DNSimpleV2DNSDriver
    
    # Uncomment this line if you want to test it with their sandbox env
    # DNSimpleV2DNSDriver.host = "api.sandbox.dnsimple.com"
    
    driver = DNSimpleV2DNSDriver("AUTH_ID", "API_KEY")
    zones = driver.list_zones()
    print(driver.list_records(zones[0]))

## How to test

You can test the code like this:

    pip install pipenv
    pipenv shell
    make test

The code coverage report is generated into htmlcov/ directory. Just open *index.html* to see it.
