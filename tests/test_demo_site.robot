*** Settings ***
Library         TestProjectLibrary
Suite Setup     Init
Suite Teardown  Close
*** Test Cases ***
Set Session
    ${previous kw}=     Register Keyword To Run On Failure      None
Login With Wrong Password
    Base Login      ${WRONG_PASSWORD}
Login With Right Password
    Base Login      ${RIGHT_PASSWORD}
Fill Form
    Select From List By Label      css:#country      Australia
    FOR     ${input}    IN    @{INPUT_ELEMENTS}
        Input Text      ${input}    ${INPUT_VALUES}[${INDEX}]
        ${INDEX}=       Evaluate    ${INDEX} + 1
    END
    Static Sleep
Submit Form
    Click Button    css:#save
    Click Button    css:#logout

*** Keywords ***
Init
    ${options}=     Headless Chrome
    Init Testproject Driver     chrome    timeout=5000      job_name=TestProject Robot  url=https://example.testproject.io/web/     desired_capabilities=${options}

Close
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
    ${result}=                Run Keyword And Return Status   Equals    ${password}    ${RIGHT_PASSWORD}
    Run Keyword If            "${result}" == "True"           Run Keywords True
    ...     ELSE              Clear Fields

Run Keywords True
    Click Button      css:#login
    Sleep             3s

Static Sleep
    Sleep             3s


*** Variables ***
${EMAIL}                test@testproject.io
${WRONG_PASSWORD}       1234
${RIGHT_PASSWORD}       12345
${INDEX}                0
${CAPABILITIES}         ${EMPTY.join(${_tmp})}
@{INPUT_ELEMENTS}       css:#address    css:#email    css:#phone
@{INPUT_VALUES}         Melbourne       test@test.io  7521234545
@{_tmp}
    ...  browserName: chrome,
    ...  version: 86,
    ...  name: RobotFramework Lambda Test
