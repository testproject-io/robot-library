# Copyright 2018 TestProject LTD. and/or its affiliates
# and other contributors as indicated by the @author tags.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from TestProjectLibrary import definitions

from src.testproject.sdk.drivers import webdriver
from selenium.webdriver import DesiredCapabilities, ChromeOptions, FirefoxOptions, IeOptions
from SeleniumLibrary import SeleniumLibrary
from robot.api.deco import keyword
from robot.api import logger
from SeleniumLibrary.keywords.webdrivertools import WebDriverCreator
from selenium.webdriver.edge.options import Options

import os
import inspect
import warnings
import datetime
from typing import Optional, Union


class TestProjectLibrary:
    # CONSTANTS #
    ACCEPT = "ACCEPT"
    ROBOT_LIBRARY_SCOPE = "GLOBAL"
    ROBOT_LISTENER_API_VERSION = 3
    CHROME_NAMES = ["googlechrome", "chrome", "gc"]
    FIREFOX_NAMES = ["firefox", "ff"]
    IE_NAMES = ["internetexplorer", "ie"]
    # CONSTANTS END #

    def __init__(self):
        self.ROBOT_LIBRARY_LISTENER = self
        self.__default_screenshot_name = f'TestProject-{datetime.date.today().strftime("%Y_%m_%d_%H_%M_%S")}.png'
        self.__reporter = None
        self.__library = SeleniumLibrary()
        self.__is_generic = False
        os.environ["RFW_SUPPRESS_WARNINGS"] = "true"

    # TESTPROJECT #
    @keyword
    def init_testproject_driver(
        self,
        browser: str = "firefox",
        url: Optional[str] = None,
        timeout: Optional[int] = 5000,
        project_name: Optional[str] = "TestProject Robot",
        job_name: Optional[str] = "Robot Job",
        desired_capabilities: Union[str, dict, None] = None,
        disabled_reports: Optional[bool] = False,
        dev_token: Optional[str] = os.getenv("TP_DEV_TOKEN"),
    ):
        logger.console(f"Initializing TestProject Library for Robot v{definitions.get_lib_version()}...")

        # # Make sure development token is set
        # if not dev_token:
        #     BuiltIn().fatal_error(
        #         "******************************************************************************\n"
        #         "* TestProject Development token not set!                                     *\n"
        #         "* Please use the 'dev_token' argument of the 'init_testproject_driver'       *\n"
        #         "* keyword, or set the 'TP_DEV_TOKEN' environment variable.                   *\n"
        #         "******************************************************************************"
        #     )

        driver = None
        # Check if instance of Options to pass to the driver.
        if not isinstance(desired_capabilities, (ChromeOptions, FirefoxOptions, IeOptions)):
            desired_capabilities = self._build_capabilities(
                WebDriverCreator(os.getcwd())._parse_capabilities(capabilities=desired_capabilities, browser=browser), browser
            )
        # If headless, override and start a clean headless session.
        if "headless" in browser:
            type = browser.split("headless", 1)[1]
            if type == "chrome":
                desired_capabilities = ChromeOptions()
            elif type == "firefox":
                desired_capabilities = FirefoxOptions()
            else:
                raise ValueError("Headless is supported for FireFox and Chrome only")
            desired_capabilities.add_argument("--headless")
            browser = type
        if browser in self.FIREFOX_NAMES:
            driver = webdriver.Firefox(
                firefox_options=desired_capabilities,
                token=dev_token,
                projectname=project_name,
                jobname=job_name,
                disable_reports=disabled_reports,
            )
        elif browser in self.CHROME_NAMES:
            driver = webdriver.Chrome(
                chrome_options=desired_capabilities,
                token=dev_token,
                projectname=project_name,
                jobname=job_name,
                disable_reports=disabled_reports,
            )
        elif browser in self.IE_NAMES:
            driver = webdriver.Ie(
                ie_options=desired_capabilities,
                token=dev_token,
                projectname=project_name,
                jobname=job_name,
                disable_reports=disabled_reports,
            )
        elif browser == "edge":
            driver = webdriver.Edge(
                edge_options=desired_capabilities,
                token=dev_token,
                projectname=project_name,
                jobname=job_name,
                disable_reports=disabled_reports,
            )
        elif browser == "safari":
            driver = webdriver.Safari(
                desired_capabilities=desired_capabilities,
                token=dev_token,
                projectname=project_name,
                jobname=job_name,
                disable_reports=disabled_reports,
            )
        elif browser == "generic":
            driver = webdriver.Generic(
                token=dev_token,
                projectname=project_name,
                jobname=job_name,
                disable_reports=disabled_reports
            )
            self.__is_generic = True
        else:
            raise ValueError("Unsupported Browser, please look at the official TestProject library documentation")

        # Set browser and timeout only if the driver is not generic
        if not self.__is_generic:
            driver.report().disable_command_reports(True)
            driver.set_script_timeout(timeout)
            driver.report().step(
                message="Set timeout",
                description=f"Time out was set to {timeout} millisecond",
                passed=True
            )
            try:
                driver.get(url)
                driver.report().step(
                    message=f"Navigated to {url}",
                    description=f"Successfully navigated to {url}",
                    passed=True
                )
            except Exception:
                driver.report().step(message=f"Failed to open {url}", description=f"Failed to open {url}", passed=True)
                raise
            self.__library.register_driver(driver=driver, alias="testproject_driver")
        else:
            driver.report().step(
                message="Generic Driver",
                description="New session created",
                passed=True,
                screenshot=False
            )

        self.__reporter = driver.report()
        self.__reporter.exclude_test_names(["run_cli", "main"])

    def _build_capabilities(self, caps, browser_name):
        options = None
        if caps:
            _, value = caps.popitem()
            try:
                browser = value["browserName"]
            except Exception as e:
                logger.console("No browser name capability was set")
                raise e
            if browser in self.FIREFOX_NAMES:
                options = FirefoxOptions()
            elif browser in self.CHROME_NAMES:
                options = ChromeOptions()
            elif browser in self.IE_NAMES:
                options = IeOptions()
            elif browser == "edge":
                options = Options()
            elif browser == "safari":
                options = DesiredCapabilities.SAFARI.copy()
            for k, v in value.items():
                options.set_capability(k, v)
        else:
            if browser_name in self.FIREFOX_NAMES:
                caps = DesiredCapabilities.FIREFOX.copy()
                options = FirefoxOptions()
            elif browser_name in self.CHROME_NAMES:
                caps = DesiredCapabilities.CHROME.copy()
                options = ChromeOptions()
            elif browser_name in self.IE_NAMES:
                caps = DesiredCapabilities.INTERNETEXPLORER.copy()
                options = IeOptions()
            elif browser_name == "edge":
                caps = DesiredCapabilities.EDGE.copy()
                options = Options()
            elif browser_name == "safari":
                options = DesiredCapabilities.SAFARI.copy()
            for k, v in caps.items():
                options.set_capability(k, v)
        return options

    # TESTPROJECT END #

    # SELECT/UNSELECT #

    @keyword
    def select_from_list_by_value(self, xpath, *values):
        self.base(xpath, f'Values selected: "{values}"', f' Values:"{xpath}", List: "{values}"', *values)

    @keyword
    def select_all_from_list(self, locator):
        self.base(locator, f'Selected all values from "{locator}"', f'"{locator}"')

    @keyword
    def select_from_list_by_label(self, locator, *labels):
        self.base(locator, f'Selected labels "{labels}"', f'Labels:"{locator}", List: "{labels}"', *labels)

    @keyword
    def unselect_all_from_list(self, locator):
        self.base(locator, f'Unselected all from "{locator}"', f'"{locator}"')

    @keyword
    def unselect_from_list_by_index(self, locator, *indexes):
        self.base(locator, f'Unselected "{indexes}" from "{locator}"', f"Indexes: {indexes}, List: {locator}", *indexes)

    @keyword
    def unselect_from_list_by_value(self, locator, *values):
        self.base(locator, f'Unselected "{values}" from "{locator}"', f"Values: {values}, List: {locator}", *values)

    @keyword
    def unselect_from_list_by_label(self, locator, *labels):
        self.base(locator, f'Unselected "{labels}" from "{locator}"', f"Labels: {labels}, List: {locator}", *labels)

    @keyword
    def get_selected_list_label(self, locator):
        return self.base(locator, "label", f"List: {locator}")

    @keyword
    def get_selected_list_labels(self, locator):
        return self.base(locator, "labels", f"List: {locator}")

    @keyword
    def get_selected_list_value(self, locator):
        return self.base(locator, "value", f"List: {locator}")

    @keyword
    def get_selected_list_values(self, locator):
        return self.base(locator, "values", f"List: {locator}")

    @keyword
    def get_list_items(self, locator, values=False):
        return self.base(locator, "list items", f"List: {locator}", values)

    @keyword
    def list_selection_should_be(self, locator, *expected):
        self.base(locator, f'Selection is "{expected}"', f"List: {locator}", *expected)

    @keyword
    def list_should_have_no_selections(self, locator):
        self.base(locator, f'List "{locator}" has no selections', f"List: {locator}")

    @keyword
    def page_should_not_contain_list(self, locator, message=None, loglevel="TRACE"):
        self.base(locator, "List is not in page", f"List: {locator}", message, loglevel)

    @keyword
    def page_should_contain_list(self, locator, message=None, loglevel="TRACE"):
        self.base(locator, "List is in page", f"List: {locator}", message, loglevel)

    # SELECT/UNSELECT END #

    # SCREENSHOTS #
    @keyword
    def capture_page_screenshot(self, filename=None):
        if not filename:  # Generate default file name with time stamp
            filename = self.__default_screenshot_name
        return self.base("", "Screenshot captured file", f" {filename}", filename)

    @keyword
    def set_screenshot_directory(self, path):
        self.base("", "previous set directory", f" {path}", path)

    @keyword
    def capture_element_screenshot(self, locator, filename=None):
        if not filename:
            filename = self.__default_screenshot_name
        return self.base(locator, "element screenshot file", f"{filename}", filename)

    # SCREENSHOTS END #

    # ELEMENTS #
    @keyword(name="Get WebElement")
    def get_webelement(self, locator):
        return self.base(locator, "first web element by the given locator", f" {locator}")

    @keyword(name="Get WebElements")
    def get_webelements(self, locator):
        return self.base(locator, "list of web elements by the given locator", f" {locator}")

    @keyword
    def element_should_contain(self, locator, expected, message=None, ignore_case=False):
        self.base(locator, f'Element contains "{expected}"', f" {locator}", expected, message, ignore_case)

    @keyword
    def element_should_not_contain(self, locator, expected, message=None, ignore_case=False):
        self.base(locator, f'Element does not contain "{expected}"', f" {locator}", expected, message, ignore_case)

    @keyword
    def page_should_contain_element(self, locator, message=None, loglevel="TRACE", limit=None):
        return self.base(locator, f'Page contains "{locator}"', f" {locator}", message, loglevel, limit)

    @keyword
    def page_should_contain(self, text, loglevel="TRACE"):
        self.base("", f'Page contains "{text}"', f" {text}", text, loglevel)

    @keyword
    def locator_should_match_x_times(self, locator, x, message=None, loglevel="TRACE"):
        self.base(locator, f'"{locator}" matched "{x}"', f"Locator: {locator}, X: {x}", x, message, loglevel)

    @keyword
    def page_should_not_contain(self, text, loglevel="TRACE"):
        self.base("", f'Page did not contain "{text}"', f" {text}", text, loglevel)

    @keyword
    def page_should_not_contain_element(self, locator, message=None, loglevel="TRACE"):
        self.base(locator, f'Page did not contain "{locator}"', f" {locator}", message, loglevel)

    @keyword
    def assign_id_to_element(self, locator, id):
        self.base(locator, f'ID was assigned to "{id}"', f" {locator}", id)

    @keyword
    def element_should_be_disabled(self, locator):
        self.base(locator, "Element is disabled", f" {locator}")

    @keyword
    def element_should_be_enabled(self, locator):
        self.base(locator, "Element is enabled", f" {locator}")

    @keyword
    def element_should_be_focused(self, locator):
        self.base(locator, "Element is focused", f" {locator}")

    @keyword
    def element_should_be_visible(self, locator, message=None):
        self.base(locator, "Element is visible", f" {locator}", message)

    @keyword
    def element_should_not_be_visible(self, locator, message=None):
        self.base(locator, "Element is not visible", f" {locator}", message)

    @keyword
    def element_text_should_be(self, locator, expected, message=None, ignore_case=False):
        self.base(locator, f'Text is "{expected}"', f"Element: {locator}, Text: {expected}", expected, message, ignore_case)

    @keyword
    def element_text_should_not_be(self, locator, not_expected, message=None, ignore_case=False):
        self.base(
            locator,
            f'Text is not "{not_expected}"',
            f"Element: {locator}, Text: {not_expected}",
            not_expected,
            message,
            ignore_case,
        )

    @keyword
    def get_element_attribute(self, locator, attribute):
        return self.base(locator, "attribute", f"Element: {locator}", attribute)

    @keyword
    def element_attribute_value_should_be(self, locator, attribute, expected, message=None):
        self.base(
            locator,
            f'Attribute "{attribute}" contains {expected}',
            f"Element: {locator}, Attribute: {expected}",
            attribute,
            expected,
            message,
        )

    @keyword
    def get_horizontal_position(self, locator):
        return self.base(locator, "Horizontal position", f" {locator}")

    @keyword
    def get_element_size(self, locator):
        return self.base(locator, "size", f"Element: {locator}")

    @keyword
    def cover_element(self, locator):
        self.base(locator, f'Element Covered "{locator}"', f" {locator}")

    @keyword
    def get_value(self, locator):
        return self.base(locator, "value", f" {locator}")

    @keyword
    def get_text(self, locator):
        return self.base(locator, "Text", f" {locator}")

    @keyword
    def clear_element_text(self, locator):
        self.base(locator, "Text cleared", f" {locator}")

    @keyword
    def get_vertical_position(self, locator):
        return self.base(locator, "vertical position", f" {locator}")

    @keyword
    def click_button(self, locator, modifier=False):
        self.base(locator, f'Clicked button "{locator}"', f" {locator}", modifier)

    @keyword
    def click_image(self, locator, modifier=False):
        self.base(locator, f'Clicked image "{locator}"', f" {locator}", modifier)

    @keyword
    def click_link(self, locator, modifier=False):
        self.base(locator, f'Clicked link "{locator}"', f" {locator}", modifier)

    @keyword
    def click_element(self, locator, modifier=False, action_chain=False):
        self.base(locator, f'Clicked "{locator}"', f" {locator}", modifier, action_chain)

    @keyword
    def click_element_at_coordinates(self, locator, xoffset, yoffset):
        self.base(locator, f'Clicked "{locator}" at X:{xoffset} , Y:{yoffset}', f" {locator}", xoffset, yoffset)

    @keyword
    def double_click_element(self, locator):
        self.base(self, f'Double clicked "{locator}"', f" {locator}")

    @keyword
    def set_focus_to_element(self, locator):
        self.base(locator, f'Element "{locator}" was is focused', f" {locator}")

    @keyword
    def scroll_element_into_view(self, locator):
        self.base(locator, f'Element "{locator}" was scrolled into view', f" {locator}")

    @keyword
    def drag_and_drop(self, locator, target):
        self.base(locator, f'Element "{locator}" was dragged to "{target}"', f"Origin: {locator}, Target: {target}", target)

    @keyword
    def drag_and_drop_by_offset(self, locator, xoffset, yoffset):
        self.base(locator, f'Element "{locator}" was dragged to X:{xoffset} , Y:{yoffset}', f" {locator}", xoffset, yoffset)

    @keyword
    def mouse_down(self, locator):
        self.base(locator, f'Mouse down on: "{locator}"', f" {locator}")

    @keyword
    def mouse_out(self, locator):
        self.base(locator, f'Mouse out on: "{locator}"', f" {locator}")

    @keyword
    def mouse_over(self, locator):
        self.base(locator, f'Mouse over on: "{locator}"', f" {locator}")

    @keyword
    def mouse_up(self, locator):
        self.base(locator, f'Mouse up on: "{locator}"', f" {locator}")

    @keyword
    def open_context_menu(self, locator):
        self.base(locator, f'Context menu opened on: "{locator}"', f" {locator}")

    @keyword
    def simulate_event(self, locator, event):
        self.base(locator, f'Event: "{event}" was simulated on {locator}', f"Element: {locator}, Event: {event}", event)

    @keyword
    def press_key(self, locator, key):
        self.base(locator, f'Key pressed: "{key}"', f"Locator: {locator}, Key: {key}", key)

    @keyword
    def press_keys(self, locator=None, *keys):
        self.base(locator, f'Keys pressed: "{keys}"\non element found at "{locator}"', f"{keys}", keys)

    @keyword
    def get_all_links(self):
        return self.base("", "links", "")

    @keyword
    def mouse_down_on_link(self, locator):
        self.base(locator, f'Mouse was pressed on "{locator}"', f" {locator}")

    @keyword
    def page_should_contain_link(self, locator, message=None, loglevel="TRACE"):
        self.base(locator, 'Page did contain link in "{}"', f" {locator}", message, loglevel)

    @keyword
    def page_should_not_contain_link(self, locator, message=None, loglevel="TRACE"):
        self.base(locator, f'Page did not contain link in "{locator}"', f" {locator}", message, loglevel)

    @keyword
    def mouse_down_on_image(self, locator):
        self.base(locator, f'Mouse was down on image found at "{locator}"', f" {locator}")

    @keyword
    def page_should_contain_image(self, locator, message=None, loglevel="TRACE"):
        self.base(locator, f'Page did contain "{locator}"', f" {locator}", message, loglevel)

    @keyword
    def page_should_not_contain_image(self, locator, message=None, loglevel="TRACE"):
        self.base(locator, f'Page did not contain "{locator}"', f" {locator}", message, loglevel)

    @keyword
    def get_element_count(self, locator):
        return self.base(locator, f'element "{locator}" count', f"Element: {locator}")

    @keyword
    def add_location_strategy(self, strategy_name, strategy_keyword, persist=False):
        self.base("", f"Strategy '{strategy_name} was added'", strategy_name, strategy_keyword, persist)

    @keyword
    def remove_location_strategy(self, strategy_name):
        self.base("", f"Strategy '{strategy_name}' was removed", f"Removed {strategy_name}", strategy_name)

    # ELEMENTS END #

    # ALERTS #
    @keyword
    def input_text_into_alert(self, text, action=ACCEPT, timeout=None):
        self.base("", f"Typed {text} into alert\nAction used: {action}", f"Text: {text}", text, action, timeout)

    @keyword
    def alert_should_be_present(self, text="", action=ACCEPT, timeout=None):
        self.base("", f"Action used: {action}", "", text, action, timeout)

    @keyword
    def alert_should_not_be_present(self, action=ACCEPT, timeout=0):
        self.base("", f"Action used: {action}", "", action, timeout)

    @keyword
    def handle_alert(self, action=ACCEPT, timeout=None):
        return self.base("", f"Alert handled with action: {action}", "", action, timeout)

    # ALERTS END #

    # COOKIES #
    @keyword
    def delete_all_cookies(self):
        self.base("", "Deleted all cookies", "")

    @keyword
    def delete_cookie(self, name):
        self.base("", "Deleted all cookies", f"{name}", name)

    @keyword
    def get_cookies(self, as_dict=False):
        return self.base("", "Cookies", "", as_dict)

    @keyword
    def get_cookie(self, name):
        return self.base("", "Cookie", f"{name}", name)

    @keyword
    def add_cookie(self, name, value, path=None, domain=None, secure=None, expiry=None):
        self.base("", f"Added cookie: {name} with value: {value}", f"{name}", name, value, path, domain, secure, expiry)

    # COOKIES END #

    # JAVASCRIPT #
    @keyword
    def execute_javascript(self, *code):
        return self.base("", f"Executed {code}", f"{code}", *code)

    @keyword
    def execute_async_javascript(self, *code):
        return self.base("", f"Executed {code} Asynchronously", f"{code}", *code)

    # JAVASCRIPT END #

    # RUN ON FAILURE #
    @keyword
    def register_keyword_to_run_on_failure(self, keyword):
        return self.base("", "Previous keyword", f"{keyword}", keyword)

    # RUN ON FAILURE END #

    # TABLE ELEMENT #
    @keyword
    def get_table_cell(self, locator, row, column, loglevel="TRACE"):
        return self.base(locator, "Cell text", f"{locator} at Row: {row}, Col: {column}", row, column, loglevel)

    @keyword
    def table_cell_should_contain(self, locator, row, column, expected, loglevel="TRACE"):
        self.base(
            locator,
            f"Cell at row: {row} and column {column} contained {expected}",
            f"{locator} at Row: {row}, Col: {column}",
            row,
            column,
            expected,
            loglevel,
        )

    @keyword
    def table_column_should_contain(self, locator, column, expected, loglevel="TRACE"):
        self.base(locator, f"Column {column} contained {expected}", f"{locator} Col: {column}", column, expected, loglevel)

    @keyword
    def table_footer_should_contain(self, locator, expected, loglevel="TRACE"):
        self.base(locator, f"Footer contained {expected}", f"Footer: {locator}, Expected: {expected}", expected, loglevel)

    @keyword
    def table_header_should_contain(self, locator, expected, loglevel="TRACE"):
        self.base(locator, f"Header contained {expected}", f"Header: {locator}, Expected: {expected}", expected, loglevel)

    @keyword
    def table_row_should_contain(self, locator, row, expected, loglevel="TRACE"):
        self.base(locator, f"Row {row} contained {expected}", f"{locator} Row: {row}", row, expected, loglevel)

    @keyword
    def table_should_contain(self, locator, expected, loglevel="TRACE"):
        self.base(locator, f"Table contained {expected}", f"Table: {locator}, Expected: {expected}", expected, loglevel)

    # TABLE ELEMENT END #

    # WAITING #
    @keyword
    def wait_for_condition(self, condition, timeout=None, error=None):
        message = self._set_message(timeout)
        self.base("", f"Condition: '{condition}' was met {message}", f"{condition}", condition, timeout, error)

    @keyword
    def wait_until_location_is(self, expected, timeout=None, message=None):
        message = self._set_message(timeout)
        self.base("", f"Location was '{expected}' {message}", f"{expected}", expected, timeout, message)

    @keyword
    def wait_until_location_is_not(self, location, timeout=None, message=None):
        message = self._set_message(timeout)
        self.base("", f"Location was not '{location}' {message}", f"{location}", location, timeout, message)

    @keyword
    def wait_until_location_contains(self, expected, timeout=None, message=None):
        message = self._set_message(timeout)
        self.base("", f"Location contained '{expected}' {message}", f"{expected}", expected, timeout, message)

    @keyword
    def wait_until_location_does_not_contain(self, location, timeout=None, message=None):
        message = self._set_message(timeout)
        self.base("", f"Location does not contain '{location}' {message}", f"{location}", location, timeout, message)

    @keyword
    def wait_until_page_contains(self, text, timeout=None, error=None):
        message = self._set_message(timeout)
        self.base("", f"Page contained '{text}' {message}", f" {text}", text, timeout, error)

    @keyword
    def wait_until_page_does_not_contain(self, text, timeout=None, error=None):
        message = self._set_message(timeout)
        self.base("", f"Page does not contain '{text}' {message}", f" {text}", text, timeout, error)

    @keyword
    def wait_until_page_contains_element(self, locator, timeout=None, error=None, limit=None):
        message = self._set_message(timeout)
        self.base(locator, f"Page contained '{locator}' {message}", f" {locator}", timeout, error, limit)

    @keyword
    def wait_until_page_does_not_contain_element(self, locator, timeout=None, error=None, limit=None):
        message = self._set_message(timeout)
        self.base(locator, f"Page does not contain '{locator}' {message}", f" {locator}", timeout, error, limit)

    @keyword
    def wait_until_element_is_visible(self, locator, timeout=None, error=None):
        message = self._set_message(timeout)
        self.base(locator, f"Element '{locator}' was visible {message}", f" {locator}", timeout, error)

    @keyword
    def wait_until_element_is_not_visible(self, locator, timeout=None, error=None):
        message = self._set_message(timeout)
        self.base(locator, f"Element '{locator}' was not visible {message}", f" {locator}", timeout, error)

    @keyword
    def wait_until_element_is_enabled(self, locator, timeout=None, error=None):
        message = self._set_message(timeout)
        self.base(locator, f"Element '{locator}' was enabled {message}", f" {locator}", timeout, error)

    @keyword
    def wait_until_element_contains(self, locator, text, timeout=None, error=None):
        message = self._set_message(timeout)
        self.base(locator, f"Element '{locator}' contained {text} {message}", f" {text}", text, timeout, error)

    @keyword
    def wait_until_element_does_not_contain(self, locator, text, timeout=None, error=None):
        message = self._set_message(timeout)
        self.base(locator, f"Element '{locator}' does not contain {text} {message}", f" {text}", text, timeout, error)

    def _set_message(self, timeout):
        return "" if timeout is None else f"(timeout: {timeout} seconds)"

    # WAITING END #

    # WINDOW #
    @keyword
    def select_window(self, locator="MAIN", timeout=None):
        return self.base(locator, f"Switched to {locator}", "", timeout)

    @keyword
    def switch_window(self, locator="MAIN", timeout=None, browser="CURRENT"):
        return self.base(locator, f"Switched to {locator}", f"{browser}", timeout, browser)

    @keyword
    def close_window(self):
        self.base("", "Window closed", "")

    @keyword
    def get_window_handles(self, browser="CURRENT"):
        return self.base("", "Window Handles", "", browser)

    @keyword
    def get_window_identifiers(self, browser="CURRENT"):
        return self.base("", "Window Identifiers", "", browser)

    @keyword
    def get_window_names(self, browser="CURRENT"):
        return self.base("", "Window Names", "", browser)

    @keyword
    def get_window_titles(self, browser="CURRENT"):
        return self.base("", "Window Titles", "", browser)

    @keyword
    def get_locations(self, browser="CURRENT"):
        return self.base("", "All Locations", "", browser)

    @keyword
    def maximize_browser_window(self):
        self.base("", "Window Maximized", "")

    @keyword
    def get_window_size(self, inner=False):
        return self.base("", "Window size", "", inner)

    @keyword
    def set_window_size(self, width, height, inner=False):
        self.base("", f"Size set to {width}, {height}", f"Width: {width}, Height: {height}", width, height, inner)

    @keyword
    def get_window_position(self):
        return self.base("", "Window position", "")

    @keyword
    def set_window_position(self, x, y):
        self.base("", f"Position set to {x}, {y}", f"X: {x}, Y: {y}", x, y)

    # WINDOW END #

    # FRAMES #
    @keyword
    def select_frame(self, locator):
        self.base(locator, f"Switched from to {locator}", f"{locator}")

    @keyword
    def unselect_frame(self):
        self.base("", "Returned to main frame", "")

    @keyword
    def current_frame_should_contain(self, text, loglevel="TRACE"):
        self.base("", f"Current frame contains {text}", f"{text}", text, loglevel)

    @keyword
    def current_frame_should_not_contain(self, text, loglevel="TRACE"):
        self.base("", f"Current frame does not contain {text}", f"{text}", text, loglevel)

    @keyword
    def frame_should_contain(self, locator, text, loglevel="TRACE"):
        self.base(locator, f"{locator} contains {text}", f"Frame: {locator}, Text: {text}", text, loglevel)

    # FRAMES END #

    # FORM ELEMENT #
    @keyword
    def submit_form(self, locator=None):
        self.base(locator, "Form submitted", f"{locator}")

    @keyword
    def checkbox_should_be_selected(self, locator):
        self.base(locator, f"Checked box {locator} is selected", f"{locator}")

    @keyword
    def checkbox_should_not_be_selected(self, locator):
        self.base(locator, f"Checked box {locator} is not selected", f"{locator}")

    @keyword
    def page_should_contain_checkbox(self, locator, message=None, loglevel="TRACE"):
        self.base(locator, f"Page contains checkbox {locator}", f"{locator}", message, loglevel)

    @keyword
    def page_should_not_contain_checkbox(self, locator, message=None, loglevel="TRACE"):
        self.base(locator, f"Page does not contain checkbox {locator}", f"{locator}", message, loglevel)

    @keyword
    def select_checkbox(self, locator):
        self.base(locator, "Checkbox selected", f"{locator}")

    @keyword
    def unselect_checkbox(self, locator):
        self.base(locator, "Checkbox unselected", f"{locator}")

    @keyword
    def page_should_contain_radio_button(self, locator, message=None, loglevel="TRACE"):
        self.base(locator, f"Page contains radio button {locator}", f"{locator}", message, loglevel)

    @keyword
    def page_should_not_contain_radio_button(self, locator, message=None, loglevel="TRACE"):
        self.base(locator, f"Page does not contain radio button {locator}", f"{locator}", message, loglevel)

    @keyword
    def radio_button_should_be_set_to(self, group_name, value):
        self.base("", f"{group_name} was set to {value}", f"{value}", group_name, value)

    @keyword
    def radio_button_should_not_be_selected(self, group_name):
        self.base("", f"{group_name} was not selected", f"{group_name}", group_name)

    @keyword
    def select_radio_button(self, group_name, value):
        self.base("", f"{group_name} was set to {value}", f"{value}", group_name, value)

    @keyword
    def choose_file(self, locator, file_path):
        self.base(locator, f"File {file_path} was uploaded", f"{locator}", file_path)

    @keyword
    def input_password(self, locator, password, clear=True):
        self.base(locator, f"Typed {password} to {locator}", f"{password}", password, clear)

    @keyword
    def input_text(self, locator, text, clear=True):
        self.base(locator, f"Typed {text} to {locator}", f"{text}", text, clear)

    @keyword
    def page_should_contain_textfield(self, locator, message=None, loglevel="TRACE"):
        self.base(locator, f"Page contains TextField {locator}", f"{locator}", message, loglevel)

    @keyword
    def page_should_not_contain_textfield(self, locator, message=None, loglevel="TRACE"):
        self.base(locator, f"Page does not contain TextField {locator}", f"{locator}", message, loglevel)

    @keyword
    def textfield_should_contain(self, locator, expected, message=None):
        self.base(locator, f"TextField {locator} contains  {expected}", f"{expected}", expected, message)

    @keyword
    def textfield_value_should_be(self, locator, expected, message=None):
        self.base(locator, f"TextField {locator} value is {expected}", f"{expected}", expected, message)

    @keyword
    def textarea_should_contain(self, locator, expected, message=None):
        self.base(locator, f"TextArea {locator} contains {expected}", f"{expected}", expected, message)

    @keyword
    def textarea_value_should_be(self, locator, expected, message=None):
        self.base(locator, f"TextArea {locator} value is {expected}", f"{expected}", expected, message)

    @keyword
    def page_should_contain_button(self, locator, message=None, loglevel="TRACE"):
        self.base(locator, f"Page contains button {locator}", f"{locator}", message, loglevel)

    @keyword
    def page_should_not_contain_button(self, locator, message=None, loglevel="TRACE"):
        self.base(locator, f"Page does not contain button {locator}", f"{locator}", message, loglevel)

    # FORM ELEMENT END #

    # BROWSER MANAGEMENT #
    @keyword
    def open_browser(self, url=None):
        if not self.__reporter:
            self.__reporter.step(
                description="Open Browser",
                message="This step is deprecated using TestProject library",
                passed=True,
                screenshot=False,
            )

        warnings.warn(
            "This is deprecated using TestProject Library, please look at the official documentation for examples.",
            DeprecationWarning,
            stacklevel=2,
        )
        logger.console("'Open Browser' is deprecated using TestProject Library, please see official documentation.")

    @keyword
    def switch_browser(self, index_or_alias):
        self.base("", f"Switched to {index_or_alias}", f"{index_or_alias}", index_or_alias)

    @keyword
    def get_browser_ids(self):
        return self.base("", "Browser Ids", "")

    @keyword
    def get_browser_aliases(self):
        return self.base("", "Browser Aliases", "")

    @keyword
    def get_session_id(self):
        return self.base("", "Session ID", "")

    @keyword
    def get_source(self):
        return self.base("", "Page Source", "")

    @keyword
    def get_title(self):
        return self.base("", "Page Title", "")

    @keyword
    def get_location(self):
        return self.base("", "Window URL", "")

    @keyword
    def location_should_be(self, url, message=None):
        self.base("", f"URL is: {url}", f"{url}", url, message)

    @keyword
    def location_should_contain(self, expected, message=None):
        self.base("", f"URL contains: {expected}", f"{expected}", expected, message)

    @keyword
    def log_location(self):
        return self.base("", "Location and logged it", "")

    @keyword
    def log_source(self, loglevel="INFO"):
        return self.base("", "Source and logged it", "", loglevel)

    @keyword
    def log_title(self):
        return self.base("", "Title and logged it", "")

    @keyword
    def title_should_be(self, title, message=None):
        return self.base("", f"Title is {title}", f"{title}", title, message)

    @keyword
    def go_back(self):
        self.base("", "Navigated Back", "")

    @keyword
    def go_to(self, url):
        self.base("", f"Navigated to {url}", f"{url}", url)

    @keyword
    def reload_page(self):
        self.base("", "Reloaded page", "")

    @keyword
    def get_selenium_speed(self):
        return self.base("", "Delay between each selenium command", "")

    @keyword
    def get_selenium_timeout(self):
        return self.base("", "Timeout between variuos keywords", "")

    @keyword
    def get_selenium_implicit_wait(self):
        return self.base("", "Implicit wait value", "")

    @keyword
    def set_selenium_speed(self, value):
        return self.base("", f"Selenium Speed set to {value}", f"{value}", value)

    @keyword
    def set_selenium_timeout(self, value):
        return self.base("", f"Timeout was set to {value}", f"{value}", value)

    @keyword
    def set_selenium_implicit_wait(self, value):
        return self.base("", f"Implicit wait set to {value}", f"{value}", value)

    @keyword
    def set_browser_implicit_wait(self, value):
        self.base("", f"Browser implicit wait set to {value}", f"{value}", value)

    @keyword
    def close_all_browsers(self):
        self.base("", "Closed all open browsers", "")

    @keyword
    def create_webdriver(self, driver_name, alias=None, kwargs={}, **init_kwargs):
        if not self.__reporter:
            self.__reporter.step(
                description="Create Webdriver",
                message="This step is deprecated using TestProject library",
                passed=True,
                screenshot=False,
            )

        warnings.warn(
            "This is deprecated using TestProject Library, please look at the offical documentation for examples.",
            DeprecationWarning,
            stacklevel=2,
        )
        logger.console("'Create WebDriver' is deprecated using TestProject Library, please see offical documentation.")

    # BROWSER MANAGEMENT END #

    # GENERIC #
    @keyword
    def create_step(self, description, message, passed=True, screenshot=False):
        self.__reporter.step(
            message=message,
            description=description,
            passed=passed,
            screenshot=False if self.__is_generic else screenshot
        )
    # GENERIC END#

    # UTIL METHODS #
    def base(self, *args):
        func_name = inspect.stack()[1].function
        locator, message, description = "N/A"
        try:
            locator = args[0]  # Get the locator of the element
            message = args[1]  # Get the message for the __reporter
            description = args[2]  # Get the description for the __reporter
            # Remove message,description and locator
            args_as_list = list(args)
            args = tuple(args_as_list[3:])
            value = self.base_keyword_action(locator, *args, func_name=func_name)
            if not value:
                self.base_report(True, message=message, func_name=func_name, description=description)
            else:
                self.base_report(True, message=f"Returned value: {value}", func_name=func_name, description=description)
            return value
        except Exception as e:
            self.base_report(success=False, exception=e, func_name=func_name, description=description)
            raise

    def build_values(self, locator, *values):
        result_list = []
        if locator:
            result_list.append(locator)

        result_list = result_list + list(values)
        return result_list

    def convert(self, word):
        return " ".join(x.capitalize() for x in word.split("_"))

    def base_report(self, success, message="", func_name="", screenshot=False, exception=None, description=None):
        if self.__reporter is None:
            return

        if not func_name:
            func_name = inspect.stack()[1].function
        func_name = self.convert(func_name)
        if success:
            self.__reporter.step(
                description=f"{func_name}: {description}", message=message, passed=True, screenshot=True
            )
        else:
            if not message:
                message += f"Failure reason:\n'{exception}'"
            self.__reporter.step(description=f"{func_name}: {description}", message=message, passed=False, screenshot=True)

    def base_keyword_action(self, locator, *values, func_name=""):
        try:
            ret_value = ""
            if not func_name:  # Get name of calling Keyword
                func_name = inspect.stack()[1].function
            if not locator and not values:
                ret_value = self.__library.run_keyword(func_name, (), {})
            elif not locator:
                ret_value = self.__library.run_keyword(func_name, self.build_values(None, *values), {})
            elif not values:
                if func_name == "get_webelements":
                    func_name = "Get WebElements"
                if func_name == "get_webelement":
                    func_name = "Get WebElement"
                ret_value = self.__library.run_keyword(func_name, [locator], {})
            else:
                ret_value = self.__library.run_keyword(func_name, self.build_values(locator, *values), {})
            return ret_value
        except Exception as e:
            raise e

    # UTIL METHODS END #

    # LISTENERS #
    def _end_test(self, data, result):
        if self.__reporter is None:
            return

        self.__reporter.test(name=result.name, passed=result.passed)

    # LISTENERS END #
