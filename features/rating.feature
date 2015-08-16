Feature: rating an application

    Scenario: user rates an app
        Given a user
        When he rates an app
        Then the user should have the app rating in his ratings
