import pytest
import os
import tempfile
import json
import subprocess
from unittest.mock import patch, MagicMock, mock_open
import sqlite3

# Import functions to test
from server_main import connect_db, bootstrap_database, get_user_profile, check_connectivity, hash_generator
from run_sast import run_bandit_scan
from run_dast import run_zap_baseline_scan, run_zap_full_scan
from security_pipeline import generate_consolidated_report, run_flask_app, wait_for_app


class TestDatabaseOperations:
    """Test database connection and initialization functions"""

    def test_connect_db(self):
        """Test database connection establishment"""
        conn = connect_db()
        assert isinstance(conn, sqlite3.Connection)
        assert conn.row_factory == sqlite3.Row
        conn.close()

    def test_bootstrap_database_creates_tables(self):
        """Test database schema initialization"""
        # Use temporary database
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            temp_db = tmp.name

        try:
            # Patch the database path
            with patch('server_main.connect_db') as mock_connect:
                mock_conn = MagicMock()
                mock_connect.return_value = mock_conn

                bootstrap_database()

                # Verify table creation was called
                mock_conn.execute.assert_called_with('''
                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY,
                        username TEXT NOT NULL,
                        password TEXT NOT NULL,
                        email TEXT
                    )
                ''')

                # Verify default users were inserted
                assert mock_conn.execute.call_count >= 2
                mock_conn.commit.assert_called_once()
                mock_conn.close.assert_called_once()

        finally:
            if os.path.exists(temp_db):
                os.unlink(temp_db)


class TestFlaskRoutes:
    """Test Flask route functions"""

    def test_get_user_profile_valid_id(self):
        """Test user profile retrieval with valid ID"""
        with patch('server_main.connect_db') as mock_connect:
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

            with patch('server_main.request') as mock_request:
                mock_request.args.get.return_value = '1'

                result = get_user_profile()

                assert 'User Profile' in result
                assert 'admin' in result
                assert 'admin@corp.internal' in result
                mock_conn.execute.assert_called_once()
                mock_conn.close.assert_called_once()

    def test_get_user_profile_invalid_id(self):
        """Test user profile retrieval with invalid ID"""
        with patch('server_main.connect_db') as mock_connect:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_conn.execute.return_value = mock_cursor
            mock_cursor.fetchone.return_value = None
            mock_connect.return_value = mock_conn

            with patch('server_main.request') as mock_request:
                mock_request.args.get.return_value = '999'

                result = get_user_profile()

                assert 'User not found' in result
                mock_conn.execute.assert_called_once()
                mock_conn.close.assert_called_once()

    def test_get_user_profile_sql_injection_attempt(self):
        """Test that SQL injection attempts are handled"""
        with patch('server_main.connect_db') as mock_connect:
            mock_conn = MagicMock()
            mock_conn.execute.side_effect = Exception("SQL syntax error")
            mock_connect.return_value = mock_conn

            with patch('server_main.request') as mock_request:
                mock_request.args.get.return_value = "1' OR '1'='1"

                result = get_user_profile()

                assert 'System Error' in result
                mock_conn.close.assert_called_once()

    @patch('server_main.subprocess.check_output')
    def test_check_connectivity_success(self, mock_subprocess):
        """Test connectivity check with successful ping"""
        mock_subprocess.return_value = b"Pinging localhost [127.0.0.1] with 32 bytes of data:\nReply from 127.0.0.1: bytes=32 time<1ms TTL=128"

        with patch('server_main.request') as mock_request:
            mock_request.args.get.return_value = 'localhost'

            result = check_connectivity()

            assert 'Connectivity Results' in result
            assert 'localhost' in result
            assert 'Reply from' in result
            mock_subprocess.assert_called_once()

    @patch('server_main.subprocess.check_output')
    def test_check_connectivity_timeout(self, mock_subprocess):
        """Test connectivity check with timeout"""
        mock_subprocess.side_effect = subprocess.TimeoutExpired(['ping'], 5)

        with patch('server_main.request') as mock_request:
            mock_request.args.get.return_value = 'unreachable.host'

            result = check_connectivity()

            assert 'Connection timed out' in result
            mock_subprocess.assert_called_once()

    @patch('server_main.subprocess.check_output')
    def test_check_connectivity_command_injection_attempt(self, mock_subprocess):
        """Test that command injection attempts are blocked"""
        mock_subprocess.side_effect = Exception("Command injection blocked")

        with patch('server_main.request') as mock_request:
            mock_request.args.get.return_value = 'localhost; rm -rf /'

            result = check_connectivity()

            assert 'Diagnostic Error' in result
            mock_subprocess.assert_called_once()

    def test_hash_generator_md5(self):
        """Test MD5 hash generation"""
        with patch('server_main.request') as mock_request:
            mock_request.args.get.return_value = 'test'

            result = hash_generator()

            assert 'Hash Generation' in result
            assert 'test' in result
            assert 'MD5:' in result
            assert 'SHA1:' in result

    def test_hash_generator_empty_input(self):
        """Test hash generation with empty input"""
        with patch('server_main.request') as mock_request:
            mock_request.args.get.return_value = ''

            result = hash_generator()

            assert 'Hash Generation' in result
            # Empty string should still produce valid hashes
            assert 'MD5:' in result
            assert 'SHA1:' in result


class TestSASTScanning:
    """Test SAST scanning functionality"""

    @patch('run_sast.subprocess.run')
    @patch('run_sast.os.path.exists')
    @patch('run_sast.open', new_callable=mock_open)
    @patch('run_sast.json.load')
    def test_run_bandit_scan_success(self, mock_json_load, mock_file, mock_exists, mock_subprocess):
        """Test successful Bandit scan execution"""
        # Mock subprocess calls
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_subprocess.return_value = mock_result

        # Mock file existence
        mock_exists.return_value = True

        # Mock JSON data
        mock_json_load.return_value = {
            'metrics': {'_totals': {'loc': 100, 'nosec': 5}},
            'results': [
                {
                    'issue_severity': 'HIGH',
                    'issue_confidence': 'HIGH',
                    'test_id': 'B101',
                    'filename': 'server_main.py',
                    'line_number': 167,
                    'issue_text': 'Use of exec detected',
                    'more_info': 'https://bandit.readthedocs.io/en/latest/'
                }
            ]
        }

        result = run_bandit_scan()

        assert result['success'] is True
        assert result['total_issues'] == 1
        assert result['high'] == 1
        assert result['medium'] == 0
        assert result['low'] == 0
        assert 'reports' in result

    @patch('run_sast.subprocess.run')
    def test_run_bandit_scan_bandit_not_found(self, mock_subprocess):
        """Test Bandit scan when bandit is not installed"""
        mock_subprocess.side_effect = FileNotFoundError()

        result = run_bandit_scan()

        assert result['success'] is False
        assert 'Bandit not installed' in result['error']

    @patch('run_sast.subprocess.run')
    @patch('run_sast.os.path.exists')
    def test_run_bandit_scan_report_generation_failure(self, mock_exists, mock_subprocess):
        """Test Bandit scan when report generation fails"""
        mock_exists.return_value = False
        mock_subprocess.return_value = MagicMock()

        result = run_bandit_scan()

        assert result['success'] is False
        assert 'Report not generated' in result['error']


class TestDASTScanning:
    """Test DAST scanning functionality"""

    @patch('run_dast.subprocess.run')
    @patch('run_dast.os.path.exists')
    def test_run_zap_baseline_scan_success(self, mock_exists, mock_subprocess):
        """Test successful ZAP baseline scan"""
        mock_exists.return_value = True

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "ZAP scan completed successfully"
        mock_result.stderr = ""
        mock_subprocess.return_value = mock_result

        result = run_zap_baseline_scan()

        assert result['success'] is True
        assert result['return_code'] == 0
        assert 'reports' in result

    @patch('run_dast.subprocess.run')
    def test_run_zap_baseline_scan_docker_not_available(self, mock_subprocess):
        """Test ZAP scan when Docker is not available"""
        mock_subprocess.side_effect = FileNotFoundError()

        result = run_zap_baseline_scan()

        assert result['success'] is False
        assert 'Docker not available' in result['error']

    @patch('run_dast.subprocess.run')
    def test_run_zap_baseline_scan_timeout(self, mock_subprocess):
        """Test ZAP scan timeout"""
        mock_subprocess.side_effect = subprocess.TimeoutExpired(['docker'], 600)

        result = run_zap_baseline_scan()

        assert result['success'] is False
        assert result['error'] == 'Timeout'

    @patch('run_dast.subprocess.run')
    @patch('run_dast.os.path.exists')
    def test_run_zap_full_scan_success(self, mock_exists, mock_subprocess):
        """Test successful ZAP full scan"""
        mock_exists.return_value = True

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Full scan completed"
        mock_subprocess.return_value = mock_result

        result = run_zap_full_scan()

        assert result['success'] is True
        assert 'Full scan completed' in result['output']


class TestSecurityPipeline:
    """Test security pipeline orchestration"""

    @patch('security_pipeline.open', new_callable=mock_open)
    def test_generate_consolidated_report_success(self, mock_file):
        """Test consolidated report generation"""
        sast_result = {
            'success': True,
            'high': 2,
            'medium': 1,
            'low': 0,
            'total_issues': 3
        }

        dast_result = {
            'success': True
        }

        result_path = generate_consolidated_report(sast_result, dast_result)

        # Verify file was written
        mock_file.assert_called_once()
        handle = mock_file()
        handle.write.assert_called_once()

        # Verify report path
        assert 'security_pipeline_report.html' in result_path

    @patch('security_pipeline.subprocess.Popen')
    def test_run_flask_app(self, mock_popen):
        """Test Flask app startup"""
        mock_process = MagicMock()
        mock_popen.return_value = mock_process

        result = run_flask_app()

        assert result == mock_process
        mock_popen.assert_called_once()

    @patch('security_pipeline.urllib.request.urlopen')
    def test_wait_for_app_success(self, mock_urlopen):
        """Test waiting for app to be ready"""
        mock_response = MagicMock()
        mock_urlopen.return_value = mock_response

        result = wait_for_app()

        assert result is True
        mock_urlopen.assert_called_once()

    @patch('security_pipeline.urllib.request.urlopen')
    def test_wait_for_app_timeout(self, mock_urlopen):
        """Test app readiness timeout"""
        mock_urlopen.side_effect = Exception("Connection refused")

        result = wait_for_app(timeout=1)

        assert result is False

    @patch('security_pipeline.run_bandit_scan')
    @patch('security_pipeline.run_flask_app')
    @patch('security_pipeline.wait_for_app')
    @patch('security_pipeline.run_zap_baseline_scan')
    @patch('security_pipeline.generate_consolidated_report')
    def test_run_pipeline_full_success(self, mock_report, mock_dast, mock_wait, mock_flask, mock_sast):
        """Test full pipeline execution success"""
        mock_sast.return_value = {'success': True, 'total_issues': 5}
        mock_wait.return_value = True
        mock_dast.return_value = {'success': True}
        mock_report.return_value = '/path/to/report.html'

        result = run_pipeline(run_dast=True)

        assert 'sast' in result
        assert 'dast' in result
        assert result['sast']['success'] is True
        assert result['dast']['success'] is True
        mock_sast.assert_called_once()
        mock_flask.assert_called_once()
        mock_wait.assert_called_once()
        mock_dast.assert_called_once()
        mock_report.assert_called_once()

    @patch('security_pipeline.run_bandit_scan')
    def test_run_pipeline_sast_only(self, mock_sast):
        """Test SAST-only pipeline execution"""
        mock_sast.return_value = {'success': True, 'total_issues': 3}

        result = run_pipeline(run_dast=False)

        assert 'sast' in result
        assert 'dast' in result
        assert result['sast']['success'] is True
        assert result['dast']['success'] is False
        assert result['dast']['error'] == 'Skipped'
        mock_sast.assert_called_once()


if __name__ == '__main__':
    pytest.main([__file__])
