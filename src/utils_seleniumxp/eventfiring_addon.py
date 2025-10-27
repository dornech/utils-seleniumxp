# Selenium webdriver utilities - XP version
# event firing and listening - additional functionalities compared to sample implementation

"""
module providing event firing and listening - additional functionalities compared to sample implementation
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
# ruff: noqa: B006, E301, PLR0904, PLR0917, SIM102
#
# disable mypy errors
# - mypy error "Returning Any from function ..."
# mypy: disable-error-code = "no-any-return"

# fmt: off

# docsig: disable



# TODO Dev:
# n. a.

# TODO Test:
# - Event Firing Extensions for SwitchTo and Alert



from typing import Any, Optional

import sys

from selenium.webdriver.remote.webdriver import WebDriver as _WebDriver
from selenium.webdriver.remote.webelement import WebElement as _WebElement
from selenium.webdriver.remote.switch_to import SwitchTo as _SwitchTo
from selenium.webdriver.common.alert import Alert as _Alert
from selenium.webdriver.support.abstract_event_listener import AbstractEventListener
from selenium.webdriver.support.event_firing_webdriver import EventFiringWebDriver
from selenium.webdriver.support.event_firing_webdriver import EventFiringWebElement



# commonly used functions for extended EventFiringXXX classes

# result wrapper
def _wrap_elements(result: Any, ef_driver: "EventFiringWebDriverExtended") -> Any:

    # handle the case if another wrapper wraps EventFiringWebElementXXX classes
    if isinstance(result, (EventFiringWebElementExtended, EventFiringSwitchTo, EventFiringAlert)):
        return result
    elif isinstance(result, _WebElement):
        return EventFiringWebElementExtended(result, ef_driver)
    elif isinstance(result, _SwitchTo):
        return EventFiringSwitchTo(result, ef_driver)
    elif isinstance(result, _Alert):
        return EventFiringAlert(result, ef_driver)
    elif isinstance(result, list):
        return [_wrap_elements(item, ef_driver) for item in result]
    # result is a built-in type.
    else:
        return result

# dispatcher (copy of original dispatcher method but modified using _dispatcherobject and _wrapperobject
# attributes of extended / new EventFiringXXX classes to avoid complex if-clause)
# for non-elementary webdriver methods (like closepopup) special treatment is implemented
def _dispatch(
    dispatcher: Any,
    l_call: Optional[str],
    l_args: tuple[Any, ...],
    d_call: str,
    d_args: tuple[Any, ...],
    b_recursive: bool = False
) -> Any:

    # if l_call is not None and l_call != "":
    if l_call:
        getattr(dispatcher._listener, f"before_{l_call}")(*l_args)
    try:
        if isinstance(dispatcher, EventFiringWebDriverExtended) and b_recursive:
            result = getattr(dispatcher, d_call)(*d_args)
        else:
            result = getattr(dispatcher._dispatcherobject, d_call)(*d_args)
    except Exception as e:
        dispatcher._listener.on_exception(e, dispatcher._driver)
        raise
    if l_call is not None and l_call != "":
        getattr(dispatcher._listener, f"after_{l_call}")(*l_args)

    return _wrap_elements(result, dispatcher._wrapperobject)

# getattr for FiringEventXXX classes (copy of original getattr method but modified to avoid
# code duplication and re-use for new classes EventFiringSwitchTo and EventFiringAlert)
def _getattr(dispatcher, name: str) -> Any:

    def _wrap(*args, **kwargs):
        try:
            result = attrib(*args, **kwargs)
            return _wrap_elements(result, dispatcher._wrapperobject)
        except Exception as e:
            dispatcher._listener.on_exception(e, dispatcher._driver)
            raise

    try:
        attrib = getattr(dispatcher._dispatcherobject, name)
        return _wrap if callable(attrib) else attrib
    except Exception as e:
        dispatcher._listener.on_exception(e, dispatcher._driver)
        raise

# generic dispatcher - deliver wrapper instead executed call
# note that log entry generation for after_event must be included in returned wrapper to keep
# execution order; however log entry generation for before_event is included as well as for non-method events
# the log entries do not make too much sense anyway
def _getattr_dispatch_generic(dispatcher: Any, l_call: Optional[str], l_args: tuple, d_call: str):

    def _wrap(*args, **kwargs):

        if l_call is not None and l_call != "":
            getattr(dispatcher._listener, f"before_{l_call}")(*l_args)
        else:
            getattr(dispatcher._listener, dispatcher._listener.generic_listener_name())(f"before_{d_call}", *l_args)
        try:
            result = attrib(*args, **kwargs)
        except Exception as e:
            dispatcher._listener.on_exception(e, dispatcher._driver)
            raise
        if l_call is not None and l_call != "":
            getattr(dispatcher._listener, f"after_{l_call}")(*l_args)
        else:
            getattr(dispatcher._listener, dispatcher._listener.generic_listener_name())(f"after_{d_call}", *l_args)

        return _wrap_elements(result, dispatcher._wrapperobject)

    attrib = getattr(dispatcher._dispatcherobject, d_call)
    return _wrap if callable(attrib) else attrib


# extended EventFiringXXX classes

# extended EventFiringWebDriver
class EventFiringWebDriverExtended(EventFiringWebDriver):
    """
    EventFiringWebDriverExtended - extended EventFiringWebDriver class
    """

    def __init__(self, webdriver: _WebDriver, eventlistener: AbstractEventListener):
        super().__init__(webdriver, eventlistener)
        self._switch_to = EventFiringSwitchTo(super().wrapped_driver._switch_to, self)
        self._dispatcherobject = self._driver
        self._wrapperobject = self

    def start_session(self, capabilities: dict[str, Any], browser_profile: Any = None) -> None:
        self._dispatch("start_session", (self._driver,), "start_session", (capabilities, browser_profile))

    def refresh(self) -> None:
        self._dispatch("refresh", (self._driver,), "refresh", ())

    def add_cookie(self, cookie_dict: dict[str, Any]) -> None:
        self._dispatch("cookiemanager", ("add", cookie_dict, self._driver), "add_cookie", (cookie_dict,))

    def delete_all_cookies(self) -> None:
        self._dispatch("cookiemanager", ("delete", "all", self._driver), "delete_all_cookies", ())

    def delete_cookie(self, name: str) -> None:
        self._dispatch("cookiemanager", ("delete", name, self._driver), "delete_cookies", (name,))

    def get_cookies(self) -> list[dict[str, Any]]:
        return self._dispatch("cookiemanager", ("get", "all", self._driver), "get_cookies", ())

    def get_cookie(self, name: str) -> dict[str, Any]:
        return self._dispatch("cookiemanager", ("get", name, self._driver), "get_cookie", (name,))

    def request(self, method: str, url: str, **kwargs) -> Any:
        return self._dispatch("request", (method, url, self._driver), "request", (method, url, *kwargs))

    def _dispatch(
        self,
        l_call: Optional[str],
        l_args: tuple[Any, ...],
        d_call: str,
        d_args: tuple[Any, ...],
        b_recursive: bool = False
    ) -> Any:
        return _dispatch(self, l_call, l_args, d_call, d_args, b_recursive)

    def __getattr__(self, name: str) -> Any:
        # generic call of event listener (if listener object has implemented the interface)
        # watch out for necessity of wrapping the call to match Callable as __getattr__ return type
        # but NOT return type of method d_call
        if hasattr(self._listener, f"before_{name}") and hasattr(self._listener, f"after_{name}"):
            # generic call - listener provides listening method not registered separately in event-firing
            # webdriver class
            return _getattr_dispatch_generic(self, name, (self._driver,), name)
        else:
            if hasattr(self._listener, "checkgeneric") and hasattr(self._listener, "generic_listener_name"):
                if self._listener.checkgeneric(name):
                    return _getattr_dispatch_generic(self, None, (self._driver,), name)
            return _getattr(self, name)


# extended EventFiringSwitchTo
class EventFiringSwitchTo:

    def __init__(self, switch_to: _SwitchTo, ef_driver: EventFiringWebDriverExtended):
        self._switch_to = switch_to
        self._ef_driver = ef_driver
        self._driver = ef_driver.wrapped_driver
        self._listener = ef_driver._listener
        self._dispatcherobject = self._switch_to
        self._wrapperobject = self._ef_driver

    @property
    def wrapped_element(self) -> _SwitchTo:
        return self._switch_to

    def active_element(self) -> Any:
        return self._dispatch(None, (), "active_element", ())

    def alert(self) -> Any:
        return self._dispatch(None, (), "alert", ())

    def default_content(self) -> None:
        self._dispatch("switch_to", ("default", "", self._driver), "default_content", ())

    def frame(self, frame_reference: Any) -> None:
        self._dispatch("switch_to", ("frame", frame_reference, self._driver), "frame", (frame_reference))

    def new_window(self, type_hint: str) -> None:
        self._dispatch("switch_to", ("new_window", type_hint, self._driver), "frame", (type_hint,))

    def parent_frame(self) -> None:
        self._dispatch("switch_to", ("parent_frame", "", self._driver), "parent_frame", ())

    def window(self, window_name: str):
        self._dispatch("switch_to", ("window", window_name, self._driver), "window", (window_name,))

    def _dispatch(
        self,
        l_call: Optional[str],
        l_args: tuple[Any, ...],
        d_call: str,
        d_args: tuple[Any, ...]
    ) -> Any:
        return _dispatch(self, l_call, l_args, d_call, d_args)

    def __getattr__(self, name: str) -> Any:
        return _getattr(self, name)

# done for original EventFiringSwitchTo not possible for own developed class
# here as registering super class is not derived from ABC metaclass
# i. e. did to inherit register method
# UtilsSeleniumXP._SwitchTo.register(EventFiringSwitchTo)


# extended EventFiringAlert
class EventFiringAlert:

    def __init__(self, alert: _Alert, ef_driver: EventFiringWebDriverExtended):
        self._alert = alert
        self._ef_driver = ef_driver
        self._driver = ef_driver.wrapped_driver
        self._listener = ef_driver._listener
        self._dispatcherobject = self._alert
        self._wrapperobject = self._ef_driver

    @property
    def wrapped_element(self) -> _Alert:
        return self._alert

    def dismiss(self) -> None:
        self._dispatch("alerthandler", ("dismiss", self._driver), "dismiss", ())

    def accept(self) -> None:
        self._dispatch("alerthandler", ("accept", self._driver), "accept", ())

    def send_keys(self, keysToSend: str) -> None:
        self._dispatch("alerthandler", (f"sendkeys '{keysToSend}'", self._driver), "send_keys", (keysToSend,))

    def _dispatch(
        self,
        l_call: Optional[str],
        l_args: tuple[Any, ...],
        d_call: str,
        d_args: tuple[Any, ...]
    ) -> Any:
        return _dispatch(self, l_call, l_args, d_call, d_args)

    def __getattr__(self, name: str) -> Any:
        return _getattr(self, name)

# done for original EventFiringAlert but not possible for own developed
# class here as registering super class is not derived from ABC metaclass
# i. e. did to inherit register method
# UtilsSeleniumXP.Alert.register(EventFiringAlert)


# extended EventFiringWebelement
class EventFiringWebElementExtended(EventFiringWebElement):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._dispatcherobject = self._webelement
        self._wrapperobject = self._ef_driver

    def submit(self) -> Any:
        self._dispatch("submit", (self._webelement, self._driver), "submit", ())

    def _dispatch(
        self,
        l_call: Optional[str],
        l_args: tuple,
        d_call: str,
        d_args: tuple
    ) -> Any:
        return _dispatch(self, l_call, l_args, d_call, d_args)

    def __getattr__(self, name: str) -> Any:
        return _getattr(self, name)

# needed for original class EventFiringWebElement but potentially not needed for
# class EventFiringWebElementExtended as this is a subclass of EventFiringWebElement
# and implicitly of class WebElement
# UtilsSeleniumXP.WebElement.register(EventFiringWebElementExtended)


# extended AbstractEventListener
class AbstractEventListenerExtended(AbstractEventListener):
    """
    AbstractEventListenerExtended - extended abstract base class AbstractEventListener for event listener

    Extensions:
     - filter mechanism for events to be captured (or not)
     - utilities for event handlers
     - additional events
     - infrastructure for handling  generic events
    """

    # properties for dynamic control which events should be included and which not

    @property
    def events_include(self) -> list[str]:
        return self._events_include

    @events_include.setter
    def events_include(self, eventlist: list[str]) -> None:
        self._events_include = eventlist
    @property
    def events_exclude(self) -> list[str]:
        return self._events_exclude
    @events_exclude.setter
    def events_exclude(self, eventlist: list[str]) -> None:
        self._events_exclude = eventlist

    @property
    def events_generic(self) -> list[str]:
        return self._events_generic
    @events_generic.setter
    def events_generic(self, eventlist: list[str]) -> None:
        self._events_generic = eventlist

    # initialization and utilities

    def __init__(
        self,
        events_include_list: list[str] = [],
        events_exclude_list: list[str] = [],
        events_generic_list: list[str] = []
    ):

        self.events_include: list[str] = events_include_list
        self.events_exclude: list[str] = events_exclude_list
        self.events_generic: list[str] = events_generic_list

    @classmethod
    def _getmethodname(cls) -> str:
        """ utility for event handler (avoid hardcoding of event name in handler method) """
        return sys._getframe(1).f_code.co_name

    def checkevent(self, event_name: str) -> bool:
        return (
            (event_name in self._events_include or self._events_include == []) and
            (event_name not in self._events_exclude)
        )

    # extended listener

    def before_cookiemanager(self, mode: str, cookiekey: str, driver: _WebDriver) -> None:
        pass

    def after_cookiemanager(self, mode: str, cookiekey: str, driver: _WebDriver) -> None:
        pass

    def before_refresh(self, driver: _WebDriver) -> None:
        pass

    def after_refresh(self, driver: _WebDriver) -> None:
        pass

    def before_start_session(self, driver: _WebDriver) -> None:
        pass

    def after_start_session(self, driver: _WebDriver) -> None:
        pass

    def before_submit(self, element, driver: _WebDriver) -> None:
        pass

    def after_submit(self, element, driver: _WebDriver) -> None:
        pass

    def before_switch_to(self, objtyp, value: Any, driver: _WebDriver) -> None:
        pass

    def after_switch_to(self, objtyp, value: Any, driver: _WebDriver) -> None:
        pass

    def before_alerthandler(self, mode: str, driver) -> None:
        pass

    def after_alerthandler(self, mode: str, driver) -> None:
        pass

    def before_closepopuphandler(self, mode: str, driver) -> None:
        pass

    def after_closepopuphandler(self, mode: str, driver) -> None:
        pass

    def before_request(self, method: str, url: str, driver) -> None:
        pass

    def after_request(self, method: str, url: str, driver) -> None:
        pass

    # generic listener

    def checkgeneric(self, event_name: str) -> bool:
        return event_name in self._events_generic

    def generic_listener_name(self):
        return self.generic_listener.__name__

    def generic_listener(self, event_name: str, *args, **kwargs):
        pass
