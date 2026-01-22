import pytest
import tempfile
import os
from unittest.mock import patch, MagicMock
import subprocess

# Import the Flask app
from server_main import app


class TestFlaskApp:
    """Test Flask application routes"""

    def setup_method(self):
        """Set up test client"""
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

        # Create temporary database for testing
        self.db_fd, self.db_path = tempfile.mkstemp(suffix='.db')
        self.app.config['DATABASE'] = self.db_path

    def teardown_method(self):
        """Clean up after tests"""
        os.close(self.db_fd)
        os.unlink(self.db_path)

    def test_dashboard_route(self):
        """Test main dashboard route"""
        response = self.client.get('/')
        assert response.status_code == 200
        assert b'CorpNet Diagnostics' in response.data
        assert b'Network Diagnostic Utilities' in response.data

    @patch('server_main.connect_db')
    def test_get_user_profile_route_valid(self, mock_connect):
        """Test user profile route with valid ID"""
        # Mock database connection and result
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.execute.return_value = mock_cursor
        mock_cursor.fetchone.return_value = {
            'id': 1,
            'username': 'admin',
            'password': 'admin123',
            'email': 'admin@corp.internal'
        }
        mock_connect.return_value = mock_conn

        response = self.client.get('/api/v1/profile?id=1')

        assert response.status_code == 200
        assert b'User Profile' in response.data
        assert b'admin' in response.data
        assert b'admin@corp.internal' in response.data

    @patch('server_main.connect_db')
    def test_get_user_profile_route_not_found(self, mock_connect):
        """Test user profile route with non-existent user"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.execute.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None
        mock_connect.return_value = mock_conn

        response = self.client.get('/api/v1/profile?id=999')

        assert response.status_code == 200
        assert b'User not found' in response.data

    @patch('server_main.connect_db')
    def test_get_user_profile_route_sql_injection(self, mock_connect):
        """Test user profile route handles SQL injection attempts"""
        mock_conn = MagicMock()
        mock_conn.execute.side_effect = Exception("SQL syntax error")
        mock_connect.return_value = mock_conn

        response = self.client.get('/api/v1/profile?id=1%27%20OR%20%271%27%3D%271')

        assert response.status_code == 200
        assert b'System Error' in response.data

    @patch('server_main.subprocess.check_output')
    def test_connectivity_route_success(self, mock_subprocess):
        """Test connectivity route with successful ping"""
        mock_subprocess.return_value = b"Pinging localhost [127.0.0.1] with 32 bytes of data:\nReply from 127.0.0.1: bytes=32 time<1ms TTL=128"

        response = self.client.get('/api/v1/connectivity?host=localhost')

        assert response.status_code == 200
        assert b'Connectivity Results' in response.data
        assert b'localhost' in response.data
        assert b'Reply from' in response.data

    @patch('server_main.subprocess.check_output')
    def test_connectivity_route_timeout(self, mock_subprocess):
        """Test connectivity route with timeout"""
        mock_subprocess.side_effect = subprocess.TimeoutExpired(['ping'], 5)

        response = self.client.get('/api/v1/connectivity?host=unreachable')

        assert response.status_code == 200
        assert b'Connection timed out' in response.data

    @patch('server_main.subprocess.check_output')
    def test_connectivity_route_command_injection(self, mock_subprocess):
        """Test connectivity route handles command injection attempts"""
        mock_subprocess.side_effect = Exception("Command injection blocked")

        response = self.client.get('/api/v1/connectivity?host=localhost;%20rm%20-rf%20/')

        assert response.status_code == 200
        assert b'Diagnostic Error' in response.data

    def test_hash_generator_route(self):
        """Test hash generator route"""
        response = self.client.get('/util/crypto?password=test123')

        assert response.status_code == 200
        assert b'Hash Generation' in response.data
        assert b'test123' in response.data
        assert b'MD5:' in response.data
        assert b'SHA1:' in response.data

    def test_hash_generator_route_default(self):
        """Test hash generator route with default password"""
        response = self.client.get('/util/crypto')

        assert response.status_code == 200
        assert b'default' in response.data

    def test_kb_search_route(self):
        """Test knowledge base search route"""
        response = self.client.get('/tools/query?q=security')

        assert response.status_code == 200
        assert b'Search Results' in response.data
        assert b'security' in response.data
        assert b'0 results' in response.data

    def test_admin_dashboard_route(self):
        """Test admin dashboard route"""
        response = self.client.get('/admin/dashboard')

        assert response.status_code == 200
        assert b'Administrative Console' in response.data
        assert b'Welcome, Administrator' in response.data

    def test_view_config_route(self):
        """Test system configuration view route"""
        response = self.client.get('/sys/config')

        assert response.status_code == 200
        assert b'System Configuration' in response.data
        assert b'Confidential' in response.data
        assert b'DB Password:' in response.data
        assert b'Secret Key:' in response.data
        assert b'API Key:' in response.data


class TestFlaskAppSecurityHeaders:
    """Test security-related aspects of Flask routes"""

    def setup_method(self):
        """Set up test client"""
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def test_routes_dont_leak_sensitive_info(self):
        """Test that routes don't accidentally leak sensitive information"""
        routes_to_test = [
            '/',
            '/api/v1/profile?id=1',
            '/api/v1/connectivity?host=localhost',
            '/tools/query?q=test',
            '/util/crypto?password=test',
            '/admin/dashboard',
            '/sys/config'
        ]

        for route in routes_to_test:
            response = self.client.get(route)
            assert response.status_code == 200

            # Ensure no hardcoded credentials appear in responses
            # (except for the config page which intentionally shows them)
            if route != '/sys/config':
                assert b'admin123' not in response.data
                assert b'super_secret_key' not in response.data
                assert b'sk-1234567890abcdef' not in response.data

    def test_config_route_exposes_credentials(self):
        """Test that config route properly exposes credentials (as intended for demo)"""
        response = self.client.get('/sys/config')

        assert response.status_code == 200
        # This route is supposed to show credentials for demo purposes
        assert b'admin123' in response.data
        assert b'super_secret_key_12345' in response.data
        assert b'sk-1234567890abcdef' in response.data


if __name__ == '__main__':
    pytest.main([__file__])
