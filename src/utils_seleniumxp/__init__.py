# Selenium webdriver utilities - XP version
# provide harmonized Python bindings for Selenium webdriver and functional enrichments

# utility functions for Python Selenium webdriver partially inspired by:
# - https://github.com/defactto/selenium-utils/tree/master/selenium_utils
# - https://github.com/jmakov/selenium-utils/
# - https://github.com/horejsek/python-webdriverwrapper
# - https://github.com/cryzed/Selenium-Requests/blob/master/seleniumrequests/request.py
# - https://github.com/mfalesni/selenium-smart-locator
# - https://github.com/bigSAS/selenium-actions
# for hiding automation f. e. for Yahoo logon in addition to stealth package:
# - https://stackoverflow.com/questions/53039551/selenium-webdriver-modifying-navigator-webdriver-flag-to-prevent-selenium-detec


"""
Package with utilities and functional extensions for Selenium webdriver Python language bindings


The package consist of various helpers and extensions to the Selenium webdriver:

- module for session handling especially a custom factory function to initialize a webdriver object
- module with additional methods for the webdriver class
- module with convenience functions for locators
- module with additional methods for the webelement class
- an extended event-firing webdriver and an extended listener abstract base class
- a sample event listener implementation based on the extended abstract base class

Different from other packages extending the Selenium webdriver class does not work with
wrapping the original webdriver but providing a mixin class or alternatively directly setting
additional methods via 'setattr' in the original webdriver class. This is done and controlled
via a pretty versatile custom factory function initializing the webdriver. The custom factory
function offers a mechanism to browser-type specific initializations and settings with examples
provided for enabling a direct download, disabling browser notifications or optimized scraping.

The webelement extension are done via setattr only. Implementing a mixin class would require
to modify webdriver methods to return the new class with the mixin. So benefit of the
settattr approach is that extending the webelement class is independend from changes to the
webdriver class.

The package also provides an extended event-firing webdriver class.

This approach makes this package a full drop-in replacement for the original selenium driver.
Beside the factory function to create the webdriver there is no change in the API.
"""


# ruff and mypy per file settings
#
# empty lines
# ruff: noqa: E302, E303
# naming conventions
# ruff: noqa: N801, N802, N803, N806, N812, N813, N815, N816, N818, N999
#
# disable mypy errors
# mypy: disable-error-code = "no-redef"

# fmt: off



# version determination

# original Hatchlor version
# from importlib.metadata import PackageNotFoundError, version
# try:
#     __version__ = version('{{ cookiecutter.project_slug }}')
# except PackageNotFoundError:  # pragma: no cover
#     __version__ = 'unknown'
# finally:
#     del version, PackageNotFoundError

# latest import requirement for hatch-vcs-footgun-example
from utils_seleniumxp.version import __version__


# import Python bindings for Selenium webdriver
# - list of imports deducted from various examples in documentation
# - module intended to reduce namespace pollution by importing in separate namespace
#   and improve transparency by using a common prefix for all Selenium related
#   identifiers
#   package: import <selenium.xxx> as <SeleniumBinding short name>
#   use: from UtilsSeleniumXP import <SeleniumBinding short name>

from selenium import webdriver as WebDriver
from selenium.webdriver.remote.webdriver import WebDriver as _RemoteWebDriver
from selenium.webdriver.remote.webelement import WebElement as _WebElement
from selenium.webdriver.remote.shadowroot import ShadowRoot as _ShadowRoot
from selenium.webdriver.remote.switch_to import SwitchTo as _SwitchTo
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.abstract_event_listener import AbstractEventListener
from selenium.webdriver.support.event_firing_webdriver import EventFiringWebDriver
from selenium.webdriver.support.event_firing_webdriver import EventFiringWebElement
from selenium.webdriver.support.color import Color

import selenium.common.exceptions as WebDriverExceptions
import selenium.webdriver.support.expected_conditions as ExpectedConditions



# exception class
class ErrorUtilsSelenium(BaseException):
    pass



# general mixin control (package global parameter)
# switch mixin method of additional functionality - MixIn class vs. direct setattr or callables
mixinactive = False

import sys
import os.path

# switch os.path -> pathlib
sys.path.insert(1, os.path.dirname(os.path.realpath(__file__)))
# sys.path.insert(1, str(pathlib.Path(__file__).resolve().parent))

# import utils_seleniumxp.sessionhandling
from utils_seleniumxp.sessionhandling import initWebDriver, init_webdriver
from utils_seleniumxp.sessionhandling import connectChrome, connect_chrome
from utils_seleniumxp.sessionhandling import checkDebugport, check_debugport
# direct import of other package modules or objects from these package modules to avoid circular imports
from utils_seleniumxp.locatorutils import SeleniumLocator as SeleniumLocator
from utils_seleniumxp.locatorutils import SeleniumLocatorXPATH as SeleniumLocatorXPATH
from utils_seleniumxp.locatorutils import SeleniumLocatorCSS as SeleniumLocatorCSS
from utils_seleniumxp.locatorutils import parameterizedSeleniumLocator as parameterizedSeleniumLocator
from utils_seleniumxp.locatorutils import  parselSelectorExtension as  parselSelectorExtension
import utils_seleniumxp.webdriver_addon as WebdriverAddOn
import utils_seleniumxp.webelement_addon as WebelementAddOn
import utils_seleniumxp.eventfiring_addon as EventFiringAddon
from utils_seleniumxp.eventlistener import SimpleEventListener
