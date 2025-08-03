# Selenium webdriver utilities - XP version
# locator tools - especially used for easy transfer of multiple locator parameter passing to close popups

"""
module providing Selenium locator tools
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
# ruff: noqa: B006, TID252
#
# disable mypy errors
# mypy: disable-error-code = "attr-defined, no-any-return"

# fmt: off



from typing import NamedTuple, Optional, Union

# from dataclasses import dataclass

import parsel
import re

from . import By
from . import ErrorUtilsSelenium



# locator as namedtuple
# note: dataclass leads to error as unpack operator will not work
class SeleniumLocator(NamedTuple):
    """
    SeleniumLocator - locator as namedtuple (dataclass leads to error as unpack operator will not work)
    """
    by: str
    value: str


# quick constructor for SeleniumLocator

# XPATH
def SeleniumLocatorXPATH(value: str):
    """
    SeleniumLocatorXPATH - factory function for XPATH-type SeleniumLocator class object
    """
    return SeleniumLocator(By.XPATH, value)

# CSS
def SeleniumLocatorCSS(value: str):
    """
    SeleniumLocatorCSS - factory function for CSS-type SeleniumLocator class object
    """
    return SeleniumLocator(By.CSS_SELECTOR, value)


# parameterized SeleniumLocator (inspired by https://pypi.org/project/selenium-actions)
# store base locator as f-string
class parameterizedSeleniumLocator:
    """
    parameterizedSeleniumLocator - parameterized SeleniumLocator class
    """

    def __init__(self, by: By, value: str):
        self._by = by
        self._value = value
        parameterlist = re.findall(r'{\w+}', value)
        if parameterlist:
            self._parameters = [re.sub(r'[{}]', '', param) for param in parameterlist]
        else:
            self._parameters = []

    @property
    def by(self) -> By:
        return self._by

    @property
    def value(self) -> str:
        return self._value

    @property
    def parameters(self) -> list[str]:
        return self._parameters

    @property
    def is_parameterized(self) -> bool:
        return len(self._parameters) > 0

    def replace_parameters(self, **kwargs) -> SeleniumLocator:
        if self.is_parameterized:
            if len(kwargs) == 0:
                err_msg = f'Missing keyword arguments: {self._parameters}'
                raise ValueError(err_msg)
            for param in self._parameters:
                if param not in kwargs:
                    err_msg = f'Missing keyword argument: {param}'
                    raise ValueError(err_msg)
            return SeleniumLocator(self._by, self._value.format(**kwargs))
        else:
            return SeleniumLocator(self._by, self._value)


# check locator list if all of specified type (default By.XPATH or By.CSS_SELECTOR)
def check_locatorlist(
    loclist: list[SeleniumLocator],
    loctypes: Optional[Union[list[str], set[str]]] = [By.XPATH, By.CSS_SELECTOR]
):
    """
    check_locator - check locator list if of type in typelist

    Args:
        loclist(List): list of SeleniumLocator objects (as unnamed parameters)
        loctypes (Optional[List[str]], optional): list of locator types. Defaults to [By.XPATH, By.CSS_SELECTOR].

    Returns:
        _type_: _description_
    """

    check = True
    for locator in loclist:
        if locator is not None:
            check = check and (locator.by in loctypes)  # type: ignore[operator]
    return check

def check_locator(locator: SeleniumLocator, loctypes: Optional[list[str]] = [By.XPATH, By.CSS_SELECTOR]):
    return check_locatorlist([locator], loctypes)



# parsel extension to unify calling for the selector types CSS and XPATH
class parselSelectorExtension(parsel.Selector):
    """
    parselSelectorExtension - parsel extension to unify calling for the selector types CSS and XPATH
    """

    def css_or_xpath(self, locator: SeleniumLocator):
        if locator.by == By.XPATH:
            return self.xpath(locator.value)
        elif locator.by == By.CSS_SELECTOR:
            return self.css(locator.value)
        else:
            ErrorUtilsSelenium("Only XPATH and CSS selectors allowed for parsel wrapper.")
