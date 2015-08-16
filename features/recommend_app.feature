Feature: recommend app

    Scenario: recommend app based on other users liking
        Given 4 apps
        When 2 users rate their apps
        And I rate an app
        Then I should receive recommendations about new apps to install
