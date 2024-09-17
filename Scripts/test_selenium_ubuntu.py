from selenium import webdriver
from selenium.webdriver.common.by import By
import os
# https://github.com/SeleniumHQ/selenium/issues/11414
# ...
install_dir = "/snap/firefox/current/usr/lib/firefox"
driver_loc = os.path.join(install_dir, "geckodriver")
binary_loc = os.path.join(install_dir, "firefox")

service = webdriver.FirefoxService(driver_loc)
opts = webdriver.FirefoxOptions()
opts.binary_location = binary_loc
driver = webdriver.Firefox(service=service, options=opts)
driver.get("https://google.com")


# opts = webdriver.FirefoxOptions()
# serv = webdriver.FirefoxService( executable_path='/snap/bin/geckodriver' )

# TODO - set some more options

# ffox_driver = webdriver.Firefox( options=opts)
# ffox_driver = webdriver.Firefox( options=opts, service=serv )
# ffox_driver.get("google.ca")