*** Settings ***
Library         TestProjectLibrary
Suite Setup     Init
Suite Teardown  Close
*** Test Cases ***
Set Session
    ${previous kw}=                 Register Keyword To Run On Failure      None
    set selenium implicit wait      15

Work On Actions
    Press Keys      //a[contains(text(), 'Actions')]
    ${buttons_count}=           Get Element Count   //div[@class='list-group']/button
    ${start}                    Set Variable        2
    FOR     ${i}   IN RANGE     ${start}            ${buttons_count}
            Click Button        (//div[@class='list-group']/button)[${i}]
            Run Keyword If      ${i} == 2           Handle New Window
            Exit For Loop If    ${i} == 3
    END

Navigate To TestProject
    Go To           https://testproject.io/

Click On Addons And Search
    Press Keys      //a[@title='Platform']
    Press keys      //a[.='Addons']
    Input Text      //input[@id='q']        Rest
    Press Keys      //div[contains(text(), 'RESTful API Client')]
    ${language}=    Get Text                //div[@class='addon-language']
    Should Be Equal As Strings              ${language}     Java
    Static Sleep

Random Actions
    Go To           https://www.google.com/
    Input Text      //input[@name='q']       TestProject
    press keys      //input[@name='q']       ENTER
    page should contain                      Free Test
    reload page
    log title
    ${links}=       Get All Links
    log to console  ${links}

*** Keywords ***
Init
    ${options_chrome}=     Headless Chrome
    Init Testproject Driver     chrome    timeout=5000     url=https://tp-solutions.herokuapp.com/code

Close
    Close All Browsers

Equals
    [Arguments]                     ${x}    ${y}
    Should Be Equal As Strings      ${x}    ${y}

Handle New Window
    ${title_var}        Get Window Titles
    Select Window       title=${title_var}[1]
    Close Window
    @{windows_num} =    Get Window Titles
    ${nWindows} =       Get Length  ${windows_num}
    ${latest_window} =  Evaluate  ${nWindows}-1
    Select Window       ${windows_num}[${latest_window}]

Headless Chrome
    ${chrome_options} =     Evaluate    sys.modules['selenium.webdriver'].ChromeOptions()    sys, selenium.webdriver
    Call Method    ${chrome_options}    add_argument    headless
    Call Method    ${chrome_options}    add_argument    disable-gpu
    [Return]       ${chrome_options}

Static Sleep
    Sleep             3s


*** Variables ***
