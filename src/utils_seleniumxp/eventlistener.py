# Selenium webdriver utilities - XP version
# event firing and listening - simple sample event listener based on abstract template class of the Selenium
# project including not covered standard functions

"""
module providing event firing and listening - simple sample event listener based on abstract template class of
the Selenium project including not covered standard functions
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
# ruff: noqa: B006, PLR0904, PLR5501, PLR6301

# fmt: off



# TODO Dev:
# - config file handling i. e. for list of events?
# - create list of loggable events as tool

# TODO Test:
# - n. a.



from typing import Optional

import sys
import logging

from utils_seleniumxp.eventfiring_addon import AbstractEventListenerExtended
import utils_mystuff as Utils



class SimpleEventListener(AbstractEventListenerExtended):
    """
    SimpleEventListener - sample event listener implementation (including extended events) with event logging
    """

    # initialization and utilities

    def __init__(
        self,
        loggername: Optional[str] = None,
        events_include_list: list[str] = [],
        events_exclude_list: list[str] = [],
        events_generic_list: list[str] = []
    ):

        class EventLoggerFilter_PyCharm_debug_exceptions(logging.Filter):

            # filter function - however, internal on-exceptions from debug mode are not properly captured
            def filter(self, record):
                # https://stackoverflow.com/questions/38634988/check-if-program-runs-in-debug-mode
                debugmode = getattr(sys, 'gettrace', None)() is not None
                attriberror = "AttributeError" in record.msg
                internalattrib = (
                        "no attribute '__'" in record.msg or
                        "no attribute 'shape'" in record.msg or
                        "no attribute '_ipython_canary_method" in record.msg
                )
                return not (debugmode and attriberror and internalattrib)

        super().__init__(events_include_list, events_exclude_list, events_generic_list)

        if loggername is None:
            loggername = "Log_SeleniumEvents"
        self._eventlogger = Utils.initLogger(loggername)
        # self._eventlogger.addFilter(EventLoggerFilter_PyCharm_debug_exceptions())

    # standard listener

    def before_navigate_to(self, url, driver):
        event_name = self._getmethodname()
        if self.checkevent(event_name):
            self._eventlogger.info(f"event '{event_name}' URL '{url}'")

    def after_navigate_to(self, url, driver):
        event_name = self._getmethodname()
        if self.checkevent(event_name):
            self._eventlogger.info(f"event '{event_name}' URL '{url}'")

    def before_navigate_back(self, driver):
        event_name = self._getmethodname()
        if self.checkevent(event_name):
            self._eventlogger.info(f"event '{event_name}'")

    def after_navigate_back(self, driver):
        event_name = self._getmethodname()
        if self.checkevent(event_name):
            self._eventlogger.info(f"event '{event_name}'")

    def before_navigate_forward(self, driver):
        event_name = self._getmethodname()
        if self.checkevent(event_name):
            self._eventlogger.info(f"event '{event_name}'")

    def after_navigate_forward(self, driver):
        event_name = self._getmethodname()
        if self.checkevent(event_name):
            self._eventlogger.info(f"event '{event_name}'")

    def before_find(self, by, value, driver):
        event_name = self._getmethodname()
        if self.checkevent(event_name):
            self._eventlogger.info(f"event '{event_name}' for {{by='{by}', value='{value}'}}")

    def after_find(self, by, value, driver):
        event_name = self._getmethodname()
        if self.checkevent(event_name):
            self._eventlogger.info(f"event '{event_name}' for {{by='{by}', value='{value}'}}")

    def before_click(self, element, driver):
        event_name = self._getmethodname()
        if self.checkevent(event_name):
            self._eventlogger.info(f"event '{event_name}' of {element} (tagname '{element.tag_name}')")

    def after_click(self, element, driver):
        event_name = self._getmethodname()
        if self.checkevent(event_name):
            self._eventlogger.info(f"event '{event_name}' of {element} (tagname '{element.tag_name}')")

    def before_change_value_of(self, element, driver):
        event_name = self._getmethodname()
        if self.checkevent(event_name):
            self._eventlogger.info(f"event '{event_name}' {element} (tagname '{element.tag_name}')")

    def after_change_value_of(self, element, driver):
        event_name = self._getmethodname()
        if self.checkevent(event_name):
            self._eventlogger.info(f"event '{event_name}' {element} (tagname '{element.tag_name}')")

    def before_execute_script(self, script, driver):
        event_name = self._getmethodname()
        if self.checkevent(event_name):
            self._eventlogger.info(f"event '{event_name}' '{script}'")

    def after_execute_script(self, script, driver):
        event_name = self._getmethodname()
        if self.checkevent(event_name):
            self._eventlogger.info(f"event '{event_name}' '{script}'")

    def before_close(self, driver):
        event_name = self._getmethodname()
        if self.checkevent(event_name):
            self._eventlogger.info(f"event '{event_name}'")

    def after_close(self, driver):
        event_name = self._getmethodname()
        if self.checkevent(event_name):
            self._eventlogger.info(f"event '{event_name}'")

    def before_quit(self, driver):
        event_name = self._getmethodname()
        if self.checkevent(event_name):
            self._eventlogger.info(f"event '{event_name}'")

    def after_quit(self, driver):
        event_name = self._getmethodname()
        if self.checkevent(event_name):
            self._eventlogger.info(f"event '{event_name}'")

    def on_exception(self, exception, driver):
        event_name = self._getmethodname()
        if self.checkevent(event_name):
            exceptionmsg = str(exception).replace("\n", " ")
            self._eventlogger.info(f"event '{event_name}' '{exception.__class__.__name__}', '{exceptionmsg}'")

    # extended listener

    def before_cookiemanager(self, mode, cookiekey, driver):
        event_name = self._getmethodname()
        if self.checkevent(event_name):
            if mode == "add":
                self._eventlogger.info(f"event '{event_name}' mode '{mode}' for cookie-key(s) '{cookiekey.keys()}'")
            else:
                if cookiekey != 'all':
                    self._eventlogger.info(f"event '{event_name}' mode '{mode}' for cookie-key '{cookiekey}'")
                else:
                    self._eventlogger.info(f"event '{event_name}' mode '{mode}' for all cookies")

    def after_cookiemanager(self, mode, cookiekey, driver):
        event_name = self._getmethodname()
        if self.checkevent(event_name):
            self._eventlogger.info(f"event '{event_name}' mode '{mode}'")

    def before_refresh(self, driver):
        event_name = self._getmethodname()
        if self.checkevent(event_name):
            self._eventlogger.info(f"event '{event_name}'")

    def after_refresh(self, driver):
        event_name = self._getmethodname()
        if self.checkevent(event_name):
            self._eventlogger.info(f"event '{event_name}'")

    def before_start_session(self, driver):
        event_name = self._getmethodname()
        if self.checkevent(event_name):
            self._eventlogger.info(f"event '{event_name}'")

    def after_start_session(self, driver):
        event_name = self._getmethodname()
        if self.checkevent(event_name):
            self._eventlogger.info(f"event '{event_name}'")

    def before_submit(self, element, driver):
        event_name = self._getmethodname()
        if self.checkevent(event_name):
            self._eventlogger.info(f"event '{event_name}' of {element}")

    def after_submit(self, element, driver):
        event_name = self._getmethodname()
        if self.checkevent(event_name):
            self._eventlogger.info(f"event '{event_name}' of {element}")

    def before_switch_to(self, objtyp, value, driver):
        event_name = self._getmethodname()
        if self.checkevent(event_name):
            self._eventlogger.info(f"event '{event_name}' {objtyp} with identifier '{value}'")

    def after_switch_to(self, objtyp, value, driver):
        event_name = self._getmethodname()
        if self.checkevent(event_name):
            self._eventlogger.info(f"event '{event_name}' {objtyp} with identifier '{value}'")

    def before_alerthandler(self, mode, driver):
        event_name = self._getmethodname()
        if self.checkevent(event_name):
            self._eventlogger.info(f"event '{event_name}' mode '{mode}'")

    def after_alerthandler(self, mode, driver):
        event_name = self._getmethodname()
        if self.checkevent(event_name):
            self._eventlogger.info(f"event '{event_name}' mode '{mode}'")

    def before_closepopuphandler(self, mode, driver):
        event_name = self._getmethodname()
        if self.checkevent(event_name):
            self._eventlogger.info(f"event '{event_name}' mode '{mode}'")

    def after_closepopuphandler(self, mode, driver):
        event_name = self._getmethodname()
        if self.checkevent(event_name):
            self._eventlogger.info(f"event '{event_name}' mode '{mode}'")

    def before_request(self, method, url, driver):
        event_name = self._getmethodname()
        if self.checkevent(event_name):
            self._eventlogger.info(f"event '{event_name}' method '{method}' for URL '{url}'")

    def after_request(self, method, url, driver):
        event_name = self._getmethodname()
        if self.checkevent(event_name):
            self._eventlogger.info(f"event '{event_name}' method '{method}' for URL '{url}'")

    # generic listener

    def generic_listener(self, event_name: str, *args, **kwargs):
        if isinstance(event_name, str):
            self._eventlogger.info(f"event '{event_name}'")
        else:
            err_msg = "Call for generic event logging not valid."
            raise Exception(err_msg)
