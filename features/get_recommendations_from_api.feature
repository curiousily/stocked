Feature: Get recommendations from the REST api

    Scenario: Get recommendations for an user
        Given an user
        When he requests new apps to install
        Then he should receive list of recommended apps
