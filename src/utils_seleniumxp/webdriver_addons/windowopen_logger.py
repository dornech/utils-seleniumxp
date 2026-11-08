# Selenium webdriver utilities - XP version
# webdriver class - additional functionalities
# implementation window.open logger

"""
module with webdriver class extensions

submodule for window.open logger
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



import utils_seleniumxp


# logger for window.open
#
# log might be helpful to retrieve internal data of website hidden in the website's JavaScript model

# inject window.open logger
def window_open_logger(webdriver: utils_seleniumxp._RemoteWebDriver) -> None:
    """
    window_open_logger - inject javascript for window.open logger

    Args:
        webdriver (utils_seleniumxp._RemoteWebDriver): webdriver
    """

    script_wol = """
        window.WindowOpenLogger = function(action) {
            // internal init
            window.__openLog ||= [];
            switch (action) {
                case 'enable':
                    if (window.__openLoggerEnabled) return true;
                    // save org function once
                    const originalOpen = window.open;
                    // proxy instead of override
                    window.open = new Proxy(originalOpen, {
                        apply(target, thisArg, args) {
                            const [url, targetName, features] = args;
                            const entry = {
                                timestamp: new Date().toISOString(),
                                url,
                                target: targetName,
                                features
                            };
                            window.__openLog.push(entry);
                            console.log('window.open:', url);
                            return Reflect.apply(target, thisArg, args);
                        }
                    });
                    window.__originalWindowOpen = originalOpen;
                    window.__openLoggerEnabled = true;
                    return true;
                case 'disable':
                    if (!window.__openLoggerEnabled) return true;
                    if (window.__originalWindowOpen) {
                        window.open = window.__originalWindowOpen;
                    }
                    window.__openLoggerEnabled = false;
                    return true;
                case 'last':
                    return (window.__openLog || []).length ? window.__openLog[window.__openLog.length - 1] : null;
                case 'log':
                    return window.__openLog || [];
                case 'clear':
                    window.__openLog = [];
                    return true;
                case 'status':
                    return {
                        enabled: !!window.__openLoggerEnabled,
                        entries: (window.__openLog || []).length
                    };
                default:
                    throw new Error('Valid actions: enable, disable, last, log, clear, status');
            }
        }
        """

    utils_seleniumxp.wait4HTMLstable()
    webdriver.execute_script(script_wol)

# enable/activate window.open logger
def enable_wol(webdriver: utils_seleniumxp._RemoteWebDriver) -> bool:
    """
    enable_wol - enable window.open logger

    Args:
        webdriver (utils_seleniumxp._RemoteWebDriver): webdriver

    Returns:
        bool: execution status
    """
    return webdriver.execute_script("return window.WindowOpenLogger('enable');")

# disable/deactivate window.open logger
def disable_wol(webdriver: utils_seleniumxp._RemoteWebDriver) -> bool:
    """
    disable_wol - disable window.open logger

    Args:
        webdriver (utils_seleniumxp._RemoteWebDriver): webdriver

    Returns:
        bool: execution status
    """
    return webdriver.execute_script("return window.WindowOpenLogger('disable');")

# clear log of window.open logger
def clear_wol(webdriver: utils_seleniumxp._RemoteWebDriver) -> bool:
    """
    clear_wol - clear log of  window.open logger

    Args:
        webdriver (utils_seleniumxp._RemoteWebDriver): webdriver

    Returns:
        bool: execution status
    """
    return webdriver.execute_script("return window.WindowOpenLogger('clear');")

#  retrieve log entry from log of window.open logger
def last_logentry_wol(webdriver: utils_seleniumxp._RemoteWebDriver) -> dict:
    """
    last_logentry_wol - retrieve log entry from log of window.open logger

    Args:
        webdriver (utils_seleniumxp._RemoteWebDriver): webdriver

    Returns:
        dict: log entry
    """
    return webdriver.execute_script("return window.WindowOpenLogger('last');")

#  retrieve complete log of window.open logger
def log_wol(webdriver: utils_seleniumxp._RemoteWebDriver) -> list[dict]:
    """
    log_wol - retrieve complete log of window.open logger

    Args:
        webdriver (utils_seleniumxp._RemoteWebDriver): webdriver

    Returns:
        list[dict]: list of log entries
    """
    return webdriver.execute_script("return window.WindowOpenLogger('log');")

#  status of window.open logger
def status_wol(webdriver: utils_seleniumxp._RemoteWebDriver) -> dict:
    """
    status_wol - status of window.open logger

    Args:
        webdriver (utils_seleniumxp._RemoteWebDriver): webdriver

    Returns:
        dict: status information
    """
    return webdriver.execute_script("return window.WindowOpenLogger('status');")

# direct setattr instead of mixin-object but avoid name conflict
if not utils_seleniumxp.mixinactive:
    setattr(utils_seleniumxp._RemoteWebDriver, "window_open_logger", window_open_logger)
    setattr(utils_seleniumxp._RemoteWebDriver, "enable_wol", enable_wol)
    setattr(utils_seleniumxp._RemoteWebDriver, "disable_wol", disable_wol)
    setattr(utils_seleniumxp._RemoteWebDriver, "clear_wol", clear_wol)
    setattr(utils_seleniumxp._RemoteWebDriver, "last_logentry_wol", last_logentry_wol)
    setattr(utils_seleniumxp._RemoteWebDriver, "log_wol", log_wol)
    setattr(utils_seleniumxp._RemoteWebDriver, "status_wol", status_wol)
