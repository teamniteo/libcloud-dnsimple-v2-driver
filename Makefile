test:
	rm -rf htmlcov
	cd libcloud_dnsimple_v2_driver && pytest --cov=. --cov-report html
	mv libcloud_dnsimple_v2_driver/htmlcov .