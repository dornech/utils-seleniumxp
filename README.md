# SeleniumXP utilities for Python

Package with utilities and functional extensions for Selenium webdriver Python language bindings

## Features

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

Note: as I am coming from camel case notation I was struggling a little bit with the Python naming conventions.
However, for publishing I tried to increase compliance with Python naming conventions and added snake case
method stubs (at least for most important subroutines) as a compromise.

## Development

To set up [hatch] and [pre-commit] for the first time:

1. install [hatch] globally, e.g. with [pipx], i.e. `pipx install hatch`,
2. make sure `pre-commit` is installed globally, e.g. with `pipx install pre-commit`.

A special feature that makes hatch very different from other familiar tools is that you almost never
activate, or enter, an environment. Instead, you use `hatch run env_name:command` and the `default` environment
is assumed for a command if there is no colon found. Thus you must always define your environment in a declarative
way and hatch makes sure that the environment reflects your declaration by updating it whenever you issue
a `hatch run ...`. This helps with reproducability and avoids forgetting to specify dependencies since the
hatch workflow is to specify everything directly in [pyproject.toml](pyproject.toml). Only in rare cases, you
will use `hatch shell` to enter the `default` environment, which is similar to what you may know from other tools.

To get you started, use `hatch run test:cov` or `hatch run test:no-cov` to run the unitest with or without coverage reports,
respectively. Use `hatch run lint:all` to run all kinds of typing and linting checks. Try to automatically fix linting
problems with `hatch run lint:fix` and use `hatch run docs:serve` to build and serve your documentation.
You can also easily define your own environments and commands. Check out the environment setup of hatch
in [pyproject.toml](pyproject.toml) for more commands as well as the package, build and tool configuration.

To support versioning and changelog generation please refer to the toolchain selected during package
generation (see also `pyproject.toml`). If not deselected, the toolchain includes a [pre-commit] hook
for linting commit messages to ensure commit messages are compliant with the conventional commit format and
support an automated changelog generation.

## Credits

This package was created with [The Hatchlor Enhanced] project template. This template is based on [The Hatchlor]
but was substantially improved.

[The Hatchlor Enhanced]: https://github.com/dornech/the-hatchlor-enhanced
[The Hatchlor]: https://github.com/florianwilhelm/the-hatchlor
[pipx]: https://pypa.github.io/pipx/
[hatch]: https://hatch.pypa.io/
[pre-commit]: https://pre-commit.com/
