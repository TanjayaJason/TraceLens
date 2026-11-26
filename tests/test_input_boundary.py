from pathlib import Path
import pytest
from tracelens.support import read_text

def test_bounded_reader_and_utf8_bom(tmp_path):
    path=tmp_path/"input.txt"
    path.write_bytes(b"\xef\xbb\xbfhello")
    assert read_text(path)=="hello"
    with pytest.raises(ValueError,match="exceeds"):
        read_text(path,max_bytes=4)
