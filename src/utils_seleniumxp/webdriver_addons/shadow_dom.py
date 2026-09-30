# Selenium webdriver utilities - XP version
# webdriver class - additional functionalities
# implementation shadow DOM access

"""
module with webdriver class extensions

submodule for shadow DOM access
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
# ruff: noqa: B010, E305, E501, PLR0914, PLR0917, PLR1702, PLR5501, PLW0717, RUF105, SIM102
#
# disable mypy errors
# mypy: disable-error-code = "no-any-return, attr-defined"

# fmt: off



# TODO Dev:
# - n. a.

# TODO Test:
# - n. a.



from collections.abc import Callable

import cssify

import utils_seleniumxp


# find elements in shadowDOM

# Note:
# - remember to escape quotes in CSS selectors
# - when integrating into event firing webdriver watch out due to recursive call like for closepopup
# - *_simple functions/methods are stubs for overhauled old logic

# utility function to cssify locator
def _prepare_selector(locator: utils_seleniumxp.SeleniumLocator) -> str:

    if locator.by == utils_seleniumxp.By.XPATH:
        return cssify.cssify(locator.value)
    elif locator.by == utils_seleniumxp.By.CSS_SELECTOR:
        return locator.value
    else:
        err_msg = "Only CSS selector allowed together with element in shadowDOM."
        raise utils_seleniumxp.ErrorUtilsSelenium(err_msg)

# find shadowDOM root (old/simple version)
def find_root_shadowdom_simple(
    webdriver: utils_seleniumxp._RemoteWebDriver,
    by: utils_seleniumxp.By,
    value: str
) -> utils_seleniumxp._ShadowRoot | None:
    """
    find_root_shadowdom_simple - find shadowDOM root

    Args:
        webdriver (utils_seleniumxp._RemoteWebDriver): browser
        by (utils_seleniumxp.By): locator type of element hosting shadowDOM root
        value (str): locator value of element hosting shadowDOM root

    Returns:
        Optional[utils_seleniumxp._WebElement]: shadowDOM root if found
    """

    shadowroot = None
    if webdriver.is_present(by, value):
        shadowhost = webdriver.find_element(by, value)
        try:
            # shadowroot = webdriver.execute_script("return arguments[0].shadowRoot", shadowhost)
            shadowroot = shadowhost.shadow_root
        except Exception:
            shadowroot = None

    return shadowroot

# find shadowDOM root with support for nested shadowDOM
def find_root_shadowdom(
    webdriver: utils_seleniumxp._RemoteWebDriver,
    locator_list: utils_seleniumxp.SeleniumLocator | list[utils_seleniumxp.SeleniumLocator],
    loggercall: Callable | None = None,
    raise_exception: bool = False,
    debug: bool = False
) -> utils_seleniumxp._ShadowRoot | None:
    """
    find_root_shadowdom - find shadowDOM root with support for nested shadowDOM

    Args:
        webdriver (utils_seleniumxp._RemoteWebDriver): browser
        locator_list: (Union[utils_seleniumxp.SeleniumLocator, list[utils_seleniumxp.SeleniumLocator]], optional): locator list to shadowDOM host. Defaults to None.
        loggercall: (Callable, optional) = log function for error. Defaults to None.
        raise_exception: (bool): flag to raise exception in case of any error in shadowDOM evaluation. Defaults to False.
        debug (bool): flag for debug mode to process every nesting level in shadowDOM separately. Defaults to False.

    Returns:
        Optional[utils_seleniumxp._WebElement]: shadowDOM root if found
    """

    def _execute_find_shadowroot(
        webdriver: utils_seleniumxp._RemoteWebDriver,
        script: str,
        scriptparam: object,
        err_msg: str,
        loggercall: Callable | None = None,
        raise_exception: bool = False
    ) -> utils_seleniumxp._ShadowRoot | None:

        try:
            shadowroot = webdriver.execute_script(script, scriptparam)
        except Exception:
            shadowroot = None
        if shadowroot is None:
            if loggercall is not None:
                loggercall(err_msg)
            if raise_exception:
                raise utils_seleniumxp.ErrorUtilsSelenium(err_msg)
        return shadowroot

    if not isinstance(locator_list, list):
        locator_list = [locator_list]
    if len(locator_list) >= 1:
        # evaluate first locator - use optimized check for presence
        shadowroot = None
        shadowhost = locator_list[0]
        if webdriver.is_present(*shadowhost):
            shadowroot = _execute_find_shadowroot(
                webdriver,
                "return arguments[0].shadowRoot",
                webdriver.find_element(*shadowhost),
                f"Locator {shadowhost} is not a valid unique locator to a shadowDOM host.",
                loggercall,
                raise_exception
            )
        if shadowroot is not None:
            # evaluate rest of locator list
            queryselector = ""
            for i in range(1, len(locator_list)):
                if debug:
                    shadowroot = _execute_find_shadowroot(
                        webdriver,
                        f"return arguments[0].querySelector('{_prepare_selector(locator_list[i])}').shadowRoot",
                        shadowroot,
                        f"Locator {locator_list[i]} is not a valid unique locator to a shadowDOM host.",
                        loggercall,
                        raise_exception
                    )
                else:
                    queryselector = queryselector + ".querySelector('" + _prepare_selector(locator_list[i]) + "').shadowRoot"
            if not debug:
                shadowroot = _execute_find_shadowroot(
                    webdriver,
                    f"return arguments[0]{queryselector}",
                    shadowroot,
                    f"Locatorlist {locator_list} contains invalid/not unique locator to a shadowDOM host.",
                    loggercall,
                    raise_exception
                )
        return shadowroot

    err_msg = f"Locatorlist {locator_list} is empty."
    if loggercall is not None:
        loggercall(err_msg)
    if raise_exception:
        raise utils_seleniumxp.ErrorUtilsSelenium(err_msg)

    return None

# find elements in shadowDOM (old/simple version)
def find_elements_shadowdom_simple(
    webdriver: utils_seleniumxp._RemoteWebDriver,
    by: utils_seleniumxp.By,
    value: str,
    shadowroot: utils_seleniumxp._ShadowRoot | utils_seleniumxp._WebElement
) -> list[utils_seleniumxp._WebElement] | None:
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

# find elements in shadowDOM with support for nested shadowDOM
def find_elements_shadowdom(
    webdriver: utils_seleniumxp._RemoteWebDriver,
    locator_list: utils_seleniumxp.SeleniumLocator | list[utils_seleniumxp.SeleniumLocator],
    shadowroot: utils_seleniumxp._ShadowRoot | utils_seleniumxp._WebElement | None = None
) -> list[utils_seleniumxp._WebElement] | None:
    """
    find_elements_shadowdom - find elements in shadowDOM with support for nested shadowDOM and root element as optional parameter

    Note: every item in the locator list must be a locator to a host of another shadowDOM root.
    The routine also accepts the shadowhost element and derives the shadowroot automatically.

    Args:
        webdriver (utils_seleniumxp._RemoteWebDriver): webdriver
        locator_list (list[utils_seleniumxp.SeleniumLocator]): locator list
        shadowroot (Union[utils_seleniumxp._ShadowRoot, utils_seleniumxp._WebElement]], optional): shadowDOM root. Defaults to None.

    Returns:
        Optional[list[utils_seleniumxp._WebElement]]: list of webelements in shadowDOM if found
    """

    if not isinstance(locator_list, list):
        locator_list = [locator_list]
    if len(locator_list) > 1 or shadowroot is not None:
        queryselector = ""
        for i in range(0, len(locator_list) - 1):
            queryselector = queryselector + ".querySelector('" + _prepare_selector(locator_list[i]) + "').shadowRoot"
        queryselector = queryselector + ".querySelectorAll('" + _prepare_selector(locator_list[-1]) + "')"
        if shadowroot is not None:
            if shadowroot.__class__.__name__ != "ShadowRoot":
                # overcome issue that shadowDOM host but not root is provided
                # try to treat shadowroot as host to derive correct root
                try:
                    shadowroot = webdriver.execute_script("return arguments[0].shadowRoot", shadowroot)
                except Exception:
                    shadowroot = None
                if shadowroot is None:
                    err_msg = "Provided webelement is neither a ShadowRoot nor a ShadowHost."
                    raise utils_seleniumxp.ErrorUtilsSelenium(err_msg)
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

# find element in shadowDOM (old/simple version)
def find_element_shadowdom_simple(
    webdriver: utils_seleniumxp._RemoteWebDriver,
    by: utils_seleniumxp.By,
    value: str,
    shadowroot: utils_seleniumxp._ShadowRoot | utils_seleniumxp._WebElement
) -> utils_seleniumxp._WebElement | None:
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

# find element in shadowDOM with support for nested shadowDOM and root element as optional parameter
def find_element_shadowdom(
    webdriver: utils_seleniumxp._RemoteWebDriver,
    locator_list: utils_seleniumxp.SeleniumLocator | list[utils_seleniumxp.SeleniumLocator],
    shadowroot: utils_seleniumxp._ShadowRoot | utils_seleniumxp._WebElement | None = None
) -> utils_seleniumxp._WebElement | None:
    """
    find_element_shadowdom - find element in shadowDOM with support for nested shadowDOM

    Note: every item in the locator list must be a locator to a host of another shadowDOM root.

    Args:
        webdriver (utils_seleniumxp._RemoteWebDriver): webdriver
        locator_list (list[utils_seleniumxp.SeleniumLocator]): locator list
        shadowroot (Union[utils_seleniumxp._ShadowRoot, utils_seleniumxp._WebElement]], optional): shadowDOM root. Defaults to None.

    Returns:
        Optional[utils_seleniumxp._WebElement]: webelement in shadowDOM if found
    """

    webelts = find_elements_shadowdom(webdriver, locator_list, shadowroot)
    if webelts is not None and webelts != []:
        if len(webelts) == 1:
            return webelts[0]
        else:
            err_msg = "Multiple elements for descriptor in shadowDOM"
            raise utils_seleniumxp.ErrorUtilsSelenium(err_msg)
    else:
        return None

# check if element present in shadowDOM with support for nested shadowDOM
def is_present_shadowdom(
    webdriver: utils_seleniumxp._RemoteWebDriver,
    locator_list: utils_seleniumxp.SeleniumLocator | list[utils_seleniumxp.SeleniumLocator],
    shadowroot: utils_seleniumxp._ShadowRoot | utils_seleniumxp._WebElement | None = None
) -> bool:
    """
    is_present_shadowdom - check if element is present in shadowDOM

    Note: every item in the locator list must be a locator to a host of another shadowDOM root.

    Args:
        webdriver (utils_seleniumxp._RemoteWebDriver): webdriver
        locator_list (list[utils_seleniumxp.SeleniumLocator]): locator list
        shadowroot (Union[utils_seleniumxp._ShadowRoot, utils_seleniumxp._WebElement]], optional): shadowDOM root. Defaults to None.

    Returns:
        bool: flag if element is present or not
    """

    webelts = find_elements_shadowdom(webdriver, locator_list, shadowroot)
    return webelts is not None and webelts != []

# direct settattr instead of mixin-object but avoid name conflict
# (not relevant for EventFiringWebDriver)
if not utils_seleniumxp.mixinactive:
    setattr(utils_seleniumxp._RemoteWebDriver, "find_root_shadowdom_simple", find_root_shadowdom_simple)
    setattr(utils_seleniumxp._RemoteWebDriver, "find_root_shadowdom", find_root_shadowdom)
    setattr(utils_seleniumxp._RemoteWebDriver, "find_elements_shadowdom_simple", find_elements_shadowdom_simple)
    setattr(utils_seleniumxp._RemoteWebDriver, "find_elements_shadowdom", find_elements_shadowdom)
    setattr(utils_seleniumxp._RemoteWebDriver, "find_element_shadowdom_simple", find_element_shadowdom_simple)
    setattr(utils_seleniumxp._RemoteWebDriver, "find_element_shadowdom", find_element_shadowdom)
    setattr(utils_seleniumxp._RemoteWebDriver, "is_present_shadowdom", is_present_shadowdom)
    setattr(utils_seleniumxp._RemoteWebDriver, "is_element_present_shadowdom", is_present_shadowdom)
