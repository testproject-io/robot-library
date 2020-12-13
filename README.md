# TestProject Library for the Robot Framework

## What is the Robot framework

Robot Framework is a generic open source automation framework. It can be used for test automation and robotic process automation (RPA).

Robot Framework has easy syntax, utilizing human-readable keywords.\
Its capabilities can be extended by libraries implemented with Python or Java.\
The framework has a rich ecosystem around it, consisting of libraries and tools that are developed as separate projects.

## Why use the TestProject Library For Robot

TestProject offers a set of tools for creating end-to-end Tests.

1. TestProject Agent handles the deployment and configuration of Selenium/Appium.
1. Keeps you up to date with the latest stable versions of Selenium/Appium drivers.
1. Cloud team collaboration and automatic test reports (HTML/PDF/JSON).
1. Scriptless test recorder allows creating and running tests without a single line of code.
1. Code extract feature, which allows you to generate Selenium/Appium code to from your scripless tests.

By integrating this library with your Robot tests, you can enjoy all these advantages\
as well as fully automated reports (with screenshots) hosted free on the TestProject platform.

Combining the TestProject Library with Robot is as simple as using the Selenium Library.\
It's implementing the same syntax, replacing only the "Open Browser" keyword.

## Prerequisites

Before starting, please make sure to complete the following:

1. Login to or create a new (**FREE**) TestProject Account: [https://testproject.io/](https://testproject.io/)
2. Download and Install the TestProject Agent.
3. Register the Agent, and get your developer token from here: [https://app.testproject.io/#/integrations/sdk](https://app.testproject.io/#/integrations/sdk)
4. Install the Robot Framework: `pip3 install robotframework`
    > Or following the installation instructions [here](https://github.com/robotframework/robotframework/blob/master/INSTALL.rst).
5. Install the TestProject Library for Robot: `pip3 install testproject-robot-library`

## Create a new test using the TestProject Library for Robot

Now we will create a simple Robot test with two different "Login" flows.\
The first will be a valid flow and the second will use an incorrect password.

First we need to create a new Robot test file. Let's call this file `MyRobotTest.robot`\
Since we're going to use the TestProject Library for Robot, we must declare it inside the test:

```python
*** Settings ***
Library TestProjectLibrary
```

Once the TestProject Library for Robot is declared, we can use its full functionality.

Next we create a `Suite Setup` section for initializing the TestProject Driver:

```python
Suite Setup InitTestProject

*** Keywords ***
InitTestProject
    Init Testproject Driver     chrome      timeout=5000    job_name=TestProjectRobot
    Open Browser https://example.testproject.io/web/
```

In this snippet, we declare a custom Keyword named `InitTestProject` which creates a new session\
with the TestProject Agent, requesting to open a Selenium session on a Chrome browser.
> Under the `*** Keywords ***` section we can put all of our **custom keywords**.

**Init TestProject Driver** is the most important part of the TestProject Library for Robot.\
It communicates with the TestProject Agent and passed any Desired capabilities, browser type, timeouts and additional data that is required by the TestProject Agent.

> This method replaces the `Create Webdriver` and `Open Browser` keywords, and is the only difference between the SeleniumLibrary and the TestProject Library for Robot.

Since the TestProject Library for Robot was created as a wrapper for the SeleniumLibrary, you can simply\
take your existing Robot tests, replace the import of the `SeleniumLibrary` with `TestProjectLibrary`, \
call the `Init TestProject Driver` keyword and you are good to go!

The follow Selenium test:
```python
Library SeleniumLibrary

Open Browser browser=Chrome url=https://example.testproject.io/web/
Create Webdriver driver_name=Chrome
```

Changes to:
```python
Library TestProjectLibrary

Init Testproject Driver browser=Chrome url=https://example.testproject.io/web/
```

**That's it!**

## New Test Suite Using the TestProject Library for Robot

In this section, we will create a simple test suite with 4 tests:
1. Login with an incorrect password
1. Login with a correct password
1. Filling in a form with some details
1. Submitting the form

The suite is built to run on TestProject's example website: https://example.testproject.io/web

Here is the complete Robot test:
```python
*** Settings ***
Library     	TestProjectLibrary
Suite Setup     Init Session
Suite Teardown  Close Session

*** Test Cases ***
Set Session
    ${previous kw}=     Register Keyword To Run On Failure      None
Login With Incorrect Password
    Base Login          ${INCORRECT_PASSWORD}
Login With Correct Password
    Base Login          ${CORRECT_PASSWORD}
Fill Form
    Select From List By Label   css:#country    Australia
    FOR     ${input}    IN      @{INPUT_ELEMENTS}
        Input Text      ${input}    ${INPUT_VALUES}[${INDEX}]
        ${INDEX}=       Evaluate    ${INDEX} + 1
    END
    Static Sleep
Submit Form
    Click Button    css:#save
    Click Button    css:#logout

*** Keywords ***
Init Session
    ${options}=                 Headless Chrome
    Init Testproject Driver     chrome    timeout=5000      job_name=TestProject Robot  url=https://example.testproject.io/web/     desired_capabilities=${options}

Close Session
    Close All Browsers

Equals
    [Arguments]                     ${x}    ${y}
    Should Be Equal As Strings      ${x}    ${y}

Clear Fields
    Clear Element Text     css:#name
    Clear Element Text     css:#password

Headless Chrome
    ${chrome_options} =     Evaluate    sys.modules['selenium.webdriver'].ChromeOptions()    sys, selenium.webdriver
    Call Method    ${chrome_options}    add_argument    headless
    Call Method    ${chrome_options}    add_argument    disable-gpu
    [Return]       ${chrome_options}

Base Login
    [Arguments]               ${input_password}
    Press Keys                css:#name                       ${EMAIL}
    Input Text                css:#password                   ${input_password}
    ${password}=              Get Value                       css:#password
    ${result}=                Run Keyword And Return Status   Equals    ${password}    ${CORRECT_PASSWORD}
    Run Keyword If            "${result}" == "True"           Run Keywords True
    ...     ELSE              Clear Fields

Run Keywords True
    Click Button      css:#login
    Sleep             3s

Static Sleep
    Sleep             3s


*** Variables ***
${EMAIL}                test@testproject.io
${INCORRECT_PASSWORD}   67890
${CORRECT_PASSWORD}     12345
${INDEX}                0
${CAPABILITIES}         ${EMPTY.join(${_tmp})}
@{INPUT_ELEMENTS}       css:#address    css:#email    css:#phone
@{INPUT_VALUES}         Melbourne       test@test.io  7521234545
@{_tmp}
    ...  browserName: chrome,
    ...  version: 86,
    ...  name: RobotFramework Test
```

##  Understanding the Test Suite Structure

In the `*** Test Cases ***` section we declare our test cases and their steps/keywords.
``` python
*** Test Cases ***
Set Session
    ${previous kw}=     Register Keyword To Run On Failure      None
Login With Incorrect Password
    Base Login          ${INCORRECT_PASSWORD}
Login With Correct Password
    Base Login          ${CORRECT_PASSWORD}
```

The first command sets the keyword which should run on Failure to `None`. This means that no keyword will be executed if a step fails.
> It can be set to any keyword of your choice, by default it is set to take a screenshot.

Next we declare two test cases with the names `Login With Incorrect Password` and `Login With Correct Password`.\
Both tests have a single Custom Keyword step called `Base Login` which takes a password as an argument, attempts to login and validates the result.

The `Base Login` declarated in the `*** Keywords ***` section:
```python
Base Login
    [Arguments]               ${input_password}
    Press Keys                css:#name                       ${EMAIL}
    Input Text                css:#password                   ${input_password}
    ${password}=              Get Value                       css:#password
    ${result}=                Run Keyword And Return Status   Equals    ${password}    ${CORRECT_PASSWORD}
    Run Keyword If            "${result}" == "True"           Run Keywords True
    ...     ELSE              Clear Fields
```

If the login fails, we execute another custom Keyword, `Clear Fields`, which is also defined in the `*** Keywords ***` section:
```python
Clear Fields
    Clear Element Text     css:#name
    Clear Element Text     css:#password
```

If the password was correct, we run the `Run Keywords True` keyword to finilize the login process:
```python
Run Keywords True
    Click Button css:#login
    Sleep 3s
```

Next, we fill in the form fields, click on Submit and Logout:
```python
Fill Form
    Select From List By Label   css:#country    Australia
    FOR     ${input}    IN      @{INPUT_ELEMENTS}
        Input Text      ${input}    ${INPUT_VALUES}[${INDEX}]
        ${INDEX}=       Evaluate    ${INDEX} + 1
    END
    Static Sleep

Submit Form
    Click Button    css:#save
    Click Button    css:#logout
```
>This also shows how to implement a simple for loop with an Index increment in Robot framework.

## Init TestProject Driver

This is the entrypoint of the TestProject Library for Robot.\
This method instructs the TestProject Agent on how to start and execute our test.
> It's possible run Regular or Headless browsers, for example, using the Desired Capabilities.

The method is defined with the following arguments:
```python
@keyword
    def init_testproject_driver(
            self,
            browser: str = "firefox",
            url: Optional[str] = None,
            timeout: Optional[int] = 5000,
            project_name: Optional[str] = "TestProject Robot",
            job_name: Optional[str] = "Robot Job",
            desired_capabilities: Union[str, dict, None] = None,
            disable_reports: Optional[bool] = False,
            dev_token: Optional[str] = os.environ["TP_DEV_TOKEN"],
):
```

1. 	`browser`: The name of the browser for the session.
1.	`url`: The initial URL to navigate to.
1.	`timeout`: - The Timeout of the selenium web driver to interact with elements.
1.	`project_name`: The project name where the reports of the Jobs will show.
1.	`job_name`: The job name which all the tests will appear under.
1.	`desired_capabilities`: The capabilities to supply to the driver, for example to run on Headless chrome you can do the following:\
    > Additional information about supported capabilities can be found [Here](https://github.com/SeleniumHQ/selenium/wiki/DesiredCapabilities).
1. `disable_reports` - If set to True, no reports will be generated and sent to the TestProject platform.
1. `dev_token` - The development token, which by default is read from the environment variable `TP_DEV_TOKEN`.\
you can get your token at: https://app.testproject.io/#/integrations/sdk.

>You can set the driver to be a generic driver as well by passing "generic" in the browser argument.
