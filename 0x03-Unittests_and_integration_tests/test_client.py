#!/usr/bin/env python3
"""Unit tests for the GithubOrgClient class in client.py."""

import unittest
from unittest.mock import patch, PropertyMock
from parameterized import parameterized, parameterized_class

from client import GithubOrgClient
from fixtures import TEST_PAYLOAD


@patch('client.get_json')
class TestGithubOrgClient(unittest.TestCase):
    """Test cases for the GithubOrgClient class."""

    @parameterized.expand([
        ("google",),
        ("abc",),
    ])
    def test_org(self, mock_get_json, org_name):
        """Test GithubOrgClient.org returns expected result."""
        expected_payload = {"org": org_name}
        mock_get_json.return_value = expected_payload

        client = GithubOrgClient(org_name)
        result = client.org

        mock_get_json.assert_called_once_with(
            f"https://api.github.com/orgs/{org_name}"
        )
        self.assertEqual(result, expected_payload)

    def test_public_repos_url(self, mock_get_json):
        """Test _public_repos_url returns expected repos_url."""
        payload = {"repos_url": "https://api.github.com/orgs/testorg/repos"}
        with patch.object(
            GithubOrgClient, "org", new_callable=PropertyMock
        ) as mock_org:
            mock_org.return_value = payload
            client = GithubOrgClient("testorg")
            result = client._public_repos_url
            self.assertEqual(result, payload["repos_url"])

    def test_public_repos(self, mock_get_json):
        """Test public_repos returns correct repository names."""
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
        """Test has_license returns True/False based on license match."""
        result = GithubOrgClient.has_license(repo, license_key)
        self.assertEqual(result, expected)

    def test_public_repos_with_fixture(self, mock_get_json):
        """Test public_repos returns expected repos from fixtures."""
        org_payload, repos_payload, expected_repos, _ = TEST_PAYLOAD[0]
        mock_get_json.side_effect = [org_payload, repos_payload]
        client = GithubOrgClient("google")
        self.assertEqual(client.public_repos(), expected_repos)

    def test_public_repos_with_license(self, mock_get_json):
        """Test public_repos filters repos by license key."""
        org_payload, repos_payload, expected_repos, apache2_repos = TEST_PAYLOAD[0]
        mock_get_json.side_effect = [org_payload, repos_payload]
        client = GithubOrgClient("google")
        self.assertEqual(client.public_repos(), expected_repos)
        self.assertEqual(
            client.public_repos(license="apache-2.0"),
            apache2_repos
        )


@parameterized_class([
    {
        "org_payload": TEST_PAYLOAD[0][0],
        "repos_payload": TEST_PAYLOAD[0][1],
        "expected_repos": TEST_PAYLOAD[0][2],
        "apache2_repos": TEST_PAYLOAD[0][3],
    }
])
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Integration tests for GithubOrgClient."""

    @classmethod
    def setUpClass(cls):
        """Set up patcher for requests.get with fixture data."""
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
        """Tear down patcher after all tests."""
        cls.get_patcher.stop()

    def test_public_repos(self):
        """Integration test: public_repos returns expected repos."""
        client = GithubOrgClient("google")
        self.assertEqual(client.public_repos(), self.expected_repos)

    def test_public_repos_with_license(self):
        """Integration test: public_repos filters by license."""
        client = GithubOrgClient("google")
        self.assertEqual(
            client.public_repos(license="apache-2.0"),
            self.apache2_repos
        )
