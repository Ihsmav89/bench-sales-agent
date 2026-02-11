"""Tests for CLI shared helper functions."""

from unittest.mock import MagicMock, call, patch

from bench_sales_agent.cli import (
    parse_csv,
    prompt_select,
    run_menu,
    show_email_panel,
)


# ── parse_csv ────────────────────────────────────────────────────────────


def test_parse_csv_basic():
    assert parse_csv("Java, Python, SQL") == ["Java", "Python", "SQL"]


def test_parse_csv_strips_whitespace():
    assert parse_csv("  Java ,  Python  , SQL  ") == ["Java", "Python", "SQL"]


def test_parse_csv_drops_empty_items():
    assert parse_csv("Java,,, Python, ,SQL") == ["Java", "Python", "SQL"]


def test_parse_csv_empty_string():
    assert parse_csv("") == []


def test_parse_csv_single_item():
    assert parse_csv("Java") == ["Java"]


def test_parse_csv_only_commas():
    assert parse_csv(",,,") == []


# ── run_menu ─────────────────────────────────────────────────────────────


@patch("bench_sales_agent.cli.Prompt.ask", return_value="0")
@patch("bench_sales_agent.cli.console")
def test_run_menu_exit_immediately(mock_console, mock_ask):
    handler = MagicMock()
    run_menu("Test Menu", [("Option A", handler)])
    handler.assert_not_called()


@patch("bench_sales_agent.cli.Prompt.ask", side_effect=["1", "0"])
@patch("bench_sales_agent.cli.console")
def test_run_menu_calls_handler(mock_console, mock_ask):
    handler = MagicMock()
    run_menu("Test Menu", [("Option A", handler)])
    handler.assert_called_once()


@patch("bench_sales_agent.cli.Prompt.ask", side_effect=["2", "1", "0"])
@patch("bench_sales_agent.cli.console")
def test_run_menu_dispatches_correct_handler(mock_console, mock_ask):
    handler_a = MagicMock()
    handler_b = MagicMock()
    run_menu("Test Menu", [("A", handler_a), ("B", handler_b)])
    handler_b.assert_called_once()
    handler_a.assert_called_once()


@patch("bench_sales_agent.cli.Prompt.ask", return_value="0")
@patch("bench_sales_agent.cli.console")
def test_run_menu_prints_title_and_options(mock_console, mock_ask):
    run_menu("My Menu", [("First", lambda: None), ("Second", lambda: None)])
    printed = [str(c) for c in mock_console.print.call_args_list]
    text = " ".join(printed)
    assert "My Menu" in text
    assert "First" in text
    assert "Second" in text


@patch("bench_sales_agent.cli.Prompt.ask", return_value="0")
@patch("bench_sales_agent.cli.console")
def test_run_menu_custom_exit_label(mock_console, mock_ask):
    run_menu("Menu", [("X", lambda: None)], exit_label="Quit")
    printed = [str(c) for c in mock_console.print.call_args_list]
    text = " ".join(printed)
    assert "Quit" in text


# ── prompt_select ────────────────────────────────────────────────────────


@patch("bench_sales_agent.cli.console")
def test_prompt_select_empty_list(mock_console):
    result = prompt_select([], lambda: None, lambda x: x, empty_msg="Nothing here.")
    assert result is None
    mock_console.print.assert_called_once()
    assert "Nothing here." in str(mock_console.print.call_args)


@patch("bench_sales_agent.cli.Prompt.ask", return_value="abc")
@patch("bench_sales_agent.cli.console")
def test_prompt_select_found(mock_console, mock_ask):
    list_fn = MagicMock()
    get_fn = MagicMock(return_value={"id": "abc", "name": "Test"})

    result = prompt_select(["item1"], list_fn, get_fn, label="Pick one")

    list_fn.assert_called_once()
    get_fn.assert_called_once_with("abc")
    assert result == {"id": "abc", "name": "Test"}


@patch("bench_sales_agent.cli.Prompt.ask", return_value="bad-id")
@patch("bench_sales_agent.cli.console")
def test_prompt_select_not_found(mock_console, mock_ask):
    get_fn = MagicMock(return_value=None)

    result = prompt_select(["item1"], lambda: None, get_fn)

    assert result is None
    printed = str(mock_console.print.call_args)
    assert "Not found" in printed


# ── show_email_panel ─────────────────────────────────────────────────────


@patch("bench_sales_agent.cli.console")
def test_show_email_panel_displays_subject_and_body(mock_console):
    email = {"subject": "Test Subject", "body": "Hello world"}
    show_email_panel(email, "My Email")

    mock_console.print.assert_called_once()
    panel = mock_console.print.call_args[0][0]
    rendered = panel.renderable
    assert "Test Subject" in rendered
    assert "Hello world" in rendered
    assert panel.title == "My Email"
