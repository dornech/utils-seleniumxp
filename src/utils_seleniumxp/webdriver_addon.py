# Selenium webdriver utilities - XP version
# webdriver class - additional functionalities

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
# ruff: noqa: B010, E301, E305, E501, PLR0904, PLR0914, PLR0917, PLR1702, PLR5501, SIM102
#
# disable mypy errors
# mypy: disable-error-code = "no-any-return"

# fmt: off



# TODO Dev:
# - more comfortable wait_for
#   params element, condition, timeout
# - find_element_frames -> loop across frames automatically?
# - integrate new Selenium 4.x API functions
#   - scroll from Actions-API (instead of script calling)
#     see https://www.selenium.dev/documentation/webdriver/actions_api/wheel/
# - automatic retry for find_element(s) (see seleniumbase as inspiration) ?
#   approach 1: derived class with redefinition and call of super-method
#   approach 2: create wrapped method and re-direct call via setattr
# - implement additional helpers like automated findwait_for_element, download (see horejsek wrapper or selgym)
#   alternatively: derived class with redefinition and call of super method?

# TODO Test:
# - n. a.



from typing import Optional, Union

import contextlib

import time
import fnmatch      # alternative: simplematch

# import queue
import collections

import cssify
from seleniumrequests.request import RequestsSessionMixin as _RequestsSessionMixin

import utils_seleniumxp



# block direct calling
# __all__ = []



# webdriver mixins approach - require Mixin classes to be used for additional functionality
# mixin-class required per browser specific webdriver class
# optional: use setattr (assumption: derived wrapper classes should automatically inherit methods)

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
        return get_user_agent(self)

    # mixin for is_present / is_element_present

    def is_present(self, by: utils_seleniumxp.By, value: str, use_parsel: bool = True) -> bool:
        return is_present(self, by, value, use_parsel)

    def is_element_present(self, by: utils_seleniumxp.By, value: str, use_parsel: bool = True) -> bool:
        return is_present(self, by, value, use_parsel)

    # mixin for find_elements_optimized
    def find_elements_optimized(self, by: utils_seleniumxp.By, value: str, use_parsel: bool = True) -> list[utils_seleniumxp._WebElement]:
        return find_elements_optimized(self, by, value, use_parsel)

    # mixin for find_shadowroot, find_elements_shadowdom and find_element_shadowdom

    def find_root_shadowdom(self, by: utils_seleniumxp.By, value: str) -> Optional[utils_seleniumxp._WebElement]:
        return find_root_shadowdom(self, by, value)

    def find_elements_shadowdom_simple(self, by: utils_seleniumxp.By, value: str, shadowroot: utils_seleniumxp._WebElement) -> Optional[list[utils_seleniumxp._WebElement]]:
        return find_elements_shadowdom_simple(self, by, value, shadowroot)

    def find_elements_shadowdom(self, locator_list: list[utils_seleniumxp.SeleniumLocator], shadowroot: Optional[utils_seleniumxp._WebElement] = None) -> Optional[utils_seleniumxp._WebElement]:
        return find_elements_shadowdom(self, locator_list, shadowroot)

    def find_element_shadowdom_simple(self, by: utils_seleniumxp.By, value: str, shadowroot: utils_seleniumxp._WebElement) -> Optional[utils_seleniumxp._WebElement]:
        return find_element_shadowdom_simple(self, by, value, shadowroot)

    def find_element_shadowdom(self, locator_list: list[utils_seleniumxp.SeleniumLocator], shadowroot: Optional[utils_seleniumxp._WebElement] = None) -> Optional[utils_seleniumxp._WebElement]:
        return find_element_shadowdom(self, locator_list, shadowroot)

    # mixin for is_present_shadowdom

    def is_present_shadowdom(self, locator_list: list[utils_seleniumxp.SeleniumLocator], shadowroot: Optional[utils_seleniumxp._WebElement] = None) -> bool:
        return is_present_shadowdom(self, locator_list, shadowroot)

    def is_element_present_shadowdom(self, locator_list: list[utils_seleniumxp.SeleniumLocator], shadowroot: Optional[utils_seleniumxp._WebElement] = None) -> bool:
        return is_element_present_shadowdom(self, locator_list, shadowroot)

    # mixin for hover over element
    def hover_over_element(self, by: utils_seleniumxp.By, value: str, by_host: Optional[utils_seleniumxp.By], value_host: Optional[str]) -> None:
        hover_over_element(self, by, value, by_host, value_host)

    # mixin for handle_alert
    def handle_alert(self, alerttext: str, accept: bool = False) -> bool:
        return handle_alert(self, alerttext, accept)

    # mixin for closepopup routines

    def closepopup(self, locator_click: utils_seleniumxp.SeleniumLocator, wait_click: float, check_click: bool = False, locator_iframe: utils_seleniumxp.SeleniumLocator = None, wait_iframe: float = 1, locator_shadowdomhost: utils_seleniumxp.SeleniumLocator = None) -> bool:
        return closepopup(self, locator_click, wait_click, check_click, locator_iframe, wait_iframe, locator_shadowdomhost)

    def closepopup_queueadd(self, locator_click: utils_seleniumxp.SeleniumLocator, wait_click: float, check_click: bool = False, locator_iframe: utils_seleniumxp.SeleniumLocator = None, wait_iframe: float = 1, locator_shadowdomhost: utils_seleniumxp.SeleniumLocator = None) -> None:
        closepopup_queueadd(self, locator_click, wait_click, check_click, locator_iframe, wait_iframe, locator_shadowdomhost)

    def closepopup_queueprocessing(self, firstonly: bool = True) -> bool:
        return closepopup_queueprocessing(self, firstonly)

    # mixin for closewindows
    def closewindows(self, keepwindows: list):
        closewindows(self, keepwindows)

    # mixin for wait4AJAX and wait4HTMLstable

    def wait4AJAX(self, timeout: int = 15, minwait: float = 0.0) -> bool:
        return wait4AJAX(self, timeout, minwait)

    def wait4HTMLstable(self, wait: float = 0.1, maxwait: float = 0.5) -> bool:
        return wait4HTMLstable(self, wait, maxwait)

    # extended wait for page load - source from ObeytheTestingGoat
    def wait_for_page_load(self, timeout=10):
        return wait_for_page_load(self, timeout)


# mixin overlay for 3rd party extensions always mixed in
def WebDriver3rdPartyMixedin(
    cls_webdriver: type[utils_seleniumxp._RemoteWebDriver]
) -> type[utils_seleniumxp._RemoteWebDriver]:
    """
    WebDriver3rdPartyMixedin - factory function for custom class with fixed 3rd party mixins

    The factory function mechanism is required to use alternative base classes like
    undetected_chromedriver.

    Args:
        cls_webdriver (type[utils_seleniumxp._RemoteWebDriver]): base class

    Returns:
        type[utils_seleniumxp._RemoteWebDriver]: custom webdriver class with mixin
    """

    class WebDriverClassCustom(_RequestsSessionMixin, cls_webdriver):
        pass

    return WebDriverClassCustom

# own mixin overlay
def WebDriverMixedin(
    cls_webdriver: type[utils_seleniumxp._RemoteWebDriver]
) -> type[utils_seleniumxp._RemoteWebDriver]:
    """
    WebDriver3rdPartyMixedin - factory function for custom class with fixed 3rd party mixins and own mixin

    The factory function mechanism is required to use alternative base classes like
    undetected_chromedriver.

    Args:
        cls_webdriver (type[utils_seleniumxp._RemoteWebDriver]): base class

    Returns:
        type[utils_seleniumxp._RemoteWebDriver]: custom webdriver class with mixin
    """

    class WebDriverClassCustom(_WebDriverMixin, _RequestsSessionMixin, cls_webdriver):
        pass

    return WebDriverClassCustom


# mixin class for eventfiring webdriver
class EventFiringWebDriverExtendedMixedin(utils_seleniumxp.eventfiring_addon.EventFiringWebDriverExtended):
    """
    EventFiringWebDriverExtendedMixedin - mixin class for eventfiring webdriver
    """

    # mixin for handle_alert
    def handle_alert(self, alerttext: str, accept: bool = False) -> bool:
        return handle_alert(self, alerttext, accept)

    # mixin for closepopup routines
    def closepopup(self, locator_click: utils_seleniumxp.SeleniumLocator, wait_click: float, check_click: bool = False, locator_iframe: utils_seleniumxp.SeleniumLocator = None, wait_iframe: float = 1, locator_shadowdomhost: utils_seleniumxp.SeleniumLocator = None) -> bool:
        return closepopup_eventfiring(self, locator_click, wait_click, check_click, locator_iframe, wait_iframe, locator_shadowdomhost)
    def closepopup_queueadd(self, locator_click: utils_seleniumxp.SeleniumLocator, wait_click: float, check_click: bool = False, locator_iframe: utils_seleniumxp.SeleniumLocator = None, wait_iframe: float = 1, locator_shadowdomhost: utils_seleniumxp.SeleniumLocator = None) -> bool:
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
    is_present - check if element is present

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
    find_elements_optimized - optimized find_elements using parsel.

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


# find elements in shadow DOM

# Note:
# - remember to escape quotes in CSS selectors
# - when integrating into event firing webdriver watch out due to recursive call like for closepopup
# - *_simple functions/methods are stubs for overhauled old logic

# find shadow DOM root
def find_root_shadowdom(
    webdriver: utils_seleniumxp._RemoteWebDriver,
    by: utils_seleniumxp.By,
    value: str
) -> Optional[utils_seleniumxp._ShadowRoot]:
    """
    find_root_shadowdom - find shadowDOM root

    Args:
        webdriver (utils_seleniumxp._RemoteWebDriver): browser
        by (utils_seleniumxp.By): locator type of element hosting shadowDOM root
        value (str): locator value of element hosting shadowDOM root

    Returns:
        Optional[utils_seleniumxp._WebElement]: shadowDOM root if found
    """

    shadowhost = webdriver.find_element(by, value)
    shadowroot = webdriver.execute_script("return arguments[0].shadowRoot", shadowhost)
    return shadowroot

# find elements in shadow DOM old/simple version
def find_elements_shadowdom_simple(
    webdriver: utils_seleniumxp._RemoteWebDriver,
    by: utils_seleniumxp.By,
    value: str,
    shadowroot: Union[utils_seleniumxp._ShadowRoot, utils_seleniumxp._WebElement]
) -> Optional[list[utils_seleniumxp._WebElement]]:
    """
    find_elements_shadowdom_simple - find elements in shadowDOM

    Args:
        webdriver (utils_seleniumxp._RemoteWebDriver): webdriver
        by (utils_seleniumxp.By): locator type
        value (str): locator value
        shadowroot (Union[utils_seleniumxp._ShadowRoot, utils_seleniumxp._WebElement]): shadowDOM root

    Returns:
        Optional[utils_seleniumxp._WebElement]: list of webelements in shadowDOM if found
    """
    return find_elements_shadowdom(webdriver, [utils_seleniumxp.SeleniumLocator(by, value)], shadowroot)

# find elements in shadow DOM with support for nested DOM - with root as optional parameter
def find_elements_shadowdom(
    webdriver: utils_seleniumxp._RemoteWebDriver,
    locator_list: list[utils_seleniumxp.SeleniumLocator],
    shadowroot: Optional[Union[utils_seleniumxp._ShadowRoot, utils_seleniumxp._WebElement]] = None
) -> Optional[list[utils_seleniumxp._WebElement]]:
    """
    find_elements_shadowdom - find elements in shadowDOM with support for nested shadowDOM

    Note: every item in the locator list must be a locator to a host of another shadowDOM root.
    The routine also accepts the shadowhost element and derives the shadowroot automatically.

    Args:
        webdriver (utils_seleniumxp._RemoteWebDriver): webdriver
        locator_list (list[utils_seleniumxp.SeleniumLocator]): locator list
        shadowroot (Optional[Union[utils_seleniumxp._ShadowRoot, utils_seleniumxp._WebElement]], optional): shadowDOM root. Defaults to None.

    Returns:
        Optional[list[utils_seleniumxp._WebElement]]: list of webelements in shadowDOM if found
    """

    def prepare_selector(locator: utils_seleniumxp.SeleniumLocator) -> str:

        if locator.by == utils_seleniumxp.By.XPATH:
            return cssify.cssify(locator.value)
        elif locator.by == utils_seleniumxp.By.CSS_SELECTOR:
            return locator.value
        else:
            err_msg = "Only CSS selector allowed together with element in shadowDOM."
            raise utils_seleniumxp.ErrorUtilsSelenium(err_msg)

    if len(locator_list) > 1 or shadowroot is not None:
        queryselector = ""
        for i in range(0, len(locator_list) - 1):
            queryselector = queryselector + ".querySelector('" + prepare_selector(locator_list[i]) + "').shadowRoot"
        queryselector = queryselector + ".querySelectorAll('" + prepare_selector(locator_list[-1]) + "')"
        if shadowroot is not None:
            if shadowroot.__class__.__name__ != "ShadowRoot":
                # overcome issue that ShadwoDOM host but not root is provided, try to treat shadowroot as host to derive correct root
                shadowroot = webdriver.execute_script("return arguments[0].shadowRoot", shadowroot)
            # overcome issue with id attribute, discovered missing in JSON return when accessing shadow root in May 2025
            if not hasattr(shadowroot, "id"):
                shadowroot.id = shadowroot._id
            try:
                return webdriver.execute_script(f"return arguments[0]{queryselector}", shadowroot)
            except Exception:
                return None
        else:
            try:
                return webdriver.execute_script(f"return document{queryselector}")
            except Exception:
                return None
    else:
        err_msg = "No sufficient selector information provided to access element in shadowDOM."
        raise utils_seleniumxp.ErrorUtilsSelenium(err_msg)

# find element in shadow DOM old/simple version
def find_element_shadowdom_simple(
    webdriver: utils_seleniumxp._RemoteWebDriver,
    by: utils_seleniumxp.By,
    value: str,
    shadowroot: Union[utils_seleniumxp._ShadowRoot, utils_seleniumxp._WebElement]
) -> Optional[utils_seleniumxp._WebElement]:
    """
    find_element_shadowdom_simple - find element in shadowDOM

    Args:
        webdriver (utils_seleniumxp._RemoteWebDriver): webdriver
        by (utils_seleniumxp.By): locator type
        value (str): locator value
        shadowroot (Union[utils_seleniumxp._ShadowRoot, utils_seleniumxp._WebElement]): shadowDOM root

    Returns:
        Optional[utils_seleniumxp._WebElement]: webelement in shadowDOM if found
    """
    return find_element_shadowdom(webdriver, [utils_seleniumxp.SeleniumLocator(by, value)], shadowroot)

# find element in shadow DOM with support for nested DOM - with top root as optional parameter
def find_element_shadowdom(
    webdriver: utils_seleniumxp._RemoteWebDriver,
    locator_list: list[utils_seleniumxp.SeleniumLocator],
    shadowroot: Optional[Union[utils_seleniumxp._ShadowRoot, utils_seleniumxp._WebElement]] = None
) -> Optional[utils_seleniumxp._WebElement]:
    """
    find_element_shadowdom - find element in shadowDOM with support for nested shadowDOM

    Note: every item in the locator list must be a locator to a host of another shadowDOM root.

    Args:
        webdriver (utils_seleniumxp._RemoteWebDriver): webdriver
        locator_list (list[utils_seleniumxp.SeleniumLocator]): locator list
        shadowroot (Optional[Union[utils_seleniumxp._ShadowRoot, utils_seleniumxp._WebElement]], optional): shadowDOM root. Defaults to None.

    Returns:
        Optional[utils_seleniumxp._WebElement]: webelement in shadowDOM if found
    """

    webelts = find_elements_shadowdom(webdriver, locator_list, shadowroot)
    if webelts is not None and webelts != []:
        if len(webelts) == 1:
            return webelts[0]
        else:
            err_msg = "Multiple elements for descriptor in shadow DOM"
            raise utils_seleniumxp.ErrorUtilsSelenium(err_msg)
    else:
        return None

# check if element present in shadow DOM with support for nested DOM - top root as optional parameter
def is_present_shadowdom(
    webdriver: utils_seleniumxp._RemoteWebDriver,
    locator_list: list[utils_seleniumxp.SeleniumLocator],
    shadowroot: Optional[Union[utils_seleniumxp._ShadowRoot, utils_seleniumxp._WebElement]] = None
) -> bool:
    """
    is_present_shadowdom - check if element is present in shadowDOM

    Note: every item in the locator list must be a locator to a host of another shadowDOM root.

    Args:
        webdriver (utils_seleniumxp._RemoteWebDriver): webdriver
        locator_list (list[utils_seleniumxp.SeleniumLocator]): locator list
        shadowroot (Optional[Union[utils_seleniumxp._ShadowRoot, utils_seleniumxp._WebElement]], optional): shadowDOM root. Defaults to None.

    Returns:
        bool: flag if element is present or not
    """

    webelts = find_elements_shadowdom(webdriver, locator_list, shadowroot)
    return webelts is not None and webelts != []

def is_element_present_shadowdom(
    webdriver: utils_seleniumxp._RemoteWebDriver,
    locator_list: list[utils_seleniumxp.SeleniumLocator],
    shadowroot: Optional[Union[utils_seleniumxp._ShadowRoot, utils_seleniumxp._WebElement]] = None
) -> bool:
    return is_present_shadowdom(webdriver, locator_list, shadowroot)

# direct settattr instead of mixin-object but avoid name conflict
# (not relevant for EventFiringWebDriver)
if not utils_seleniumxp.mixinactive:
    setattr(utils_seleniumxp._RemoteWebDriver, "find_root_shadowdom", find_root_shadowdom)
    setattr(utils_seleniumxp._RemoteWebDriver, "find_elements_shadowdom_simple", find_elements_shadowdom_simple)
    setattr(utils_seleniumxp._RemoteWebDriver, "find_elements_shadowdom", find_elements_shadowdom)
    setattr(utils_seleniumxp._RemoteWebDriver, "find_element_shadowdom_simple", find_element_shadowdom_simple)
    setattr(utils_seleniumxp._RemoteWebDriver, "find_element_shadowdom", find_element_shadowdom)
    setattr(utils_seleniumxp._RemoteWebDriver, "is_present_shadowdom", is_present_shadowdom)
    setattr(utils_seleniumxp._RemoteWebDriver, "is_element_present_shadowdom", is_present_shadowdom)


# hover over element

# hover over element
def hover_over_element(
    webdriver: utils_seleniumxp._RemoteWebDriver,
    by: utils_seleniumxp.By,
    value: str,
    by_host: Optional[utils_seleniumxp.By],
    value_host: Optional[str]
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
        shadowroot = webdriver.find_root_shadowdom(by_host, value_host)
        webelement = webdriver.find_element_shadowdom_simple(by, value, shadowroot)
    utils_seleniumxp.WebDriver.ActionChains(webdriver).move_to_element(webelement).perform()

# direct settattr instead of mixin-object but avoid name conflict
# (not relevant for EventFiringWebDriver)
if not utils_seleniumxp.mixinactive:
    setattr(utils_seleniumxp._RemoteWebDriver, "hover_over_element", hover_over_element)


# alert handling

# alert handler including check of alert text
def handle_alert(webdriver: utils_seleniumxp._RemoteWebDriver, alerttext: str, accept: bool = False) -> bool:
    """
    handle_alert

    Args:
        webdriver (utils_seleniumxp._RemoteWebDriver): webdriver
        alerttext (str): alert text
        accept (bool, optional): accept yes or no. Defaults to False.

    Returns:
        bool: flag if alert was processed successfully or not
    """

    if utils_seleniumxp.ExpectedConditions.alert_is_present():
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


# close popups - processing via a queue to speed up subsequent tries to close popups via html parsing
#
# note: when using shadow DOM ist seems CSS is mandatory at least for end nodes
# see https://github.com/SeleniumHQ/selenium/issues/4971

# close popup using parsel for XPath and CSS
def closepopup(
        webdriver: utils_seleniumxp._RemoteWebDriver,
        locator_click: utils_seleniumxp.SeleniumLocator,
        wait_click: float = 0.1, check_click: bool = False,
        locator_iframe: utils_seleniumxp.SeleniumLocator = None,
        wait_iframe: float = 1,
        locator_shadowdomhost: utils_seleniumxp.SeleniumLocator = None
) -> bool:
    """
    closepopup - close popups with use of parsel

    Args:
        webdriver (utils_seleniumxp._RemoteWebDriver): webdriver
        locator_click (utils_seleniumxp.SeleniumLocator): locator for webelement to lcick for closing
        wait_click (float, optional): wait after click. DEfaults to 0.1.
        check_click (bool, optional): check after click if popup closed. Defaults to False.
        locator_iframe (utils_seleniumxp.SeleniumLocator, optional): locator for iframe containing click object. Defaults to None.
        wait_iframe (float, optional): wait to switch to iframe. Defaults to 1.
        locator_shadowdomhost (utils_seleniumxp.SeleniumLocator, optional): locator to shadowDOM host. Defaults to None.

    Returns:
        bool: flag if a matching popup was found and closed
    """

    closepopup_queueadd(webdriver, locator_click, wait_click, check_click, locator_iframe, wait_iframe, locator_shadowdomhost)
    return closepopup_queueprocessing(webdriver)

# closepopup - queue request
def closepopup_queueadd(
        webdriver: utils_seleniumxp._RemoteWebDriver,
        locator_click: utils_seleniumxp.SeleniumLocator,
        wait_click: float = 0.1, check_click: bool = False,
        locator_iframe: utils_seleniumxp.SeleniumLocator = None,
        wait_iframe: float = 1,
        locator_shadowdomhost: utils_seleniumxp.SeleniumLocator = None
) -> None:
    """
    closepopup_queueadd - add entry to closepopop processing queue

    Args:
        webdriver (utils_seleniumxp._RemoteWebDriver): webdriver
        locator_click (utils_seleniumxp.SeleniumLocator): locator for webelement to lcick for closing
        wait_click (float, optional): wait after click. DEfaults to 0.1.
        check_click (bool, optional): check after click if popup closed. Defaults to False.
        locator_iframe (utils_seleniumxp.SeleniumLocator, optional): locator for iframe containing click object. Defaults to None.
        wait_iframe (float, optional): wait to switch to iframe. Defaults to 1.
        locator_shadowdomhost (utils_seleniumxp.SeleniumLocator, optional): locator to shadowDOM host. Defaults to None.
    """

    # check if webdriver has queue attribute already
    if hasattr(webdriver, 'closepopup_queue'):
        pass
    else:
        closepopup_queue = collections.deque()  # type: ignore[var-annotated]
        setattr(webdriver, 'closepopup_queue', closepopup_queue)

    # add to queue
    queueentry = {
        "locator_click": locator_click,
        "wait_click": wait_click,
        "check_click": check_click,
        "locator_iframe": locator_iframe,
        "wait_iframe": wait_iframe,
        "locator_shadowdomhost": locator_shadowdomhost
    }
    webdriver.closepopup_queue.append(queueentry)

# closepopup - queue processing
def closepopup_queueprocessing(webdriver: utils_seleniumxp._RemoteWebDriver, firstonly: bool = True) -> bool:
    """
    closepopup_queueprocessing - process closepopup queue

    Args:
        webdriver (utils_seleniumxp._RemoteWebDriver): webdriver
        firstonly (bool, optional): process  first found target webelement only. Defaults to True.

    Returns:
        bool: flag if a matching popup was found and closed
    """

    # set return default
    closedpopup: bool = False

    if hasattr(webdriver, 'closepopup_queue'):

        if len(webdriver.closepopup_queue) > 0:
            webdriver.wait4AJAX()
            parsedhtml = utils_seleniumxp.locatorutils.parselSelectorExtension(text=webdriver.page_source)

        while len(webdriver.closepopup_queue) > 0:

            webdriver.wait4AJAX()
            queueentry = webdriver.closepopup_queue.popleft()

            locator_click = queueentry["locator_click"]
            wait_click = queueentry["wait_click"]
            check_click = queueentry["check_click"]
            locator_iframe = queueentry["locator_iframe"]
            wait_iframe = queueentry["wait_iframe"]
            locator_shadowdomhost = queueentry["locator_shadowdomhost"]

            if not firstonly or not closedpopup:

                # convert locator within shadowDOM to CSS
                if locator_shadowdomhost is not None:
                    if locator_click.by == utils_seleniumxp.By.XPATH:
                        locator_click = utils_seleniumxp.SeleniumLocator(utils_seleniumxp.By.CSS_SELECTOR, cssify.cssify(locator_click.value))
                    elif locator_click.by != utils_seleniumxp.By.CSS_SELECTOR:
                        utils_seleniumxp.ErrorUtilsSelenium("Only CSS selector allowed together with element in shadowDOM.")

                # initialize parsedhtml at beginning of loop
                parsedhtml = utils_seleniumxp.locatorutils.parselSelectorExtension(text=webdriver.page_source)

                # go to frame of popup (if any)
                if locator_iframe is not None:
                    if utils_seleniumxp.locatorutils.check_locator(locator_iframe, [utils_seleniumxp.By.XPATH, utils_seleniumxp.By.CSS_SELECTOR]):
                        frames = parsedhtml.css_or_xpath(locator_iframe).getall()
                        # re-parse once, sometimes timing problem -> caused by switch-to error
                        if len(frames) == 0:
                            parsedhtml = utils_seleniumxp.locatorutils.parselSelectorExtension(text=webdriver.page_source)
                            frames = parsedhtml.css_or_xpath(locator_iframe).getall()
                    else:
                        frames = webdriver.find_elements(*locator_iframe)
                    if len(frames) == 0:
                        if hasattr(webdriver, "closepopup_logger"):
                            webdriver.closepopup_logger.info(f"FRAME not found\t{webdriver.current_url}\t({locator_click})\t({locator_iframe})\t({locator_shadowdomhost})")
                        continue
                    elif len(frames) == 1:
                        utils_seleniumxp.WebDriverWait(webdriver, wait_iframe).until(utils_seleniumxp.ExpectedConditions.frame_to_be_available_and_switch_to_it(locator_iframe))
                        if (utils_seleniumxp.locatorutils.check_locator(locator_click, [utils_seleniumxp.By.XPATH, utils_seleniumxp.By.CSS_SELECTOR]) or
                            utils_seleniumxp.locatorutils.check_locator(locator_shadowdomhost, [utils_seleniumxp.By.XPATH, utils_seleniumxp.By.CSS_SELECTOR])
                            ):
                            parsedhtml = utils_seleniumxp.locatorutils.parselSelectorExtension(text=webdriver.page_source)
                    elif len(frames) > 1:
                        if hasattr(webdriver, "closepopup_logger"):
                            webdriver.closepopup_logger.info(f"FRAME not unique\t{webdriver.current_url}\t({locator_click})\t({locator_iframe})\t({locator_shadowdomhost})")
                        continue

                # find close popup (considering also shadow DOM webelements)
                if locator_shadowdomhost is not None:
                    if utils_seleniumxp.locatorutils.check_locator(locator_shadowdomhost, [utils_seleniumxp.By.XPATH, utils_seleniumxp.By.CSS_SELECTOR]):
                        shadowhosts = parsedhtml.css_or_xpath(locator_shadowdomhost).getall()
                        # re-parse once, sometimes timing problem
                        if len(shadowhosts) == 0:
                            parsedhtml = utils_seleniumxp.locatorutils.parselSelectorExtension(text=webdriver.page_source)
                            shadowhosts = parsedhtml.css_or_xpath(locator_shadowdomhost).getall()
                    else:
                        shadowhosts = webdriver.find_elements(*locator_shadowdomhost)
                    if len(shadowhosts) == 0:
                        webelts = []
                        if hasattr(webdriver, "closepopup_logger"):
                            webdriver.closepopup_logger.info(f"ShadowDOM host not found\t{webdriver.current_url}\t({locator_click})\t({locator_iframe})\t({locator_shadowdomhost})")
                        continue
                    elif len(shadowhosts) == 1:
                        shadowhost = webdriver.find_element(*locator_shadowdomhost)
                        shadowroot = webdriver.execute_script("return arguments[0].shadowRoot", shadowhost)
                        webelts = shadowroot.find_elements(*locator_click)
                    else:
                        webelts = []
                        if hasattr(webdriver, "closepopup_logger"):
                            webdriver.closepopup_logger.info(f"ShadowDOM host not unique\t{webdriver.current_url}\t({locator_click})\t({locator_iframe})\t({locator_shadowdomhost})")
                        continue
                else:
                    if utils_seleniumxp.locatorutils.check_locator(locator_click, {utils_seleniumxp.By.XPATH, utils_seleniumxp.By.CSS_SELECTOR}):
                        webelts = parsedhtml.css_or_xpath(locator_click).getall()
                        webelts = webdriver.find_elements(*locator_click) if len(webelts) > 0 else []
                    else:
                        webelts = webdriver.find_elements(*locator_click)

                # close popup
                if len(webelts) > 0:

                    closedpopup_thisrun = False
                    for webelt in webelts:
                        try:
                            if webelt.is_displayed():
                                countwindows = len(webdriver.window_handles)
                                keepwindows = webdriver.window_handles
                                webelt.click()
                                if wait_click > 0:
                                    time.sleep(wait_click)
                                if len(webdriver.window_handles) > countwindows:
                                    closewindows(webdriver, keepwindows)
                                closedpopup = True
                                closedpopup_thisrun = True
                                if hasattr(webdriver, "closepopup_logger"):
                                    webdriver.closepopup_logger.info(f"found target\t{webdriver.current_url}\t({locator_click})\t({locator_iframe})\t({locator_shadowdomhost})")
                                break
                        except utils_seleniumxp.WebDriverExceptions.StaleElementReferenceException:
                            pass   # simple rerun
                        except:
                            raise

                    if check_click and closedpopup_thisrun:
                        if locator_shadowdomhost is not None:
                            webelts = shadowroot.find_elements(*locator_click)
                        else:
                            if utils_seleniumxp.locatorutils.check_locator(locator_click, {utils_seleniumxp.By.XPATH, utils_seleniumxp.By.CSS_SELECTOR}):
                                webelts = parsedhtml.css_or_xpath(locator_click).getall()
                                webelts = webdriver.find_elements(*locator_click) if len(webelts) > 0 else []
                            else:
                                webelts = webdriver.find_elements(*locator_click)
                        for webelt in webelts:
                            if webelt.is_displayed():
                                err_msg = "Popup could not be closed."
                                raise utils_seleniumxp.ErrorUtilsSelenium(err_msg)

                else:
                    if hasattr(webdriver, "closepopup_logger"):
                        webdriver.closepopup_logger.info(f"not found\t{webdriver.current_url}\t({locator_click})\t({locator_iframe})\t({locator_shadowdomhost})")

                # switch back from frame if necessary
                if locator_iframe is not None:
                    if len(frames) != 0:
                        webdriver.switch_to.default_content()

            else:
                if hasattr(webdriver, "closepopup_logger"):
                    webdriver.closepopup_logger.info(f"not checked\t{webdriver.current_url}\t({locator_click})\t({locator_iframe})\t({locator_shadowdomhost})")

    return closedpopup

# direct settattr instead of mixin-object but avoid name conflict
if not utils_seleniumxp.mixinactive:
    setattr(utils_seleniumxp._RemoteWebDriver, "closepopup", closepopup)
    setattr(utils_seleniumxp._RemoteWebDriver, "closepopup_queueadd", closepopup_queueadd)
    setattr(utils_seleniumxp._RemoteWebDriver, "closepopup_queueprocessing", closepopup_queueprocessing)


# closepopup methods for EventFiringWebDriver
#
# note:
# - as closepopup methods are not elementary methods i.e. other event firing methods are called, a special
#   treatment for "recursive" calling is required
# - as closepopup_queueadd creates a new attribute (the queue), when using EventFiringWebDriverExtended it must be
#   taken care that the attribute is created and accessed on same class level i.e. event firing driver class or
#   wrapped driver class level -> implementation prevents methods/calls marked as "recursive" on event firing
#   driver class level to be dispatched down to wrapped class level

def closepopup_eventfiring(webdriver: utils_seleniumxp.eventfiring_addon.EventFiringWebDriverExtended, locator_click: utils_seleniumxp.SeleniumLocator, wait_click: float, check_click: bool = False, locator_iframe: utils_seleniumxp.SeleniumLocator = None, wait_iframe: float = 1, locator_shadowdomhost: utils_seleniumxp.SeleniumLocator = None) -> bool:
    return webdriver._dispatch("closepopuphandler", ("simpleclose", webdriver._driver), "_closepopup", (locator_click, wait_click, check_click, locator_iframe, wait_iframe, locator_shadowdomhost), b_recursive=True)

def closepopup_queueadd_eventfiring(webdriver: utils_seleniumxp.eventfiring_addon.EventFiringWebDriverExtended, locator_click: utils_seleniumxp.SeleniumLocator, wait_click: float, check_click: bool = False, locator_iframe: utils_seleniumxp.SeleniumLocator = None, wait_iframe: float = 1, locator_shadowdomhost: utils_seleniumxp.SeleniumLocator = None) -> bool:
    return webdriver._dispatch(None, (), "_closepopup_queueadd", (locator_click, wait_click, check_click, locator_iframe, wait_iframe, locator_shadowdomhost), b_recursive=True)

def closepopup_queueprocessing_eventfiring(webdriver: utils_seleniumxp.eventfiring_addon.EventFiringWebDriverExtended, firstonly: bool = True) -> bool:
    return webdriver._dispatch("closepopuphandler", ("queueprocessing", webdriver._driver), "_closepopup_queueprocessing", (firstonly,), b_recursive=True)

# direct settattr instead of mixin-object but avoid name conflict
if not utils_seleniumxp.mixinactive:
    setattr(utils_seleniumxp.eventfiring_addon.EventFiringWebDriverExtended, "closepopup", closepopup_eventfiring)
    setattr(utils_seleniumxp.eventfiring_addon.EventFiringWebDriverExtended, "closepopup_queueadd", closepopup_queueadd_eventfiring)
    setattr(utils_seleniumxp.eventfiring_addon.EventFiringWebDriverExtended, "closepopup_queueprocessing", closepopup_queueprocessing_eventfiring)
# shadow routines to overcome recursion issue, inherited by EventFiringWebDriverExtended_Mixin
setattr(utils_seleniumxp.eventfiring_addon.EventFiringWebDriverExtended, "_closepopup", closepopup)
setattr(utils_seleniumxp.eventfiring_addon.EventFiringWebDriverExtended, "_closepopup_queueadd", closepopup_queueadd)
setattr(utils_seleniumxp.eventfiring_addon.EventFiringWebDriverExtended, "_closepopup_queueprocessing", closepopup_queueprocessing)


# close new windows opened automatically f. e. by downloads

# close new windows opened by automatic downloads, ...
# note: transfer value for parameter keepwindows as list even if a single handle !!!
def closewindows(webdriver: utils_seleniumxp._RemoteWebDriver, keepwindows: list):
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

# direct settattr instead of mixin-object but avoid name conflict
if not utils_seleniumxp.mixinactive:
    setattr(utils_seleniumxp._RemoteWebDriver, "closewindows", closewindows)


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

    timeoutdocrs = False
    try:
        utils_seleniumxp.WebDriverWait(webdriver, timeout).until(lambda webdriver: webdriver.execute_script('return document.readyState') == 'complete')
    except utils_seleniumxp.WebDriverExceptions.TimeoutException:
        timeoutdocrs = True

    while (time.time() < starttime + min_wait):
        time.sleep(0.1)

    return timeoutscript or timeoutdocrs

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

    wait4AJAX(webdriver)
    HTMLprev = ""
    starttime = time.time()
    while (HTMLprev != webdriver.page_source and (time.time() < starttime + max_wait)):
        HTMLprev = webdriver.page_source
        time.sleep(wait)

    return HTMLprev == webdriver.page_source

# direct setattr instead of mixin-object but avoid name conflict
if not utils_seleniumxp.mixinactive:
    setattr(utils_seleniumxp._RemoteWebDriver, "wait4AJAX", wait4AJAX)
    setattr(utils_seleniumxp._RemoteWebDriver, "wait4HTMLstable", wait4HTMLstable)


# extended wait for page load - source from ObeyTheTestingGoat
@contextlib.contextmanager
def wait_for_page_load(webdriver: utils_seleniumxp._RemoteWebDriver, timeout=10):
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
        webdriver (utils_seleniumxp._RemoteWebDriver): webdriiver
        timeout (int, optional): timeout. Defaults to 10.
    """
    old_page = webdriver.find_element(utils_seleniumxp.By.TAG_NAME, 'html')
    yield
    utils_seleniumxp.WebDriverWait(webdriver, timeout).until(utils_seleniumxp.ExpectedConditions.staleness_of(old_page))

# direct setattr instead of mixin-object but avoid name conflict
if not utils_seleniumxp.mixinactive:
    setattr(utils_seleniumxp._RemoteWebDriver, "wait_for_page_load", wait_for_page_load)
