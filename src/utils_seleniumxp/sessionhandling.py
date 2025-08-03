# Selenium webdriver utilities - XP version
# routines for starting / configuring browser sessions, currently full support for Chrome and Firefox only

"""
Module with session handling functions

Session handling functions include:
- start a webdriver session with a new driver including logging
- connect a webdriver session to a running via debug port (Chrome only).
- browser setting bundling functions for a) direct download b) disabling notifications
  c) optimized scraping

Currently full support is implemented for Chrome and Firefox only.
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
# ruff: noqa: B006, B008, B010, E501, PLC0415, PLR0914, PLR0917, PLR1702, PLR2004, RUF022, S110, S113, SIM102
#
# disable mypy errors
# mypy: disable-error-code = "attr-defined, arg-type, call-overload, no-any-return"

# fmt: off



# TODO Dev:
# - decorator to check brwoser type for various functions to simplify code ?
# - use user profiles ?
# - additional parameters in INI file Selenium.ini
#   - implicitlywait
#   - flag for stealth mode ?
#   - flag for optimized scraping mode ?
#   - combine with a wrapper for config
#     https://github.com/MikeFez/BrowserWrapper/blob/main/BrowserWrapper/browserwrapper.py ?
# - include/activate webdriver management ?
# - Firefox improvements (but worth the effort as Chrome is faster anyway and currently causes problems?)
#   - Firefox eventfiring webdriver: problem with hanging Firefox and hanging processes when checked last time
#   - re-connect mechanism as for Chrome, seems to be supported from Selenium4 onwards
#     feature calling seems to be similar to Chrome but it is unclear how to control  marionette port (as the
#     standard built-in Firefox automation driver) and Geckodriver supporting the Webdriver protocol
#     for the Selenium side and if relevant
#     -> advantage unclear, Chrome feature used to start browser session with VBA and hand it over
#        but Firefox does not work with SeleniumBasic COM-wrapper anymore
#     https://wiki.mozilla.org/Firefox/CommandLineOptions
#     https://stackoverflow.com/questions/43272919/difference-between-webdriver-firefox-marionette-webdriver-gecko-driver
#     https://stackoverflow.com/questions/57579761/is-there-any-way-to-change-the-webdrivers-port
#     https://stackoverflow.com/questions/68340118/how-can-i-attach-firefoxdriver-to-a-running-instance-of-firefox
#     https://stackoverflow.com/questions/72331816/how-to-connect-to-an-existing-firefox-instance-using-seleniumpython

# TODO Test:
# - n. a.



from typing import Any, Callable, Optional, Union

import os
# switch to pathlib postponed as os is required
# import pathlib
import tempfile
import configparser
import logging
import inspect
import atexit
import contextlib
import psutil
import signal

import requests

from stealthenium import stealth

import utils_seleniumxp.eventfiring_addon
import utils_mystuff as Utils



# block direct calling
# __all__ = []
__all__ = [
    'initWebDriver', 'init_webdriver',
    'directdownload',
    'disablenotifications',
    'connectChrome', 'connect_chrome',
    'checkDebugport', 'check_debugport'
]



# supported browsers
supported_browsers = {"chrome": ("chrome.exe", "chromedriver.exe"), "firefox": ("firefox.exe", "geckodriver.exe")}

# switch stealth mode
stealthmode_default = False
# switch optimized scraping
optimizedscraping_default = False



# initialize selenium driver including starting new browser instance
def init_webdriver(
    browser: Optional[str] = None,
    inifile: Optional[str] = None,
    inisection: str = "DEFAULT",
    settings: list[Union[(tuple[str], tuple[str, list[Any]])]] = [("disablenotifications",), ("directdownload", [tempfile.gettempdir()])],
    debugport: int = 0,
    implicitlywait: int = 10,
    maxpageload: int = 30,
    mixin: bool = utils_seleniumxp.mixinactive,
    eventlistener: Optional[utils_seleniumxp.eventfiring_addon.AbstractEventListenerExtended] = None,
    stealthmode: bool = stealthmode_default,
    optimizedscraping: bool = optimizedscraping_default,
    URL: str = "about:blank",
    alt_cls_webdriverwrapper: Optional[type[utils_seleniumxp._RemoteWebDriver]] = None,
    alt_cls_options: Union[type[utils_seleniumxp.WebDriver.ChromeOptions], type[utils_seleniumxp.WebDriver.FirefoxOptions], None] = None
) -> utils_seleniumxp._RemoteWebDriver:
    """
    init_webdriver - initialize Selenium webdriver session

    INI file:
    The ini file provides a possibility to define profiles with extensions to be loaded and paths
    to the webdriver binary and extension files. A profile section defines the browser, the driver path,
    the extension path and the extensions to be loaded. Config file interpolation might be used for paths.
    Per driver a driver specific section is required defining at least the file for the extensions.
    Currently settings beyond paths and extensions are not supported.

    settings:
    settings is provided as a list of callables. The callables must return a browser-specific settings data object.
    Refer to functions 'directdownload', 'disablenotifications' and 'optimizedscraping' as example.

    alternative base class:
    To use special bases like undetected_chromedriver it is possible to provide an alternative
    browser class. Note that an alternative options class must be provided as well.

    Args:
        browser (Optional[str], optional): browser, read from INI file if not set. Defaults to None.
        inifile (Optional[str], optional): INI file. Defaults to None.
        inisection (str, optional): INI section to be evaluated. Defaults to "DEFAULT".
        settings (list[Union[, optional): Browser preference setting functions. Defaults to [("disablenotifications",), ("directdownload", [tempfile.gettempdir()])].
        debugport (int, optional): set debugport (currently Chrome only). Defaults to 0.
        implicitlywait (int, optional): implicit wait time. Defaults to 10.
        maxpageload (int, optional): max pageload time. Defaults to 20.
        mixin (bool, optional): flag to switch between mixin and setattr mode. Defaults to utils_seleniumxp.mixinactive.
        eventlistener (Optional[utils_seleniumxp.eventfiring_addon.AbstractEventListenerExtended], optional): eventlistener object to activate eventfiring mode. Defaults to None.
        stealthmode (bool, optional): flag to control selenium_stealth mode. Defaults to stealthmode_default.
        optimizedscraping (bool, optional): flag to control optimized settings for scraping (no pictures etc.). Defaults to optimizedscraping_default.
        URL (str, optional): start URL. Defaults to "about:blank".
        alt_cls_webdriverwrapper (Optional[utils_seleniumxp.WebDriver], optional): optional base webdriver class. Defaults to None.
        alt_cls_options (Union[utils_seleniumxp.WebDriver.ChromeOptions, utils_seleniumxp.WebDriver.FirefoxOptions, None], optional): optional browser options class. Defaults to None.

    Returns:
        utils_seleniumxp.WebDriver: webdriver object
    """

    # internal helper for session init routine

    def evaluate_prefsfunction(prefsfunction: Any) -> Union[dict, list[tuple[str, Any]]]:

        if type(prefsfunction) is tuple:
            if len(prefsfunction) == 1:
                prefsfunction = (prefsfunction[0], None)
        else:
            prefsfunction = (prefsfunction, None)
        try:
            if prefsfunction[1] is None:
                return globals()[prefsfunction[0]](browser)
            else:
                return globals()[prefsfunction[0]](browser, *prefsfunction[1])
        except Exception as exc_prefscfuntion_eval:
            err_msg = f"Browser preference set {prefsfunction[0]} not defined."
            raise utils_seleniumxp.ErrorUtilsSelenium(err_msg) from exc_prefscfuntion_eval

    def evaluate_extensionspath(evalfunc: Callable[[str], None], extensionspath: str) -> int:

        extensions_installed = 0
        if "extensions" in config[inisection]:
            extensions = config[inisection]["extensions"].split(", ")
            if len(extensions) > 0:
                if sessionstartlog is not None:
                    sessionstartlog.info("Add-Ons:")
                for extensionID in extensions:
                    # get-function used to enable fallback value
                    extensionfile = config[browser].get("extension_" + extensionID, fallback="")  # type: ignore[index]
                    if extensionfile != "":
                        extensionfile = os.path.join(extensionspath, extensionfile)
                        # extensionfile = pathlib.Path(extensionspath).joinpath(extensionfile)
                        # if extensionfile.is_file():
                        if os.path.isfile(extensionfile):
                            evalfunc(extensionfile)
                            if sessionstartlog is not None:
                                sessionstartlog.info(f"- '{extensionfile}' for '{extensionID}' found.")
                            extensions_installed += + 1
                        elif sessionstartlog is not None:
                            sessionstartlog.info(f"- File '{extensionfile}' for '{extensionID}' not found.")
                    elif sessionstartlog is not None:
                        sessionstartlog.info(f"- Extensionfile for '{extensionID}' not defined.")
        return extensions_installed

    # start ini processing

    regkey_AppPaths: str = "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\App Paths\\"

    # read config file (standard: seleniumpythonutils.ini)
    config, config_without_default = read_configfile(inifile)

    # activate sessionstart log
    sessionstartlog = set_log_sessionstart(config, inisection)
    if sessionstartlog is not None:
        sessionstartlog.info("----- start webdriver session -----")
        sessionstartlog.info("Parameters:")
        # get arg-values without reference to callable
        cframe = inspect.currentframe()
        args_info = inspect.getargvalues(cframe)
        # collecting args-values in a dictionary
        argsdict = {arg: args_info.locals.get(arg) for arg in args_info.args}
        # log args dictionary
        for key, value in argsdict.items():
            sessionstartlog.info(f"- {key}: {value}")

    # read browser
    if browser is None:
        browser = config[inisection]["browser"]
    # check browser
    if browser not in supported_browsers:
        err_msg = f"Browser '{browser}' not supported."
        raise utils_seleniumxp.ErrorUtilsSelenium(err_msg)

    browserbinarypath: Optional[str] = None
    driverpath: Optional[str] = None

    # check binaries from config (Windows only)
    if os.name == "nt":

        # check browser binary location (for portable installations - only windows)
        import winreg
        browserbinary: str = supported_browsers[browser][0]
        browserbinarypath = check_configpath(config, browser, "browserbinarypath", browserbinary, checkwd=False)
        if browserbinarypath is None or browserbinarypath == "":
            try:
                winreg.QueryValue(winreg.HKEY_LOCAL_MACHINE, regkey_AppPaths + browserbinary)
            except Exception as exc_winreg:
                err_msg = f"Browser '{browser}' not installed and no portable app path provided."
                raise utils_seleniumxp.ErrorUtilsSelenium(err_msg) from exc_winreg

        # use Selenium Manager as per default
        # if not config.getboolean(browser, "use_seleniummanager"):
        if not Utils.to_bool(config[browser]["use_seleniummanager"]):
            # check/set webdriver executable path
            driverbinary: str = supported_browsers[browser][1]
            driverpath = check_configpath(config_without_default, inisection, "driverpath", driverbinary, checkwd=False)
            if driverpath == "":
                driverpath = check_configpath(config, browser, "driverpath", driverbinary, checkwd=True)
            if driverpath == "":
                driverpath = check_usrpath(config, browser, "usrpath_suffix_driver")
            if driverpath is None or driverpath == "":
                err_msg = f"Driver {driverbinary} for Browser '{browser}' could not be found in path defined in config file or current working directory."
                raise utils_seleniumxp.ErrorUtilsSelenium(err_msg)
            else:
                # set PATH
                envpath = os.environ["PATH"]
                if driverpath not in envpath:
                    os.environ["PATH"] += os.pathsep + driverpath

    else:

        # browserbinarypath = check_configpath(config, browser, "", "browserbinarypath", checkwd=False)
        browserbinarypath = config[browser]["browserbinarypath"]

    # optimized scraping (bot detection prevention)
    if optimizedscraping and "optimizedscraping" not in settings:
        settings.append(("optimizedscraping",))

    # create browser options / profile object and set preferences
    if browser == "chrome":

        # set options object - some wrappers define own options class
        browsersettings = utils_seleniumxp.WebDriver.ChromeOptions() if alt_cls_options is None else alt_cls_options()

        # options / preferences
        prefsdict: dict = {}
        for prefsfunction in settings:
            prefs = evaluate_prefsfunction(prefsfunction)
            prefsdict = {**prefsdict, **prefs}  # type: ignore[dict-item]
        if len(prefsdict) > 0:
            browsersettings.add_experimental_option("prefs", prefsdict)
            if sessionstartlog is not None:
                sessionstartlog.info("Preferences / Options:")
                for key, value in prefsdict.items():
                    # log Chrome prefs
                    sessionstartlog.info(f"- {key}: {value}")

        # settings for Chrome
        browsersettings.add_argument("--disable-features=UserAgentClientHint,OptimizationGuideModelDownloading,OptimizationHintsFetching,OptimizationTargetPrediction,OptimizationHints")
        browsersettings.add_argument("--disable-search-engine-choice-screen")
        # settings in addition to stealth extension from stackoverflow
        # https://stackoverflow.com/questions/53039551/selenium-webdriver-modifying-navigator-webdriver-flag-to-prevent-selenium-detec
        # https://stackoverflow.com/questions/67341346/how-to-bypass-cloudflare-bot-protection-in-selenium
        if stealthmode:
            browsersettings.add_experimental_option("excludeSwitches", ["enable-automation"])
            browsersettings.add_experimental_option("useAutomationExtension", False)
            browsersettings.add_argument("--disable-blink-features=AutomationControlled")

        # remote debugging (currently only Chrome)
        if debugport != 0:
            browsersettings.add_argument(f"--remote-debugging-port={debugport}")

    elif browser == "firefox":

        # set options object - some wrappers define own options class
        browsersettings = utils_seleniumxp.WebDriver.FirefoxOptions() if alt_cls_options is None else alt_cls_options()

        # options / preferences
        if len(settings) > 0:
            if sessionstartlog is not None:
                sessionstartlog.info("Preferences / Options:")
            for prefsfunction in settings:
                prefs = evaluate_prefsfunction(prefsfunction)
                for pref in prefs:
                    browsersettings.set_preference(pref[0], pref[1])
                    # log FireFox prefs
                    if sessionstartlog is not None:
                        sessionstartlog.info(f"- {pref[0]}: {pref[1]}")

        # does not work anymore with Selenium 4.x
        # browsersettings.set_preference("xpinstall.signatures.required", False)   # for unsigned extensions

        # potentially switch to options.profile to be amended (Selenium 4)

        # settings for Firefox
        # settings in addition to stealth extension from stackoverflow (currently Chrome only)
        if stealthmode:
            pass

        # remote debugging (currently Chrome only)
        if debugport != 0:
            pass

    # set browser binary location in webdriver/browser profile
    if browserbinarypath is not None:
        browsersettings.binary_location = os.path.join(browserbinarypath, browserbinary)

    # install requested extensions
    # Selenium 3.x: not working properly with FireFox but no error message
    # Selenium 4.x: sub-routine evaluate as Chrome includes add-on in options but firefox requires webdriver start first
    extensionspath = check_configpath(config_without_default, inisection, "extensionspath")
    if extensionspath == "":
        extensionspath = check_configpath(config, browser, "extensionspath")
    if extensionspath == "":
        extensionspath = check_usrpath(config, browser, "usrpath_suffix_ext")
    if extensionspath == "":
        err_msg = f"Extensions for Browser '{browser}' could not be found in path defined in config file."
        raise utils_seleniumxp.ErrorUtilsSelenium(err_msg)

    # install requested extensions - Chrome
    if browser == "chrome" and extensionspath != "":
        extensions_installed = evaluate_extensionspath(
            browsersettings.add_extension, extensionspath
        )
        # fix according to https://github.com/SeleniumHQ/selenium/issues/15788
        if extensions_installed > 0:
            browsersettings.add_argument("--disable-features=DisableLoadExtensionCommandLineSwitch")

    # instantiate Selenium webdriver + browser, load blank page
    if browser == "chrome":
        cls_webdriver = utils_seleniumxp.WebDriver.Chrome
        if alt_cls_webdriverwrapper is not None:
            if (browser.upper() in [mro_cls.__module__.upper() for mro_cls in alt_cls_webdriverwrapper.__mro__]) or \
                ("selenium.webdriver.chrome.webdriver" in [mro_cls.__module__ for mro_cls in alt_cls_webdriverwrapper.__mro__]):
                cls_webdriver = alt_cls_webdriverwrapper
    elif browser == "firefox":
        cls_webdriver = utils_seleniumxp.WebDriver.Firefox
        if alt_cls_webdriverwrapper is not None:
            if (browser.upper() in [mro_cls.__module__.upper() for mro_cls in alt_cls_webdriverwrapper.__mro__]) or \
                ("selenium.webdriver.firefox.webdriver" in [mro_cls.__module__ for mro_cls in alt_cls_webdriverwrapper.__mro__]):
                cls_webdriver = alt_cls_webdriverwrapper
    if mixin or utils_seleniumxp.mixinactive:
        webdriver = utils_seleniumxp.webdriver_addon.WebDriverMixedin(cls_webdriver)(options=browsersettings)
    else:
        webdriver = utils_seleniumxp.webdriver_addon.WebDriver3rdPartyMixedin(cls_webdriver)(options=browsersettings)
    if eventlistener is not None:
        if mixin or utils_seleniumxp.mixinactive:
            webdriver = utils_seleniumxp.webdriver_addon.EventFiringWebDriverExtendedMixedin(webdriver, eventlistener)
        else:
            webdriver = utils_seleniumxp.eventfiring_addon.EventFiringWebDriverExtended(webdriver, eventlistener)
    webdriver.get("about:blank")

    # install requested extensions - Firefox
    if browser == "firefox" and extensionspath != "":
        extensions_installed = evaluate_extensionspath(
            webdriver.install_addon, extensionspath
        )

    # set implicitly wait if defined
    if implicitlywait != 0:
        webdriver.implicitly_wait(implicitlywait)

    # set maxpage load
    if maxpageload != 0:
        webdriver.set_page_load_timeout(maxpageload)

    # close browser windows from extensions
    if extensions_installed > 0:
        webdriver.wait4HTMLstable()
        if len(webdriver.window_handles) > 1:
            while len(webdriver.window_handles) > 1:
                webdriver.close()

    # activate stealth mode (so far only available for chrome)
    if stealthmode:
        # set full screen-size as anti-bot measure -> would require screen-size not to be changed by calling programm
        webdriver.maximize_window()
        # delete  navigator flag
        webdriver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => false})")
        # browser-specific stuff
        if browser == "chrome":
            webdriver.execute_cdp_cmd(
                "Page.addScriptToEvaluateOnNewDocument",
                {
                    "source": """
                        Object.defineProperty(navigator, 'webdriver', {get: () => undefined})
                            """
                }
            )
            # solve wrapping issue for EventFiringWebDriver
            webdriver_temp = webdriver.wrapped_driver if hasattr(webdriver, "wrapped_driver") else webdriver
            stealth(
                driver=webdriver_temp,
                user_agent="",
                languages=["en-US", "en", "de-DE", "de"],
                vendor="Google Inc.",
                platform="Win32",
                webgl_vendor="Intel Inc.",
                renderer="Intel Iris OpenGL Engine",
                fix_hairline=True,
                run_on_insecure_origins=False
            )

    # get URL
    if URL != "about:blank":
        webdriver.get(URL)

    # close log for session start
    close_log_sessionstart(sessionstartlog)

    # set logging for closing popups
    set_log_closepopup(webdriver, config, inisection)

    # make sure closepopup log is closed when application ends
    atexit.register(close_log_closepopup, webdriver)
    # make sure webdriver process is killed when application ends
    atexit.register(kill_driver_processes, browser, webdriver.service.process.pid)

    return webdriver

def initWebDriver(
    browser: Optional[str] = None,
    inifile: Optional[str] = None,
    inisection: str = "DEFAULT",
    settings: list[Union[(tuple[str], tuple[str, list[Any]])]] = [("disablenotifications",), ("directdownload", [tempfile.gettempdir()])],
    debugport: int = 0,
    implicitlywait: int = 10,
    maxpageload: int = 30,
    mixin: bool = utils_seleniumxp.mixinactive,
    eventlistener: Optional[utils_seleniumxp.eventfiring_addon.AbstractEventListenerExtended] = None,
    stealthmode: bool = stealthmode_default,
    optimizedscraping: bool = optimizedscraping_default,
    URL: str = "about:blank",
    alt_cls_webdriverwrapper: Optional[utils_seleniumxp._RemoteWebDriver] = None,
    alt_cls_options: Union[utils_seleniumxp.WebDriver.ChromeOptions, utils_seleniumxp.WebDriver.FirefoxOptions, None] = None
) -> utils_seleniumxp._RemoteWebDriver:
    """
    initWebDriver - initialize Selenium webdriver session

    INI file:
    The ini file provides a possibility to define profiles with extensions to be loaded and paths
    to the webdriver binary and extension files. A profile section defines the browser, the driver path,
    the extension path and the extensions to be loaded. Config file interpolation might be used for paths.
    Per driver a driver specific section is required defining at least the file for the extensions.
    Currently settings beyond paths and extensions are not supported.

    settings:
    settings is provided as a list of callables. The callables must return a browser-specific settings data object.
    Refer to functions 'directdownload', 'disablenotifications' and 'optimizedscraping' as example.

    alternative base class:
    To use special bases like undetected_chromedriver it is possible to provide an alternative
    browser class. Note that an alternative options class must be provided as well.

    Args:
        browser (Optional[str], optional): browser, read from INI file if not set. Defaults to None.
        inifile (Optional[str], optional): INI file. Defaults to None.
        inisection (str, optional): INI section to be evaluated. Defaults to "DEFAULT".
        settings (list[Union[, optional): Browser preference setting functions. Defaults to [("disablenotifications",), ("directdownload", [tempfile.gettempdir()])].
        debugport (int, optional): set debugport (currently Chrome only). Defaults to 0.
        implicitlywait (int, optional): implicit wait time. Defaults to 10.
        maxpageload (int, optional): max pageload time. Defaults to 20.
        mixin (bool, optional): flag to switch between mixin and setattr mode. Defaults to utils_seleniumxp.mixinactive.
        eventlistener (Optional[utils_seleniumxp.eventfiring_addon.AbstractEventListenerExtended], optional): eventlistener object to activate eventfiring mode. Defaults to None.
        stealthmode (bool, optional): flag to control selenium_stealth mode. Defaults to stealthmode_default.
        optimizedscraping (bool, optional): flag to control optimized settings for scraping (no pictures etc.). Defaults to optimizedscraping_default.
        URL (str, optional): start URL. Defaults to "about:blank".
        alt_cls_webdriverwrapper (Optional[utils_seleniumxp.WebDriver], optional): optional base webdriver class. Defaults to None.
        alt_cls_options (Union[utils_seleniumxp.WebDriver.ChromeOptions, utils_seleniumxp.WebDriver.FirefoxOptions, None], optional): optional browser options class. Defaults to None.

    Returns:
        utils_seleniumxp.WebDriver: webdriver object
    """
    return init_webdriver(
        browser, inifile, inisection, settings, debugport,
        implicitlywait, maxpageload, mixin, eventlistener,
        stealthmode, optimizedscraping, URL,
        alt_cls_webdriverwrapper, alt_cls_options
    )


# initialize selenium driver - check existing Chrome browser instance before connecting
def check_debugport(debugport: int) -> bool:
    """
    check_debugport - check port if activated as debugport

    Args:
        debugport (int): port number

    Returns:
        bool: flag if port connects to a browser
    """

    checkDbgPortOK = False
    try:
        response = requests.get("http://localhost:" + str(debugport))
    except Exception:
        return False

    checkDbgPortOK = ((response.status_code == 200) and (response.reason == "OK"))

    return checkDbgPortOK

def checkDebugport(debugport: int) -> bool:
    """
    checkDebugport - check port if activated as debugport

    Args:
        debugport (int): port number

    Returns:
        bool: flag if port connects to a browser
    """
    return check_debugport(debugport)


# initialize selenium driver - connect to existing Chrome browser instance
# https://cosmocode.io/how-to-connect-selenium-to-an-existing-browser-that-was-opened-manually/
def connect_chrome(
    debugport: int,
    inifile: Optional[str] = None,
    inisection: str = "DEFAULT",
    mixin: bool = utils_seleniumxp.mixinactive,
    eventlistener: Optional[utils_seleniumxp.AbstractEventListener] = None,
    URL: str = "about:blank"
) -> Optional[utils_seleniumxp._RemoteWebDriver]:
    """
    connect_chrome - connect to Chrome instance via debugport

    Args:
        debugport (int): assumed debug port of Chrome instance
        inifile (Optional[str], optional): INI file. Defaults to None.
        inisection (str, optional): INI section to be evaluated. Defaults to "DEFAULT".
        mixin (bool, optional): flag to switch between mixin and setattr mode. Defaults to utils_seleniumxp.mixinactive.
        eventlistener (Optional[utils_seleniumxp.eventfiring_addon.AbstractEventListenerExtended], optional): eventlistener object to activate eventfiring mode. Defaults to None.
        URL (str, optional): start URL. Defaults to "about:blank".

    Returns:
        utils_seleniumxp.WebDriver: webdriver object
    """

    # check if debugport active with browser instance
    if not check_debugport(debugport):
        return None

    browser = "chrome"

    # read config file (standard: selenium.ini)
    config, config_without_default = read_configfile(inifile)

    driverpath: Optional[str] = None

    # check binaries from config (Windows only)
    if os.name == "nt":

        # use Selenium Manager as per default
        # if not config.getboolean(browser, "use_seleniummanager"):
        if not Utils.to_bool(config[browser]["use_seleniummanager"]):
            # check/set webdriver executable path
            driverbinary: str = supported_browsers[browser][1]
            driverpath = check_configpath(config_without_default, inisection, "driverpath", driverbinary, checkwd=False)
            if driverpath == "":
                driverpath = check_configpath(config, browser, "driverpath", driverbinary, checkwd=True)
            if driverpath == "":
                driverpath = check_usrpath(config, browser, "usrpath_suffix_driver")
            if driverpath == "":
                err_msg = f"Driver {driverbinary} for Browser '{browser}' could not be found in path defined in config file or current working directory."
                raise utils_seleniumxp.ErrorUtilsSelenium(err_msg)
            else:
                # set PATH
                envpath = os.environ["PATH"]
                if driverpath not in envpath:  # type: ignore[operator]
                    os.environ["PATH"] += os.pathsep + driverpath  # type: ignore[operator]

    # create browser options / profile object and set preferences
    browsersettings = utils_seleniumxp.WebDriver.ChromeOptions()
    # connect to existing browser instance via debug-port (chrome only)
    browsersettings.add_experimental_option("debuggerAddress", f"localhost:{debugport}")

    # instantiate Selenium webdriver, load blank page
    if mixin or utils_seleniumxp.mixinactive:
        webdriver = utils_seleniumxp.webdriver_addon.WebDriverMixedin(utils_seleniumxp.WebDriver.Chrome)(
            options=browsersettings
        )
    else:
        webdriver = utils_seleniumxp.webdriver_addon.WebDriver3rdPartyMixedin(utils_seleniumxp.WebDriver.Chrome)(
            options=browsersettings
        )
    if eventlistener is not None:
        if mixin or utils_seleniumxp.mixinactive:
            webdriver = utils_seleniumxp.eventfiring_addon.EventFiringWebDriverExtended(webdriver, eventlistener)
        else:
            webdriver = utils_seleniumxp.webdriver_addon.EventFiringWebDriverExtendedMixedin(webdriver, eventlistener)
    # webdriver.get("about:blank")

    # set logging for closepopup
    set_log_closepopup(webdriver, config, inisection)

    # get URL
    if URL != "about:blank":
        webdriver.get(URL)

    # make sure closepopup log is closed when application ends
    atexit.register(close_log_closepopup, webdriver)
    # make sure webdriver process(es) is/are killed when application ends
    # -> does not need to happen as chromedriver.exe of calling application might be killed?
    # atexit.register(os.kill, webdriver.service.process.pid, signal.SIGTERM)
    atexit.register(kill_driver_processes, browser, webdriver.service.process.pid)

    return webdriver

def connectChrome(
    debugport: int,
    inifile: Optional[str] = None,
    inisection: str = "DEFAULT",
    mixin: bool = utils_seleniumxp.mixinactive,
    eventlistener: Optional[utils_seleniumxp.AbstractEventListener] = None,
    URL: str = "about:blank"
) -> Optional[utils_seleniumxp._RemoteWebDriver]:
    """
    connectChrome - connect to Chrome instance via debugport

    Args:
        debugport (int): assumed debug port of Chrome instance
        inifile (Optional[str], optional): INI file. Defaults to None.
        inisection (str, optional): INI section to be evaluated. Defaults to "DEFAULT".
        mixin (bool, optional): flag to switch between mixin and setattr mode. Defaults to utils_seleniumxp.mixinactive.
        eventlistener (Optional[utils_seleniumxp.eventfiring_addon.AbstractEventListenerExtended], optional): eventlistener object to activate eventfiring mode. Defaults to None.
        URL (str, optional): start URL. Defaults to "about:blank".

    Returns:
        utils_seleniumxp.WebDriver: webdriver object
    """
    return connect_chrome(debugport, inifile, inisection, mixin, eventlistener, URL)



# utilities for initialization

# read config file
def read_configfile(inifile: Optional[str]) -> tuple[configparser.ConfigParser, configparser.ConfigParser]:
    """
    read_configfile - read config file

    Args:
        inifile (Optional[str], optional): INI file with config data. Defaults to None.

    Returns:
        configparser.ConfigParser: configparser object
    """

    if inifile is None or not os.path.isfile(inifile):
        inifile = os.path.join(os.path.expanduser("~"), "SeleniumPythonUtils.ini")
    if not os.path.isfile(inifile):
        inifile = os.path.join(os.path.dirname(__file__), "SeleniumPythonUtils.ini")

    config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
    config.read(inifile)

    config_without_default = configparser.ConfigParser(default_section=None, interpolation=configparser.ExtendedInterpolation())
    config_without_default.read(inifile)

    return config, config_without_default

# check path parameter from config
# used to check
# - browser binary location (for portable installations)
# - webdriver location
def check_configpath(
    config: configparser.ConfigParser,
    inisection: str,
    configparampath: str,
    binaryfile: str = "",
    checkwd: bool = False
) -> Optional[str]:
    """
    check_configpath - check path for binaries
    """

    checkpath: str = config.get(inisection, configparampath, fallback="")

    if checkpath != "":
        checkpath = os.path.expandvars(checkpath)
        if binaryfile:
            if os.path.isdir(checkpath):
                if os.path.isfile(os.path.join(checkpath, binaryfile)):
                    return checkpath
            if checkwd:
                checkpath = os.getcwd()
                if os.path.isfile(os.path.join(checkpath, binaryfile)):
                    return checkpath
        elif os.path.isdir(checkpath):
            return checkpath

    return ""

# check path parameter from config
# used to check fallback via userprofile
def check_usrpath(config: configparser.ConfigParser, inisection: str, configparampathsuffix: str) -> Optional[str]:
    """
    check_usrpath - check path für user path suffix from config file
    """

    homepath = os.path.expanduser("~")
    try:
        checkpath = os.path.join(homepath, os.path.expandvars(config[inisection][configparampathsuffix]))
        if os.path.isdir(checkpath):
            return checkpath
    except Exception:
        pass

    return ""


# predefined config-setting packages (only for new browser instances)

# config/options-settings for direct download - Chrome & Firefox
# routine to be used as function parameter for Selenium webdriver initialization/generator function
def directdownload(browser: str, defaultdir: Optional[str]) -> Union[dict, list, None]:
    """
    directdownload - create settings data object with config/options-settings for direct download

    Args:
        browser (str): browser
        defaultdir (str, optional): target directory. Defaults to None.

    Returns:
        Union[dict, list, None]: settings data object
    """

    if browser not in supported_browsers:
        err_msg = f"Browser '{browser}' not supported."
        raise utils_seleniumxp.ErrorUtilsSelenium(err_msg)

    if defaultdir is None:
        defaultdir = tempfile.gettempdir()

    if browser == "chrome":
        return {
            "download.default_directory": defaultdir,
            "download.prompt_for_download": False,
            "plugins.always_open_pdf_externally": True
        }
    elif browser == "firefox":
        return [
            ("browser.download.folderList", 2),
            ("browser.download.dir", defaultdir),
            ("browser.download.manager.showWhenStarting", False),
            ("browser.helperApps.alwaysAsk.force", False),
            ("browser.helperApps.neverAsk.saveToDisk", "application/pdf,text/csv"),
            ("pdfjs.disabled", True)
        ]
    return None

# config/options-settings for disabling notifications - Chrome & Firefox
# routine to be used as function parameter for Selenium webdriver initialization/generator function
def disablenotifications(browser: str) -> Union[dict, list, None]:
    """
    disablenotifications - create settings data object with config/options-settings for disabling notifications

    Args:
        browser (str): browser

    Returns:
        Union[dict, list, None]: settings data object
    """

    if browser not in supported_browsers:
        err_msg = f"Browser '{browser}' not supported."
        raise utils_seleniumxp.ErrorUtilsSelenium(err_msg)

    if browser == "chrome":
        return {
            "profile.managed_default_content_settings.notifications": 2
        }
    elif browser == "firefox":
        return [
            ("dom.webnotifications.enabled", False),
        ]
    return None

# config/options-settings for optimized scraping - Chrome & Firefox
# routine to be used as function parameter for Selenium webdriver initialization/generator function
#
# inspiration:
# https://github.com/dinuduke/Selenium-chrome-firefox-tips
# https://petertc.medium.com/pro-tips-for-selenium-setup-1855a11f88f8
# 0 -> default, 1 -> allow, 2 -> block
# NOTE: cookies must be allowed to click popup "away"
def optimizedscraping(browser: str) -> Union[dict, list, None]:
    """
    optimizedscraping - create settings data object with config/options-settings for optimized scraping

    Args:
        browser (str): browser

    Returns:
        Union[dict, list, None]: settings data object
    """

    if browser not in supported_browsers:
        err_msg = f"Browser '{browser}' not supported."
        raise utils_seleniumxp.ErrorUtilsSelenium(err_msg)

    if browser == "chrome":
        return {
            "profile.default_content_setting_values.notifications": 2,
            "profile.managed_default_content_settings.images": 2,
            "profile.managed_default_content_settings.stylesheets": 2,
            "profile.managed_default_content_settings.cookies": 1,
            "profile.managed_default_content_settings.javascript": 1,
            "profile.managed_default_content_settings.plugins": 1,
            "profile.managed_default_content_settings.popups": 2,
            "profile.managed_default_content_settings.geolocation": 2,
            "profile.managed_default_content_settings.media_stream": 2
        }
    elif browser == "firefox":
        return [
            ("permissions.default.stylesheet", 2),
            ("permissions.default.image", 2),
            ("dom.ipc.plugins.enabled.libflashplayer.so", "false")
        ]
    return None


# routines to support other stuff - routines not used as direct callables for mixin-methods or any kind of wrapping

# set up log for session initialization

def set_log_sessionstart(config: configparser.ConfigParser, inisection: str) -> Optional[logging.Logger]:
    """
    set_log_sessionstart - initialize logger for logging of session start

    Args:
        config (configparser.ConfigParser): configuration parser object filed form INI file
        inisection (str): INI file section

    Returns:
        Optional[logging.Logger]: logger object
    """

    # if config[inisection]["log_sessionstart"]:
    if config.getboolean(inisection, "log_sessionstart"):
        logpath = config.get(inisection, "log_sessionstart_path")
        return Utils.initLogger(loggername="Log_SessionStart", filename=logpath)
    else:
        return None

def close_log_sessionstart(sessionstart_logger: Optional[logging.Logger]):
    """
    close_log_sessionstart - close logger for logging session start

    Args:
        sessionstart_logger (Optional[logging.Logger]): logger
    """

    if sessionstart_logger is not None:
        for handler in sessionstart_logger.handlers:
            handler.close()

# set up log for closepopup

def set_log_closepopup(webdriver: utils_seleniumxp._RemoteWebDriver, config: configparser.ConfigParser, inisection: str):
    """
    set_log_closepopup - - initialize logger for logging close popups

    Args:
        webdriver (utils_seleniumxp._RemoteWebDriver): webdriver object
        config (configparser.ConfigParser): configuration parser object filed form INI file
        inisection (str): INI file section
    """

    # if config[inisection]["log_closepopup"]:
    if config.getboolean(inisection, "log_closepopup"):
        logpath = config.get(inisection, "log_closepopup_path")
        setattr(webdriver, "closepopup_logger", Utils.initLogger(loggername="Log_ClosePopup", filename=logpath))

def close_log_closepopup(webdriver: utils_seleniumxp._RemoteWebDriver):
    """
    close_log_closepopup - close logger for logging close popups

    Args:
        webdriver (utils_seleniumxp._RemoteWebDriver): webdriver object
    """

    if hasattr(webdriver, "closepopup_logger"):
        if webdriver.closepopup_logger is not None:
            for handler in webdriver.closepopup_logger.handlers:
                handler.close()


# clean up driver processes
def kill_driver_processes(browser: str = "chrome", pid=None):
    """
    kill_driver_processes - routine to kill driver process(es) for automated clean-up

    Args:
        browser (str, optional): browser. Defaults to "chrome".
    """

    if browser not in supported_browsers:
        err_msg = f"Browser '{browser}' not supported."
        raise utils_seleniumxp.ErrorUtilsSelenium(err_msg)

    driverbinary: str = supported_browsers[browser][1]
    with contextlib.suppress(psutil.NoSuchProcess):
        psutil.Process(pid).send_signal(signal.SIGTERM)
    pids: list = []
    try:
        for proc in psutil.process_iter(["name"]):
            if proc.info["name"] == driverbinary:
                if pid is None or pid == proc.pid:
                    pids.append(proc.pid)
    except Exception:
        pass
    for pid in pids:  # noqa: PLR1704
        psutil.Process(pid).send_signal(signal.SIGTERM)
