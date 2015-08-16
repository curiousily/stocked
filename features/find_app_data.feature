Feature: find data about an app

    Scenario: view data about app installs
        Given an app
        When I enter the app installs
        Then I should see average daily installs
        And total installs

    Scenario: view market ratings about app
        Given an app
        When I enter the app market ratings
        Then I should see the average rating
        And I should see the number of ratings
