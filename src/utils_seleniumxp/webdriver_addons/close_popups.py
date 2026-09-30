# Selenium webdriver utilities - XP version
# webdriver class - additional functionalities
# implementation close popups

"""
module with webdriver class extensions

submodule for close popups
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



import time

import collections

import cssify

import utils_seleniumxp


# close popups - processing via a queue to speed up subsequent tries to close popups via html parsing
#
# note: when using shadowDOM ist seems CSS is mandatory at least for end nodes
# see https://github.com/SeleniumHQ/selenium/issues/4971

# close popup using parsel for XPath and CSS
def closepopup(
        webdriver: utils_seleniumxp._RemoteWebDriver,
        locator_click: utils_seleniumxp.SeleniumLocator,
        wait_click: float = 0.1,
        check_click: bool = False,
        locator_iframe: utils_seleniumxp.SeleniumLocator | None = None,
        wait_iframe: float = 1,
        locator_shadowdomhost: utils_seleniumxp.SeleniumLocator | list[utils_seleniumxp.SeleniumLocator] | None = None
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
        locator_shadowdomhost (Union[utils_seleniumxp.SeleniumLocator, list[utils_seleniumxp.SeleniumLocator]], optional): locator list to shadowDOM host. Defaults to None.

    Returns:
        bool: flag if a matching popup was found and closed
    """

    closepopup_queueadd(webdriver, locator_click, wait_click, check_click, locator_iframe, wait_iframe, locator_shadowdomhost)
    return closepopup_queueprocessing(webdriver)

# closepopup - queue request
def closepopup_queueadd(
        webdriver: utils_seleniumxp._RemoteWebDriver,
        locator_click: utils_seleniumxp.SeleniumLocator,
        wait_click: float = 0.1,
        check_click: bool = False,
        locator_iframe: utils_seleniumxp.SeleniumLocator | None = None,
        wait_iframe: float = 1,
        locator_shadowdomhost: utils_seleniumxp.SeleniumLocator | list[utils_seleniumxp.SeleniumLocator] | None = None
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
        locator_shadowdomhost (Union[utils_seleniumxp.SeleniumLocator, list[utils_seleniumxp.SeleniumLocator]], optional): locator list to shadowDOM host. Defaults to None.
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

            locator_click: utils_seleniumxp.SeleniumLocator = queueentry["locator_click"]
            wait_click: float = queueentry["wait_click"]
            check_click: bool = queueentry["check_click"]
            locator_iframe: utils_seleniumxp.SeleniumLocator | None = queueentry["locator_iframe"]
            wait_iframe: float = queueentry["wait_iframe"]
            locator_shadowdomhost: utils_seleniumxp.SeleniumLocator | list[utils_seleniumxp.SeleniumLocator] | None = queueentry["locator_shadowdomhost"]

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
                        # shadowDOM cannot be evaluated via parsel / lxml but first node always not in shadowDOM
                        if (utils_seleniumxp.locatorutils.check_locator(locator_click, [utils_seleniumxp.By.XPATH, utils_seleniumxp.By.CSS_SELECTOR]) or
                            utils_seleniumxp.locatorutils.check_locatorlist(locator_shadowdomhost, [utils_seleniumxp.By.XPATH, utils_seleniumxp.By.CSS_SELECTOR])
                        ):
                            parsedhtml = utils_seleniumxp.locatorutils.parselSelectorExtension(text=webdriver.page_source)
                    elif len(frames) > 1:
                        if hasattr(webdriver, "closepopup_logger"):
                            webdriver.closepopup_logger.info(f"FRAME not unique\t{webdriver.current_url}\t({locator_click})\t({locator_iframe})\t({locator_shadowdomhost})")
                        continue

                # find close popup (considering also shadowDOM webelements)
                if locator_shadowdomhost is not None:
                    # if utils_seleniumxp.locatorutils.check_locatorlist(locator_shadowdomhost, [utils_seleniumxp.By.XPATH, utils_seleniumxp.By.CSS_SELECTOR]):
                    #     shadowhosts = parsedhtml.css_or_xpath(locator_shadowdomhost).getall()
                    #     # re-parse once, sometimes timing problem (probably caused by opening shadowDOM and loading?)
                    #     if len(shadowhosts) == 0:
                    #         parsedhtml = utils_seleniumxp.locatorutils.parselSelectorExtension(text=webdriver.page_source)
                    #         shadowhosts = parsedhtml.css_or_xpath(locator_shadowdomhost).getall()
                    # else:
                    #     shadowhosts = webdriver.find_elements(*locator_shadowdomhost)
                    # webelts = []
                    # if len(shadowhosts) == 0:
                    #     if hasattr(webdriver, "closepopup_logger"):
                    #         webdriver.closepopup_logger.info(f"ShadowDOM host not found\t{webdriver.current_url}\t({locator_click})\t({locator_iframe})\t({locator_shadowdomhost})")
                    #     continue
                    # elif len(shadowhosts) == 1:
                    #     # shadowhost = webdriver.find_element(*locator_shadowdomhost)
                    #     # shadowroot = webdriver.execute_script("return arguments[0].shadowRoot", shadowhost)
                    #     shadowroot = webdriver.find_root_shadowdom_simple(*locator_shadowdomhost)
                    #     if shadowroot is not None:
                    #         webelts = shadowroot.find_elements(*locator_click)
                    # else:
                    #     if hasattr(webdriver, "closepopup_logger"):
                    #         webdriver.closepopup_logger.info(f"ShadowDOM host not unique\t{webdriver.current_url}\t({locator_click})\t({locator_iframe})\t({locator_shadowdomhost})")
                    #     continue
                    shadowroot = webdriver.find_root_shadowdom(locator_shadowdomhost, webdriver.closepopup_logger.info if hasattr(webdriver, "closepopup_logger") else None, raise_exception=False)
                    if shadowroot is not None:
                        webelts = shadowroot.find_elements(*locator_click)
                    else:
                        if hasattr(webdriver, "closepopup_logger"):
                            webdriver.closepopup_logger.info(f"ShadowDOM root not found \t{webdriver.current_url}\t({locator_click})\t({locator_iframe})\t({locator_shadowdomhost})")
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
                            # if webelt.is_displayed() and not webelt.is_overlapped():  # type: ignore[union-attr]
                            if webelt.is_displayed():
                                countwindows = len(webdriver.window_handles)
                                keepwindows = webdriver.window_handles
                                webelt.click()
                                if wait_click > 0:
                                    time.sleep(wait_click)
                                if len(webdriver.window_handles) > countwindows:
                                    utils_seleniumxp.closewindows(webdriver, keepwindows)
                                closedpopup = True
                                closedpopup_thisrun = True
                                if hasattr(webdriver, "closepopup_logger"):
                                    webdriver.closepopup_logger.info(f"found target\t{webdriver.current_url}\t({locator_click})\t({locator_iframe})\t({locator_shadowdomhost})")
                                break
                        except utils_seleniumxp.WebDriverExceptions.StaleElementReferenceException:
                            pass   # simple rerun
                        except utils_seleniumxp.WebDriverExceptions.ElementClickInterceptedException:
                            pass  # simple rerun
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

def closepopup_eventfiring(
    webdriver: utils_seleniumxp.eventfiring_addon.EventFiringWebDriverExtended,
    locator_click: utils_seleniumxp.SeleniumLocator,
    wait_click: float,
    check_click: bool = False,
    locator_iframe: utils_seleniumxp.SeleniumLocator | None = None,
    wait_iframe: float = 1,
    locator_shadowdomhost: utils_seleniumxp.SeleniumLocator | list[utils_seleniumxp.SeleniumLocator] | None = None
) -> bool:
    """
    closepopup_eventfiring - closepopup for eventfiring webdriver, required to avoid endless recurion loop)
    """
    return webdriver._dispatch("closepopuphandler", ("simpleclose", webdriver._driver), "_closepopup", (locator_click, wait_click, check_click, locator_iframe, wait_iframe, locator_shadowdomhost), b_recursive=True)

def closepopup_queueadd_eventfiring(
    webdriver: utils_seleniumxp.eventfiring_addon.EventFiringWebDriverExtended,
    locator_click: utils_seleniumxp.SeleniumLocator,
    wait_click: float,
    check_click: bool = False,
    locator_iframe: utils_seleniumxp.SeleniumLocator | None = None,
    wait_iframe: float = 1,
    locator_shadowdomhost: utils_seleniumxp.SeleniumLocator | list[utils_seleniumxp.SeleniumLocator] | None = None
) -> bool:
    """
    closepopup_queueadd_eventfiring - closepopup_queueadd for eventfiring webdriver, required to avoid endless recurion loop)
    """
    return webdriver._dispatch(None, (), "_closepopup_queueadd", (locator_click, wait_click, check_click, locator_iframe, wait_iframe, locator_shadowdomhost), b_recursive=True)

def closepopup_queueprocessing_eventfiring(
    webdriver: utils_seleniumxp.eventfiring_addon.EventFiringWebDriverExtended,
    firstonly: bool = True
) -> bool:
    """
    closepopup_queueprocessing_eventfiring - closepopup_queueprocessing for eventfiring webdriver, required to avoid endless recurion loop)
    """
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
