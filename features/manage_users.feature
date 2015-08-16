Feature: Manage users

    Scenario: Create, read and delete an user
        Given I am an administrator
        When I create an user
        Then I should read it
        And delete it

    Scenario: user rates an app
        Given existing user
        When he wants to rate an app
        Then he should send his rating
