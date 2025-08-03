# ​SeleniumXP utilities for Python

## Short description

Package with utilities and functional extensions for Selenium webdriver Python language bindings

## Package content

The package consist of various helpers and extensions to the Selenium webdriver:

- module for session handling especially a custom factory function to initialize a webdriver object
- module with additional methods for the webdriver class
- module with convenience functions for locators
- module with additional methods for the webelement class
- an extended event-firing webdriver and an extended listener abstract base class
- a sample event listener implementation based on the extended abstract base class

Different from other packages extending the Selenium webdriver class does not work with
wrapping the original webdriver but providing a mixin class or alternatively directly setting
additional methods via 'setattr' in the original webdriver class. This is done and controlled
via a pretty versatile custom factory function initializing the webdriver.

The webelement extension are done via setattr only. Implementing a mixin class would require
to modify webdriver methods to return the new class with the mixin. So benefit of the
settattr approach is that extending the webelement class is independend from changes to the
webdriver class.

## Navigation

Documentation for specific `MAJOR.MINOR` versions can be chosen by using the dropdown on the top of every page.
The `dev` version reflects changes that have not yet been released. Shortcuts can be used for navigation, i.e.
<kbd>,</kbd>/<kbd>p</kbd> and <kbd>.</kbd>/<kbd>n</kbd> for previous and next page, respectively, as well as
<kbd>/</kbd>/<kbd>s</kbd> for searching.
