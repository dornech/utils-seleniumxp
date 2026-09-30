# Selenium webdriver utilities - XP version
# webdriver class - additional functionalities
# implementation via mixin class or monkey-patching alternatively

"""
module with webdriver class extensions

Webdriver extensions include:
- speed-up for finding elements using parsel
- access to shadow dom (with translation of xpath to css)
- helper closing pop-ups
- wait functions
"""


# ruff and mypy per file settings
#
# empty lines
# ruff: noqa: E302, E303
# naming conventions
# ruff: noqa: N801, N802, N803, N806, N812, N813, N815, N816, N818, N999
# boolean-type arguments
# ruff: noqa: FBT001, FBT002
# others
# ruff: noqa: B010, E301, E305, E501, F403, F405, PLR0904, PLR0914, PLR0917, PLR1702, PLR5501, PLW0717, RUF075, RUF105, S101, SIM102, TID252
#
# disable mypy errors
# mypy: disable-error-code = "no-any-return, attr-defined, unused-ignore"

# fmt: off



# TODO Dev:
# - smartwait module -> implement in webdriver_addon
# - restructure module for better maintainability (clearer structure, shorter module(s)
#   - Mixin-class related stuff remains in webdriver_addon.py
#   - webdriver subdirectory and submoduls for wait support, closepopup, element helpers / shadowDOM
#   - from <module> import *
#   - pilot with wait_helper
# - find_element_frames -> loop across frames automatically?
# - integrate new Selenium 4.x API functions
#   - scroll from Actions-API (instead of script calling)
#     see https://www.selenium.dev/documentation/webdriver/actions_api/wheel/

# TODO Test:
# - n. a.



from typing import cast, TypeVar
# from collections.abc import Callable, Generator
from collections.abc import Generator

import contextlib

# import time
import fnmatch  # alternative: simplematch

# import collections

# import cssify
from seleniumrequests.request import RequestsSessionMixin as _RequestsSessionMixin

import utils_seleniumxp

from .webdriver_addons.close_popups import *
from .webdriver_addons.shadow_dom import *
from .webdriver_addons.windowopen_logger import *



# block direct calling
# __all__ = []



# webdriver mixins approach - require Mixin classes to be used for additional functionality
# mixin-class required per browser specific webdriver class
# optional: monkey-patching by setattr (assumption: derived wrapper classes should automatically inherit methods)

# mixin object for normal webdriver
class _WebDriverMixin:
    """
    _WebDriverMixin - mixin class with extensions
    """

    # call __init__ of base class to avoid it is ignored due to mixin MRO
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    # mixin for get_user_agent
    def get_user_agent(self) -> str:
        assert isinstance(self, utils_seleniumxp._RemoteWebDriver)
        return get_user_agent(self)

    # mixin for is_present / is_element_present

    def is_present(self, by: utils_seleniumxp.By, value: str, use_parsel: bool = True) -> bool:
        assert isinstance(self, utils_seleniumxp._RemoteWebDriver)
        return is_present(self, by, value, use_parsel)

    def is_element_present(self, by: utils_seleniumxp.By, value: str, use_parsel: bool = True) -> bool:
        assert isinstance(self, utils_seleniumxp._RemoteWebDriver)
        return is_present(self, by, value, use_parsel)

    # mixin for find_elements_optimized
    def find_elements_optimized(
        self, by: utils_seleniumxp.By, value: str, use_parsel: bool = True
    ) -> list[utils_seleniumxp._WebElement]:
        assert isinstance(self, utils_seleniumxp._RemoteWebDriver)
        return find_elements_optimized(self, by, value, use_parsel)

    # mixin for find_shadowroot, find_elements_shadowdom and find_element_shadowdom

    def find_root_shadowdom_simple(self, by: utils_seleniumxp.By, value: str) ->  utils_seleniumxp._ShadowRoot | None:
        assert isinstance(self, utils_seleniumxp._RemoteWebDriver)
        return find_root_shadowdom_simple(self, by, value)

    def find_root_shadowdom(self, locator_list: utils_seleniumxp.SeleniumLocator | list[utils_seleniumxp.SeleniumLocator]) ->  utils_seleniumxp._ShadowRoot | None:
        assert isinstance(self, utils_seleniumxp._RemoteWebDriver)
        return find_root_shadowdom(self, locator_list)

    def find_elements_shadowdom_simple(
        self, by: utils_seleniumxp.By, value: str, shadowroot: utils_seleniumxp._ShadowRoot | utils_seleniumxp._WebElement
    ) -> list[utils_seleniumxp._WebElement] | None:
        assert isinstance(self, utils_seleniumxp._RemoteWebDriver)
        return find_elements_shadowdom_simple(self, by, value, shadowroot)

    def find_elements_shadowdom(
        self, locator_list: utils_seleniumxp.SeleniumLocator | list[utils_seleniumxp.SeleniumLocator], shadowroot: utils_seleniumxp._ShadowRoot | utils_seleniumxp._WebElement | None = None
    ) -> list[utils_seleniumxp._WebElement] | None:
        assert isinstance(self, utils_seleniumxp._RemoteWebDriver)
        return find_elements_shadowdom(self, locator_list, shadowroot)

    def find_element_shadowdom_simple(
        self, by: utils_seleniumxp.By, value: str, shadowroot: utils_seleniumxp._ShadowRoot | utils_seleniumxp._WebElement
    ) -> utils_seleniumxp._WebElement | None:
        assert isinstance(self, utils_seleniumxp._RemoteWebDriver)
        return find_element_shadowdom_simple(self, by, value, shadowroot)

    def find_element_shadowdom(
        self, locator_list: utils_seleniumxp.SeleniumLocator | list[utils_seleniumxp.SeleniumLocator], shadowroot: utils_seleniumxp._ShadowRoot | utils_seleniumxp._WebElement | None = None
    ) -> utils_seleniumxp._WebElement | None:
        assert isinstance(self, utils_seleniumxp._RemoteWebDriver)
        return find_element_shadowdom(self, locator_list, shadowroot)

    # mixin for is_present_shadowdom / is_element_present_shadowdom

    def is_present_shadowdom(
        self, locator_list: utils_seleniumxp.SeleniumLocator | list[utils_seleniumxp.SeleniumLocator], shadowroot: utils_seleniumxp._ShadowRoot | utils_seleniumxp._WebElement | None = None
    ) -> bool:
        assert isinstance(self, utils_seleniumxp._RemoteWebDriver)
        return is_present_shadowdom(self, locator_list, shadowroot)

    def is_element_present_shadowdom(
        self, locator_list: utils_seleniumxp.SeleniumLocator | list[utils_seleniumxp.SeleniumLocator], shadowroot: utils_seleniumxp._ShadowRoot | utils_seleniumxp._WebElement | None = None
    ) -> bool:
        assert isinstance(self, utils_seleniumxp._RemoteWebDriver)
        return is_present_shadowdom(self, locator_list, shadowroot)

    # mixin for hover over element
    def hover_over_element(
        self, by: utils_seleniumxp.By, value: str, by_host: utils_seleniumxp.By | None = None, value_host: str | None = None
    ) -> None:
        assert isinstance(self, utils_seleniumxp._RemoteWebDriver)
        hover_over_element(self, by, value, by_host, value_host)

    # mixin for handle_alert
    def handle_alert(self, alerttext: str, accept: bool = False) -> bool:
        assert isinstance(self, utils_seleniumxp._RemoteWebDriver)
        return handle_alert(self, alerttext, accept)

    # mixin for closepopup routines

    def closepopup(
        self,
        locator_click: utils_seleniumxp.SeleniumLocator,
        wait_click: float,
        check_click: bool = False,
        locator_iframe: utils_seleniumxp.SeleniumLocator | None = None,
        wait_iframe: float = 1,
        locator_shadowdomhost: utils_seleniumxp.SeleniumLocator | list[utils_seleniumxp.SeleniumLocator] | None = None
    ) -> bool:
        assert isinstance(self, utils_seleniumxp._RemoteWebDriver)
        return closepopup(self, locator_click, wait_click, check_click, locator_iframe, wait_iframe, locator_shadowdomhost)

    def closepopup_queueadd(
        self,
        locator_click: utils_seleniumxp.SeleniumLocator,
        wait_click: float,
        check_click: bool = False,
        locator_iframe: utils_seleniumxp.SeleniumLocator | None = None,
        wait_iframe: float = 1,
        locator_shadowdomhost: utils_seleniumxp.SeleniumLocator | list[utils_seleniumxp.SeleniumLocator] | None = None
    ) -> None:
        assert isinstance(self, utils_seleniumxp._RemoteWebDriver)
        closepopup_queueadd(self, locator_click, wait_click, check_click, locator_iframe, wait_iframe, locator_shadowdomhost)

    def closepopup_queueprocessing(self, firstonly: bool = True) -> bool:
        assert isinstance(self, utils_seleniumxp._RemoteWebDriver)
        return closepopup_queueprocessing(self, firstonly)

    # mixin for closewindows
    def closewindows(self, keepwindows: list) -> None:
        assert isinstance(self, utils_seleniumxp._RemoteWebDriver)
        closewindows(self, keepwindows)

    # mixin for window.open logger

    def window_open_logger(self) -> None:
        assert isinstance(self, utils_seleniumxp._RemoteWebDriver)
        return window_open_logger(self)

    def enable_wol(self) -> bool:
        assert isinstance(self, utils_seleniumxp._RemoteWebDriver)
        return enable_wol(self)

    def disable_wol(self) -> bool:
        assert isinstance(self, utils_seleniumxp._RemoteWebDriver)
        return disable_wol(self)

    def clear_wol(self) -> bool:
        assert isinstance(self, utils_seleniumxp._RemoteWebDriver)
        return clear_wol(self)

    def last_logentry_wol(self) -> dict:
        assert isinstance(self, utils_seleniumxp._RemoteWebDriver)
        return last_logentry_wol(self)

    def log_wol(self) -> list[dict]:
        assert isinstance(self, utils_seleniumxp._RemoteWebDriver)
        return log_wol(self)

    def status_wol(self) -> dict:
        assert isinstance(self, utils_seleniumxp._RemoteWebDriver)
        return status_wol(self)

    # mixin for wait4AJAX and wait4HTMLstable

    def wait4AJAX(self, timeout: int = 15, min_wait: float = 0.0) -> bool:
        assert isinstance(self, utils_seleniumxp._RemoteWebDriver)
        return wait4AJAX(self, timeout, min_wait)

    def wait4HTMLstable(self, wait: float = 0.1, max_wait: float = 0.5) -> bool:
        assert isinstance(self, utils_seleniumxp._RemoteWebDriver)
        return wait4HTMLstable(self, wait, max_wait)

    # extended wait for page load - source from ObeytheTestingGoat
    def wait_for_page_load(self, timeout=10) -> contextlib.AbstractContextManager:
        assert isinstance(self, utils_seleniumxp._RemoteWebDriver)
        return wait_for_page_load(self, timeout)


# TypeVar for custom classes to help MyPy
T = TypeVar("T", bound="utils_seleniumxp._RemoteWebDriver")

# mixin overlay for 3rd party extensions always mixed in
def WebDriverMixedinOnly3rdParty(cls_webdriver: type[T]) -> type[T]:
    """
    WebDriverMixedinOnly3rdParty - factory function for custom class with fixed 3rd party mixins

    The factory function mechanism is required to use alternative base classes like
    undetected_chromedriver.

    Args:
        cls_webdriver (type[utils_seleniumxp._RemoteWebDriver]): base class

    Returns:
        type[utils_seleniumxp._RemoteWebDriver]: custom webdriver class with mixin
    """

    class WebDriverClassCustom(_RequestsSessionMixin, cls_webdriver):  # type: ignore[valid-type, misc]
        pass

    return cast(type[T], WebDriverClassCustom)

# own mixin overlay
def WebDriverMixedin(cls_webdriver: type[T]) -> type[T]:
    """
    WebDriverMixedin - factory function for custom class with fixed 3rd party mixins and own mixin

    The factory function mechanism is required to use alternative base classes like
    undetected_chromedriver.

    Args:
        cls_webdriver (type[utils_seleniumxp._RemoteWebDriver]): base class

    Returns:
        type[utils_seleniumxp._RemoteWebDriver]: custom webdriver class with mixin
    """

    class WebDriverClassCustom(_WebDriverMixin, _RequestsSessionMixin, cls_webdriver):  # type: ignore[valid-type, misc]
        pass

    return cast(type[T], WebDriverClassCustom)

# mixin class for eventfiring webdriver
class EventFiringWebDriverExtendedMixedin(utils_seleniumxp.eventfiring_addon.EventFiringWebDriverExtended):  # docsig: disable
    """
    EventFiringWebDriverExtendedMixedin - mixin class for eventfiring webdriver
    """

    # mixin for closepopup routines

    def closepopup(
        self,
        locator_click: utils_seleniumxp.SeleniumLocator,
        wait_click: float,
        check_click: bool = False,
        locator_iframe: utils_seleniumxp.SeleniumLocator | None = None,
        wait_iframe: float = 1,
        locator_shadowdomhost: utils_seleniumxp.SeleniumLocator | list[utils_seleniumxp.SeleniumLocator] | None = None
    ) -> bool:
        return closepopup_eventfiring(self, locator_click, wait_click, check_click, locator_iframe, wait_iframe, locator_shadowdomhost)

    def closepopup_queueadd(
        self, locator_click:
        utils_seleniumxp.SeleniumLocator,
        wait_click: float,
        check_click: bool = False,
        locator_iframe: utils_seleniumxp.SeleniumLocator | None = None,
        wait_iframe: float = 1,
        locator_shadowdomhost: utils_seleniumxp.SeleniumLocator | list[utils_seleniumxp.SeleniumLocator] | None = None
    ) -> bool:
        return closepopup_queueadd_eventfiring(self, locator_click, wait_click, check_click, locator_iframe, wait_iframe, locator_shadowdomhost)

    def closepopup_queueprocessing(self, firstonly: bool = True) -> bool:
        return closepopup_queueprocessing_eventfiring(self, firstonly)



# user agent

# get user agent via JavaScript
def get_user_agent(webdriver: utils_seleniumxp._RemoteWebDriver) -> str:
    """
    get_user_agent - get user agent via javascript

    Args:
        webdriver (utils_seleniumxp._RemoteWebDriver): webdriver

    Returns:
        str: user agent string
    """
    return webdriver.execute_script("return navigator.userAgent")

# direct settattr instead of mixin-object but avoid name conflict
if not utils_seleniumxp.mixinactive:
    setattr(utils_seleniumxp._RemoteWebDriver, "get_user_agent", get_user_agent)


# element present

# check if element is present
def is_present(
    webdriver: utils_seleniumxp._RemoteWebDriver,
    by: utils_seleniumxp.By,
    value: str,
    use_parsel: bool = True
) -> bool:
    """
    is_present - check if webelement is present

    If element is not present, the standard routine is pretty time-consuming compared to parsel
    using C implemented lxml library. The overhead caused by the library is comparably slow.
    However, parsel can only be used for XPATH and CSS.

    Args:
        webdriver (utils_seleniumxp._RemoteWebDriver): webdriver
        by (utils_seleniumxp.By): locator type
        value (str): locator value
        use_parsel (bool, optional): flag to use parsel. Defaults to True.

    Returns:
        bool: flag if element is present or not
    """

    if use_parsel and by in {utils_seleniumxp.By.XPATH, utils_seleniumxp.By.CSS_SELECTOR}:
        parsedhtml = utils_seleniumxp.locatorutils.parselSelectorExtension(text=webdriver.page_source)
        return len(parsedhtml.css_or_xpath(utils_seleniumxp.SeleniumLocator(by, value)).getall()) > 0
    else:
        # alternative variant -> as slow as try-variant if not present (even slightly slower in case element is present)
        # but potentially more errors if descriptor is not unique
        # return len(webdriver.find_elements(by, value)) > 0
        try:
            webdriver.find_element(by, value)
        except Exception:
            return False
        else:
            return True

def is_element_present(
    webdriver: utils_seleniumxp._RemoteWebDriver,
    by: utils_seleniumxp.By,
    value: str,
    use_parsel: bool = True
) -> bool:
    """
    is_element_present - check if webelement is present (alternative caller vor _is_present)
    """
    return is_present(webdriver, by, value, use_parsel)

# direct settattr instead of mixin-object but avoid name conflict
# (not relevant for EventFiringWebDriver)
if not utils_seleniumxp.mixinactive:
    setattr(utils_seleniumxp._RemoteWebDriver, "is_present", is_present)
    setattr(utils_seleniumxp._RemoteWebDriver, "is_element_present", is_present)


# find elements - optimized if not present

# find elements optimized
def find_elements_optimized(
    webdriver: utils_seleniumxp._RemoteWebDriver,
    by: utils_seleniumxp.By,
    value: str,
    use_parsel: bool = True
) -> list[utils_seleniumxp._WebElement]:
    """
    find_elements_optimized - optimized find_elements using parsel

    Args:
        webdriver (utils_seleniumxp._RemoteWebDriver): webdriver
        by (utils_seleniumxp.By): locator type
        value (str): locator value
        use_parsel (bool, optional): flag to use parsel. Defaults to True.

    Returns:
        list[utils_seleniumxp._WebElement]: list of webelements matching locator
    """

    if use_parsel and by in {utils_seleniumxp.By.XPATH, utils_seleniumxp.By.CSS_SELECTOR}:
        if webdriver.is_present(by, value, use_parsel):
            return webdriver.find_elements(by, value)
        else:
            return []
    else:
        return webdriver.find_elements(by, value)

# direct settattr instead of mixin-object but avoid name conflict
# (not relevant for EventFiringWebDriver)
if not utils_seleniumxp.mixinactive:
    setattr(utils_seleniumxp._RemoteWebDriver, "find_elements_optimized", find_elements_optimized)


# hover over element

# hover over element
def hover_over_element(
    webdriver: utils_seleniumxp._RemoteWebDriver,
    by: utils_seleniumxp.By,
    value: str,
    by_host: utils_seleniumxp.By | None = None,
    value_host: str | None = None
) -> None:
    """
    hover_over_element - action chain to hover over element

    Args:
        webdriver (utils_seleniumxp._RemoteWebDriver): webdriver
        by (utils_seleniumxp.By): locator type
        value (str): locator value
        by_host (utils_seleniumxp.By, optional): locator type of shadowhost. Defaults to None.
        value_host (str, optional): locator value of shadowhost. Defaults to None.
"""

    if value_host is None:
        if webdriver.is_present(by, value):
            webelement = webdriver.find_element(by, value)
    else:
        shadowroot = webdriver.find_root_shadowdom_simple(by_host, value_host)
        webelement = webdriver.find_element_shadowdom_simple(by, value, shadowroot)
    utils_seleniumxp.ActionChains(webdriver).move_to_element(webelement).perform()

# direct settattr instead of mixin-object but avoid name conflict
# (not relevant for EventFiringWebDriver)
if not utils_seleniumxp.mixinactive:
    setattr(utils_seleniumxp._RemoteWebDriver, "hover_over_element", hover_over_element)


# alert handling

# alert handler including check of alert text
def handle_alert(webdriver: utils_seleniumxp._RemoteWebDriver, alerttext: str, accept: bool = False) -> bool:
    """
    handle_alert - handle alert

    Args:
        webdriver (utils_seleniumxp._RemoteWebDriver): webdriver
        alerttext (str): alert text
        accept (bool, optional): accept yes or no. Defaults to False.

    Returns:
        bool: flag if alert was processed successfully or not
    """

    if utils_seleniumxp.ExpectedConditions.alert_is_present():  # type: ignore[truthy-function]
        try:
            alert = webdriver._switch_to.alert
            alertmatch = (not alerttext or fnmatch.fnmatch(alert.text, "*" + alerttext + "*"))
            if alertmatch:
                if accept:
                    alert.accept()
                else:
                    alert.dismiss()
                return True
            else:
                return False
        except utils_seleniumxp.WebDriverExceptions.NoAlertPresentException:
            return False
    else:
        return False

# direct settattr instead of mixin-object but avoid name conflict
if not utils_seleniumxp.mixinactive:
    setattr(utils_seleniumxp._RemoteWebDriver, "handle_alert", handle_alert)
    setattr(utils_seleniumxp.eventfiring_addon.EventFiringWebDriverExtended, "handle_alert", handle_alert)


# close new windows opened automatically f. e. by downloads

# close new windows opened by automatic downloads, ...
# note: transfer value for parameter keepwindows as list even if a single handle !!!
def closewindows(webdriver: utils_seleniumxp._RemoteWebDriver, keepwindows: list) -> None:
    """
    closewindows - close windows except those in 'keeplist'

    Args:
        webdriver (utils_seleniumxp._RemoteWebDriver): webdriver
        keepwindows (list): list with windows to keep
    """

    keepcount: int = len(keepwindows)
    if keepcount == 0:
        return

    while len(webdriver.window_handles) > keepcount:
        for handle in reversed(webdriver.window_handles):
            if handle not in keepwindows:
                webdriver.switch_to.window(handle)
                webdriver.close()
                break

def close_windows(webdriver: utils_seleniumxp._RemoteWebDriver, keepwindows: list) -> None:

    closewindows(webdriver, keepwindows)

# direct settattr instead of mixin-object but avoid name conflict
if not utils_seleniumxp.mixinactive:
    setattr(utils_seleniumxp._RemoteWebDriver, "closewindows", closewindows)
    setattr(utils_seleniumxp._RemoteWebDriver, "close_windows", closewindows)


# extended wait for page load - readyState + AJAX-script

# wait for AJAX script and readyState
# first check if jQuery is active
def wait4AJAX(webdriver: utils_seleniumxp._RemoteWebDriver, timeout: int = 10, min_wait: float = 0.5) -> bool:
    """
    wait4AJAX - wait routine checking jQuery.active via JavaScript and document.readyState

    Args:
        webdriver (utils_seleniumxp._RemoteWebDriver): webdriver
        timeout (int): timeout
        min_wait (float, optional): minimum wait time. Defaults to 0.5.

    Returns:
        bool: flag if timeout reached
    """

    # check "smartwait" mode not used
    if not getattr(webdriver, "_smartwait", None):
        # check jQuery state
        starttime = time.time()
        timeoutscript = False
        try:
            utils_seleniumxp.WebDriverWait(webdriver, 1).until(lambda webdriver: webdriver.execute_script('return jQuery.active') == 0)
        except (utils_seleniumxp.WebDriverExceptions.JavascriptException, utils_seleniumxp.WebDriverExceptions.TimeoutException):
            pass
        else:
            try:
                utils_seleniumxp.WebDriverWait(webdriver, timeout).until(lambda webdriver: webdriver.execute_script('return jQuery.active') == 0)
            except utils_seleniumxp.WebDriverExceptions.TimeoutException:
                timeoutscript = True
        # check document.readyState
        timeoutdocrs = False
        try:
            utils_seleniumxp.WebDriverWait(webdriver, timeout).until(lambda webdriver: webdriver.execute_script('return document.readyState') == 'complete')
        except utils_seleniumxp.WebDriverExceptions.TimeoutException:
            timeoutdocrs = True
        while (time.time() < starttime + min_wait):
            time.sleep(0.1)
        return timeoutscript or timeoutdocrs
    else:
        return False

# wait for HTML, AJAX script and readyState
def wait4HTMLstable(webdriver: utils_seleniumxp._RemoteWebDriver, wait: float = 0.1, max_wait: float = 0.5) -> bool:
    """
    wait4HTMLstable - wait routine checking stability page source

    Args:
        webdriver (utils_seleniumxp._RemoteWebDriver): webdriver
        wait (float, optional): wait between re-checks. Defaults to 0.1.
        max_wait (float, optional): timeout. Defaults to 0.5.

    Returns:
        bool: flag if page source is stable
    """

    # check "smartwait" mode not used
    if not getattr(webdriver, "_smartwait", None):
        # call "lower" level wait
        wait4AJAX(webdriver)
        HTMLprev = ""
        starttime = time.time()
        # check for HTML source stable
        while (HTMLprev != webdriver.page_source and (time.time() < starttime + max_wait)):
            HTMLprev = webdriver.page_source
            time.sleep(wait)
        return HTMLprev == webdriver.page_source
    else:
        return True


# direct setattr instead of mixin-object but avoid name conflict
if not utils_seleniumxp.mixinactive:
    setattr(utils_seleniumxp._RemoteWebDriver, "wait4AJAX", wait4AJAX)
    setattr(utils_seleniumxp._RemoteWebDriver, "wait4HTMLstable", wait4HTMLstable)


# extended wait for page load - source from ObeyTheTestingGoat
@contextlib.contextmanager
def wait_for_page_load(webdriver: utils_seleniumxp._RemoteWebDriver, timeout=10) -> Generator:
    """
    wait_for_page_load - wait routine with contextmanager from ObeyTheTestingGoat

    method checks for the staleness of the old page (i.e., that the new page has loaded)
    prior to moving forward with further actions. Therefore, it only works in situations
    where the URL changes between page loads.

    Usage:
    with self.wait_for_page_load():
        click a button or do whatever
    do the next thing that was failing before using this

    Args:
        webdriver (utils_seleniumxp._RemoteWebDriver): webdriver
        timeout (int, optional): timeout. Defaults to 10.

    Return:
        (Generator): contextmanager generator
    """
    old_page = webdriver.find_element(utils_seleniumxp.By.TAG_NAME, 'html')
    yield
    utils_seleniumxp.WebDriverWait(webdriver, timeout).until(utils_seleniumxp.ExpectedConditions.staleness_of(old_page))

# direct setattr instead of mixin-object but avoid name conflict
if not utils_seleniumxp.mixinactive:
    setattr(utils_seleniumxp._RemoteWebDriver, "wait_for_page_load", wait_for_page_load)
