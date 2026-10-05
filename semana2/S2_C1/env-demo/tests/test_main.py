import pytest

from env_demo.main import environment_message, main


@pytest.mark.parametrize("environment", ["dev", "pre", "pro"])
def test_environment_message(environment):
    assert environment_message(environment) == f"Entorno activo: {environment.upper()}"


def test_environment_normalization():
    assert environment_message(" PRE ") == "Entorno activo: PRE"


@pytest.mark.parametrize("environment", ["", "production", "test"])
def test_invalid_environment(environment):
    with pytest.raises(ValueError, match="APP_ENV debe ser dev, pre o pro"):
        environment_message(environment)


@pytest.mark.parametrize("environment", ["dev", "pre", "pro"])
def test_main_uses_environment(monkeypatch, capsys, environment):
    monkeypatch.setenv("APP_ENV", environment)
    main()
    assert capsys.readouterr().out.strip() == f"Entorno activo: {environment.upper()}"


def test_main_defaults_to_dev(monkeypatch, capsys):
    monkeypatch.delenv("APP_ENV", raising=False)
    main()
    assert capsys.readouterr().out.strip() == "Entorno activo: DEV"
