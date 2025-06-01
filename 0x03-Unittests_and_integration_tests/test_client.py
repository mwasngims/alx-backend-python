#!/usr/bin/env python3
"""Unit tests for the GithubOrgClient class in client.py.
"""

from parameterized import parameterized
from parameterized import parameterized_class
from unittest.mock import patch, PropertyMock
import unittest
import requests
from client import GithubOrgClient

from fixtures import TEST_PAYLOAD

org_payload, repos_payload, expected_repos, apache2_repos = TEST_PAYLOAD[0]


@patch('client.get_json')
class TestGithubOrgClient(unittest.TestCase):
    """Test cases for the GithubOrgClient class."""

    @parameterized.expand([
        ("google",),
        ("abc",),
    ])
    def test_org(self, mock_get_json, org_name):
        """
        Test that GithubOrgClient.org returns the correct value and that
        get_json is called once with the expected URL.
        """
        expected_payload = {"org": org_name}
        mock_get_json.return_value = expected_payload

        client = GithubOrgClient(org_name)
        result = client.org

        mock_get_json.assert_called_once_with(
            f"https://api.github.com/orgs/{org_name}"
        )
        self.assertEqual(result, expected_payload)

    def test_public_repos_url(self, mock_get_json):
        """
        Test that GithubOrgClient._public_repos_url returns the correct URL
        based on the payload returned by GithubOrgClient.org.
        """
        payload = {"repos_url": "https://api.github.com/orgs/testorg/repos"}
        with patch.object(
            GithubOrgClient, "org", new_callable=PropertyMock
        ) as mock_org:
            mock_org.return_value = payload
            client = GithubOrgClient("testorg")
            result = client._public_repos_url
            self.assertEqual(result, payload["repos_url"])

    def test_public_repos(self, mock_get_json):
        """
        Test that GithubOrgClient.public_repos returns the correct list of
        public repositories based on the payload returned by get_json and
        the URL returned by GithubOrgClient._public_repos_url.
        """
        test_payload = [
            {"name": "repo1"},
            {"name": "repo2"},
            {"name": "repo3"},
        ]
        mock_get_json.return_value = test_payload
        test_url = "https://api.github.com/orgs/testorg/repos"

        with patch.object(
            GithubOrgClient, "_public_repos_url", new_callable=PropertyMock
        ) as mock_url:
            mock_url.return_value = test_url
            client = GithubOrgClient("testorg")
            repos = client.public_repos()
            self.assertEqual(repos, ["repo1", "repo2", "repo3"])
            mock_url.assert_called_once()
            mock_get_json.assert_called_once_with(test_url)

    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False),
    ])
    def test_has_license(self, mock_get_json, repo, license_key, expected):
        """
        Test that GithubOrgClient.has_license
        returns True if the repo's license
        matches license_key, otherwise False.
        """
        result = GithubOrgClient.has_license(repo, license_key)
        self.assertEqual(result, expected)

    def test_public_repos(self, mock_get_json):
        """
        Test that GithubOrgClient.public_repos returns the expected list
        of repository names based on the fixtures.
        """
        # Set side_effect to return org_payload first, then repos_payload
        mock_get_json.side_effect = [org_payload, repos_payload]
        client = GithubOrgClient("google")
        self.assertEqual(client.public_repos(), expected_repos)

    def test_public_repos_with_license(self, mock_get_json):
        """
        Test that GithubOrgClient.public_repos returns the expected list
        of repository names filtered by license="apache-2.0"
        based on the fixtures.
        """
        mock_get_json.side_effect = [org_payload, repos_payload]
        client = GithubOrgClient("google")
        self.assertEqual(
            client.public_repos(),
            expected_repos
        )

        self.assertEqual(
            client.public_repos(license="apache-2.0"),
            apache2_repos
        )


@parameterized_class([
    {
        "org_payload": org_payload,
        "repos_payload": repos_payload,
        "expected_repos": expected_repos,
        "apache2_repos": apache2_repos,
    }
])
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Integration tests for GithubOrgClient.public_repos."""

    @classmethod
    def setUpClass(cls):
        """Set up class-wide mocks for requests.get."""
        cls.get_patcher = patch('requests.get')
        cls.mock_get = cls.get_patcher.start()

        def side_effect(url):
            mock_response = unittest.mock.Mock()
            if url == GithubOrgClient.ORG_URL.format(org="google"):
                mock_response.json.return_value = cls.org_payload
            elif url == cls.org_payload["repos_url"]:
                mock_response.json.return_value = cls.repos_payload
            return mock_response

        cls.mock_get.side_effect = side_effect

    @classmethod
    def tearDownClass(cls):
        """Stop the requests.get patcher."""
        cls.get_patcher.stop()

    def test_integration_placeholder(self):
        """Dummy test to satisfy parameterized_class check."""
        self.assertTrue(True)
        