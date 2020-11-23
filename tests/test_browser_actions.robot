*** Settings ***
Library         TestProjectLibrary
Library         String
Suite Setup     Init
Suite Teardown  Close
*** Test Cases ***
Set Session
    ${previous kw}=                 Register Keyword To Run On Failure      None
    set selenium implicit wait      30 seconds

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
    click element         //a[@id='cc-button']
    Click Element         //a[@title='Platform']
    Click Element         //a[.='Addons']
    Click Element         //button[@aria-label='Close']
    Input Text            //input[@id='q']        Rest
    wait until element is visible  locator=//div[contains(text(), 'RESTful API Client')]    timeout=5s
    Click Element         //div[contains(text(), 'RESTful API Client')]
    ${language}=          Get Text                //div[@class='addon-language']
    Should Be Equal As Strings                 ${language}     Java

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
    Init Testproject Driver     headlessfirefox     url=https://tp-solutions.herokuapp.com/code

Close
    Close All Browsers

Equals
    [Arguments]                     ${x}    ${y}
    Should Be Equal As Strings      ${x}    ${y}

Handle New Window
    Switch Window                       locator=NEW
    close window
    Switch Window                       locator=MAIN


*** Variables ***
