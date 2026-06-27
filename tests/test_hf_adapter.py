from pathlib import Path

from ncc.hf_adapter import count_basic_tokens, validate_hf_text_dataset


def test_count_basic_tokens():
    assert count_basic_tokens("hello world") == 2


def test_validate_hf_text_dataset(tmp_path: Path):
    path = tmp_path / "hf.jsonl"
    path.write_text(
        '{"text":"<|system|> test <|user|> input <|assistant|> output"}\n',
        encoding="utf-8",
    )

    report = validate_hf_text_dataset(path)

    assert report["total"] == 1
    assert report["malformed"] == 0
    assert report["empty_text"] == 0
    assert report["loadable"] is True
