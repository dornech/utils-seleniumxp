# Selenium webdriver utilities - XP version
# webelement - additional functionalities
# wrapper class not possible as WebElement class is referred to by general webdriver class

"""
module with webelement class extensions

Webelement extensions include:
- more convenient access as select object
- various scrolling
- retrieval of XPATH of an element
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
# ruff: noqa: B010, E305, E501
#
# disable mypy errors
# mypy: disable-error-code = "no-any-return, attr-defined"


# fmt: off



# TODO Dev:
# - extension for mixin classes / own routines
# - click_and_wait (possibly include scroll_into_view) ?

# TODO Test:
# - n. a.



import time

import parsel
import cssify

import utils_seleniumxp



# block direct calling
# __all__ = []



# asselect wrapper for webelement - provides more OOic approach on SELECT-webelement

# pseudo-wrapper for select webelement - implement asselect method to avoid Select(webdriver.find_element(...))
def asselect(webelement: utils_seleniumxp._WebElement) -> utils_seleniumxp.Select:
    """
    asselect - provide direct access to select object to a SELECT-tag

    Args:
        webelement (utils_seleniumxp._WebElement): webelement

    Returns:
        utils_seleniumxp.Select: Selenium select object
    """

    if webelement.tag_name.upper() == "SELECT":
        return utils_seleniumxp.Select(webelement)
    else:
        err_msg = "WebElement is not a SELECT element."
        raise utils_seleniumxp.ErrorUtilsSelenium(err_msg)

def as_select(webelement: utils_seleniumxp._WebElement) -> utils_seleniumxp.Select:
    """
    as_select - provide direct access to select object to a SELECT-tag (alternative caller to asselect)
    """
    return asselect(webelement)

# no mixin-object for WebElement -> direct settattr
setattr(utils_seleniumxp._WebElement, "asselect", asselect)
setattr(utils_seleniumxp._WebElement, "as_select", asselect)


# webelement - hover over element

# hover over element
def hover_over(webelement: utils_seleniumxp._WebElement) -> None:
    """
    hover_over -  action chain to hover over element

    Args:
        webelement (utils_seleniumxp._WebElement): webelement
    """

    utils_seleniumxp.WebDriver.ActionChains(webelement.parent).move_to_element(webelement).perform()

# no mixin-object for WebElement -> direct settattr
setattr(utils_seleniumxp._WebElement, "hover_over", hover_over)


# webelement - scroll into view or viewport / scroll into view and click

# scroll into view
def scroll_into_view(
    webelement: utils_seleniumxp._WebElement, offset_pixels: int = 0, align_to_top: bool = False
) -> None:
    """
    scroll_into_view - scroll webelement into view

    Args:
        webelement (utils_seleniumxp._WebElement): webelement
        offset_pixels (int, optional): vertical pixel offset. Defaults to 0.
        align_to_top (bool, optional): flag for alignment to top of page. Defaults to False.
    """

    webelement.parent.execute_script("arguments[0].scrollIntoView(arguments[1]);", webelement, align_to_top)
    # compensate for the header
    # unfortunately subsequent scripts seem to interfere with previous script if no wait
    if offset_pixels != 0:
        time.sleep(0.5)
        webelement.parent.execute_script(f"window.scrollBy(0, {offset_pixels});")
    else:
        time.sleep(0.5)

# scroll into view and click
def scroll_into_view_and_click(
    webelement: utils_seleniumxp._WebElement, offset_pixels: int = 0, align_to_top: bool = False
) -> None:
    """
    scroll_into_view_and_click - scroll webelement into view and click

    Args:
        webelement (utils_seleniumxp._WebElement): webelement
        offset_pixels (int, optional): vertical pixel offset. Defaults to 0.
        align_to_top (bool, optional): flag for alignment to top of page. Defaults to False.
    """

    webelement.scroll_into_view(offset_pixels, align_to_top)
    webelement.click()

# scroll into middle of viewport
def scroll_into_viewportmid(webelement: utils_seleniumxp._WebElement) -> None:
    """
    scroll_into_viewportmid - scroll webelement into mid of viewport

    Args:
        webelement (utils_seleniumxp._WebElement): webelement
    """

    script = (
            "var viewPortHeight = Math.max(document.documentElement.clientHeight, window.innerHeight || 0);"
            "var elementTop = arguments[0].getBoundingClientRect().top;"
            "window.scrollBy(0, elementTop-(viewPortHeight/2));"
        )
    webelement.parent.execute_script(script, webelement)
    time.sleep(0.5)

# no mixin-object for WebElement -> direct settattr
setattr(utils_seleniumxp._WebElement, "scroll_into_view", scroll_into_view)
setattr(utils_seleniumxp._WebElement, "scroll_into_view_and_click", scroll_into_view_and_click)
setattr(utils_seleniumxp._WebElement, "scroll_into_viewportmid", scroll_into_viewportmid)


# webelement - get xpath and CSS selector

# script for getting element index to retrieve tag
script_get_tag_idx = """
    function get_tag_idx(element) {
         var ix = 0;
         var siblings = element.parentElement.children;
         for (var i = 0; i < siblings.length; i++) {
             var sibling = siblings[i];
             if (sibling === element)
                 return (ix+1);
             if (sibling.tagName === element.tagName)
                 ix++;
         }
    }
    return get_tag_idx(arguments[0]);
"""

# get simple XPath via loop
# idea and input:
# - https://stackoverflow.com/questions/2661818/javascript-get-xpath-of-a-node
# - https://stackoverflow.com/questions/5913927/get-child-node-index/42692428
def get_xpath(webelement: utils_seleniumxp._WebElement, use_id: bool = True) -> str:
    """
    get_xpath - get XPATH for webelement

    Args:
        webelement (utils_seleniumxp._WebElement): webelement
        use_id (bool, optional): flag if ID attribute should be used. Defaults to True.

    Returns:
        str: XPATH to webelement
    """

    parsedhtml = parsel.Selector(text=webelement.parent.page_source)
    xpath = ""

    while "/body" not in xpath:

        webelement_id = webelement.get_attribute("id")
        webelement_tag = webelement.tag_name.lower()

        if webelement_id is not None and webelement_id != "" and webelement_tag != "body":
            # use id
            xpath_section = f"/{webelement_tag}[@id='{webelement_id}']"
            if use_id and len(parsedhtml.xpath("/" + xpath_section).getall()) == 1:
                xpath = "/" + xpath_section + xpath
                break
            else:
                xpath = xpath_section + xpath
        elif webelement_tag == "body":
            # body element reached
            xpath = "/html/body" + xpath
            break
        else:
            # get element index (two versions possible - a) generalized n-th child or b) n-th child with specific tag-name
            # idx = webelement.parent.execute_script("return Array.from(arguments[0].parentNode.children).indexOf(arguments[0])", webelement)
            # xpath_section = f"/*[{idx + 1}]"
            idx = webelement.parent.execute_script(script_get_tag_idx, webelement)
            xpath_section = f"/{webelement_tag}[{idx}]"
            xpath = xpath_section + xpath
        webelement = webelement.find_element(utils_seleniumxp.By.XPATH, "./parent::*")

    return xpath

# get simple XPath via recursive call
def get_xpath_recursive(webelement: utils_seleniumxp._WebElement, parsedhtml=None, use_id: bool = True) -> str:
    """
    get_xpath_recursive - get XPATH for webelement

    Args:
        webelement (utils_seleniumxp._WebElement): webelement
        parsedhtml (_type_, optional): parsel selector object. Defaults to None.
        use_id (bool, optional): flag if ID attribute should be used. Defaults to True.

    Returns:
        str: XPATH to webelement
    """

    if webelement is None:
        return ""

    if parsedhtml is None:
        parsedhtml = parsel.Selector(text=webelement.parent.page_source)

    webelement_id = webelement.get_attribute("id")
    webelement_tag = webelement.tag_name.lower()

    if webelement_id is not None and webelement_id != "" and webelement_tag != "body":
        # use id
        xpath_section = f"/{webelement_tag}[@id='{webelement_id}']"
        if use_id and len(parsedhtml.xpath("/" + xpath_section).getall()) == 1:
            return "/" + xpath_section
    elif webelement_tag == "body":
        # body element reached
        return "/html/body"
    else:
        # get element index (two versions possible - a) generalized n-th child or b) n-th child with specific tag-name)
        # idx = webelement.parent.execute_script("return Array.from(arguments[0].parentNode.children).indexOf(arguments[0])", webelement)
        # xpath_section = f"/*[{idx + 1}]"
        idx = webelement.parent.execute_script(script_get_tag_idx, webelement)
        xpath_section = f"/{webelement_tag}[{idx}]"

    return get_xpath_recursive(
        webelement.find_element(utils_seleniumxp.By.XPATH, "./parent::*"), parsedhtml, use_id
    ) + xpath_section

# no mixin-object for WebElement -> direct settattr
setattr(utils_seleniumxp._WebElement, "get_xpath", get_xpath)
setattr(utils_seleniumxp._WebElement, "get_xpath_recursive", get_xpath_recursive)

# get simple CSS selector
def get_css_selector_from_xpath(webelement: utils_seleniumxp._WebElement, use_id: bool = False) -> str:
    """
    get_css_selector_from_xpath - get CSS selector for webelement by transforming XPATH

    Args:
        webelement (utils_seleniumxp._WebElement): webelement
        use_id (bool, optional): flag if ID attribute should be used. Defaults to False.

    Returns:
        str: CSS selector to webelement
    """

    xpath = webelement.get_xpath(use_id)
    return cssify.cssify(xpath)

def get_css_selector(webelement: utils_seleniumxp._WebElement) -> str:
    """
    get_css_selector - get CSS selector for webelement

    Args:
        webelement (utils_seleniumxp._WebElement): webelement

    Returns:
        str: CSS selector to webelement
    """

    css_selector: list[str] = []
    element = webelement

    while element.tag_name.lower() != 'html':

        tag = element.tag_name.lower()
        parent = element.find_element(utils_seleniumxp.By.XPATH, "..")
        siblings = parent.find_elements(utils_seleniumxp.By.XPATH, f"./{tag}")

        if len(siblings) == 1:
            css_selector.insert(0, tag)
        else:
            index = None
            for i, sibling in enumerate(siblings, start=1):
                if sibling._id == element._id:
                    index = i
                    break
            css_selector.insert(0, f"{tag}:nth-of-type({index})")

        element = parent

    css_selector.insert(0, "html")
    return " > ".join(css_selector)

# no mixin-object for WebElement -> direct settattr
setattr(utils_seleniumxp._WebElement, "get_css_selector_from_xpath", get_css_selector)
setattr(utils_seleniumxp._WebElement, "get_css_selector", get_css_selector)


# webelement - check if element is present

# check if child webelement is present
# w/o optimization pretty slow, optimization uses XPATH to webelement
def is_present(
    webelement: utils_seleniumxp._WebElement, by: utils_seleniumxp.By, value: str, use_parsel: bool = True
) -> bool:
    """
    is_present - check if child webelement is present

    Args:
        webelement (utils_seleniumxp._WebElement): webelement
        by (utils_seleniumxp.By): locator type
        value (str): locator value
        use_parsel (bool, optional): flag to use parsel. Defaults to True

    Returns:
        bool: flag if element is present or not
    """

    if use_parsel and by in {utils_seleniumxp.By.XPATH, utils_seleniumxp.By.CSS_SELECTOR}:
        xpath = webelement.get_xpath()
        value = xpath + "/" + value if by == utils_seleniumxp.By.XPATH else cssify.cssify(xpath) + " > " + value
        parsedhtml = utils_seleniumxp.parselSelectorExtension(text=webelement.parent.page_source)
        return len(parsedhtml.css_or_xpath(utils_seleniumxp.SeleniumLocator(by, value)).getall()) > 0
    else:
        try:
            webelement.find_element(by, value)
        except Exception:
            return False
        else:
            return True

def is_element_present(webelement: utils_seleniumxp._WebElement, by: utils_seleniumxp.By, value: str, use_parsel: bool = True) -> bool:
    """
    is_element_present - check if child webelement is present (alternative caller to is_present)
    """
    return is_present(webelement, by, value, use_parsel)

# no mixin-object for WebElement -> direct settattr
setattr(utils_seleniumxp._WebElement, "is_present", is_present)
setattr(utils_seleniumxp._WebElement, "is_element_present", is_present)


# webelement - check for overlap, get overlapping element
# inspired by https://stackoverflow.com/questions/49921128/selenium-cant-click-element-because-other-element-obscures-it/72361846#72361846

# check for overlap
def is_overlapped(webelement: utils_seleniumxp._WebElement) -> bool:
    """
    is_overlapped -  check if element is overlapped

    Args:
        webelement (utils_seleniumxp._WebElement): webelement

    Return:
        bool: element is overlapped
    """

    check_element = get_overlapping_element(webelement)
    return not (check_element is None or check_element == webelement)

# no mixin-object for WebElement -> direct settattr
setattr(utils_seleniumxp._WebElement, "is_overlapped", is_overlapped)

# get overlapping element
def get_overlapping_element(webelement: utils_seleniumxp._WebElement) -> utils_seleniumxp._WebElement:
    """
    get_overlapping_element - get overlapping element

    Args:
        webelement (utils_seleniumxp._WebElement): webelement

    Return:
        utils_seleniumxp._WebElement: overlapping webelement
    """

    rect = webelement.rect
    result = webelement.parent.execute_script("return document.elementFromPoint(arguments[0], arguments[1]);", rect['x'] + rect['width'] // 2, rect['y'] + rect['height'] // 2)
    if result == webelement:
        result = None
    return result

# no mixin-object for WebElement -> direct settattr
setattr(utils_seleniumxp._WebElement, "get_overlapping_element", get_overlapping_element)


# webelement - clear & send_keys

# clear element and send keys
def clear_and_send_keys(webelement: utils_seleniumxp._WebElement, value: str) -> None:
    """
    clear_and_send_keys - clear element and send keys to it (combine simple calls)

    Args:
        webelement (utils_seleniumxp._WebElement): webelement
        value (str): value for send_keys
    """

    webelement.clear()
    webelement.send_keys(value)

# no mixin-object for WebElement -> direct settattr
setattr(utils_seleniumxp._WebElement, "clear_and_send_keys", clear_and_send_keys)
