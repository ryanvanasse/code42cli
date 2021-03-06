import py42.sdk
import py42.settings.debug as debug
import pytest
from py42.exceptions import Py42UnauthorizedError
from requests import Response
from requests.exceptions import ConnectionError
from requests.exceptions import RequestException

from .conftest import create_mock_profile
from code42cli.errors import Code42CLIError
from code42cli.errors import LoggedCLIError
from code42cli.sdk_client import create_sdk
from code42cli.sdk_client import validate_connection


@pytest.fixture
def sdk_logger(mocker):
    return mocker.patch("code42cli.sdk_client.logger")


@pytest.fixture
def mock_sdk_factory(mocker):
    return mocker.patch("py42.sdk.from_local_account")


@pytest.fixture
def requests_exception(mocker):
    mock_response = mocker.MagicMock(spec=Response)
    mock_exception = mocker.MagicMock(spec=RequestException)
    mock_exception.response = mock_response
    return mock_exception


def test_create_sdk_when_profile_has_ssl_errors_disabled_sets_py42_setting_and_prints_warning(
    profile, mocker, capsys
):
    mock_py42 = mocker.patch("code42cli.sdk_client.py42")
    profile.ignore_ssl_errors = "True"
    create_sdk(profile, False)
    output = capsys.readouterr()
    assert not mock_py42.settings.verify_ssl_certs
    assert (
        "Warning: Profile '{}' has SSL verification disabled. Adding certificate verification is strongly advised.".format(
            profile.name
        )
        in output.err
    )


def test_create_sdk_when_py42_exception_occurs_raises_and_logs_cli_error(
    sdk_logger, mock_sdk_factory, requests_exception
):

    mock_sdk_factory.side_effect = Py42UnauthorizedError(requests_exception)
    profile = create_mock_profile()

    def mock_get_password():
        return "Test Password"

    profile.get_password = mock_get_password
    with pytest.raises(Code42CLIError) as err:
        create_sdk(profile, False)

    assert "Invalid credentials for user" in err.value.message
    assert sdk_logger.log_error.call_count == 1
    assert "Failure in HTTP call" in sdk_logger.log_error.call_args[0][0]


def test_create_sdk_when_connection_exception_occurs_raises_and_logs_cli_error(
    sdk_logger, mock_sdk_factory
):
    mock_sdk_factory.side_effect = ConnectionError("connection message")
    profile = create_mock_profile()

    def mock_get_password():
        return "Test Password"

    profile.get_password = mock_get_password
    with pytest.raises(LoggedCLIError) as err:
        create_sdk(profile, False)

    assert "Problem connecting to" in err.value.message
    assert sdk_logger.log_error.call_count == 1
    assert "connection message" in sdk_logger.log_error.call_args[0][0]


def test_create_sdk_when_unknown_exception_occurs_raises_and_logs_cli_error(
    sdk_logger, mock_sdk_factory
):
    mock_sdk_factory.side_effect = Exception("test message")
    profile = create_mock_profile()

    def mock_get_password():
        return "Test Password"

    profile.get_password = mock_get_password
    with pytest.raises(LoggedCLIError) as err:
        create_sdk(profile, False)

    assert "Unknown problem validating" in err.value.message
    assert sdk_logger.log_error.call_count == 1
    assert "test message" in sdk_logger.log_error.call_args[0][0]


def test_create_sdk_when_told_to_debug_turns_on_debug(mock_sdk_factory):
    profile = create_mock_profile()

    def mock_get_password():
        return "Test Password"

    profile.get_password = mock_get_password
    create_sdk(profile, True)
    assert py42.settings.debug.level == debug.DEBUG


def test_validate_connection_uses_given_credentials(mock_sdk_factory):
    assert validate_connection("Authority", "Test", "Password")
    mock_sdk_factory.assert_called_once_with("Authority", "Test", "Password")
