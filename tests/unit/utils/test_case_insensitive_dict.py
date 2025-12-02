"""Tests for case-insensitive dictionary implementation."""

from src.utils.case_insensitive_dict import CaseInsensitiveDict


class TestCaseInsensitiveDict:
    """Test case-insensitive dictionary behavior."""

    def test_basic_case_insensitive_lookup(self):
        """Test basic case-insensitive get/set operations."""
        d = CaseInsensitiveDict()
        d["myKey"] = "value1"

        assert d["myKey"] == "value1"
        assert d["MYKEY"] == "value1"
        assert d["MyKey"] == "value1"
        assert d["mykey"] == "value1"

    def test_first_declaration_casing_preserved(self):
        """Test that first declaration's casing is preserved."""
        d = CaseInsensitiveDict()
        d["myParam"] = 1
        d["MYPARAM"] = 2  # Should update same key

        assert d["myParam"] == 2
        assert d.get_original_name("myparam") == "myParam"
        assert d.get_original_name("MYPARAM") == "myParam"

    def test_contains_case_insensitive(self):
        """Test 'in' operator is case-insensitive."""
        d = CaseInsensitiveDict()
        d["myKey"] = "value"

        assert "myKey" in d
        assert "MYKEY" in d
        assert "MyKey" in d
        assert "mykey" in d
        assert "otherKey" not in d

    def test_get_with_default(self):
        """Test get() method with default value."""
        d = CaseInsensitiveDict()
        d["exists"] = "value"

        assert d.get("EXISTS") == "value"
        assert d.get("notExists", "default") == "default"
        assert d.get("NOTEXISTS") is None

    def test_delete_case_insensitive(self):
        """Test deletion is case-insensitive."""
        d = CaseInsensitiveDict()
        d["myKey"] = "value"

        del d["MYKEY"]  # Delete with different case
        assert "myKey" not in d
        assert "MYKEY" not in d

    def test_pop_case_insensitive(self):
        """Test pop() is case-insensitive."""
        d = CaseInsensitiveDict()
        d["myKey"] = "value"

        result = d.pop("MYKEY")
        assert result == "value"
        assert "myKey" not in d

    def test_original_keys_iterator(self):
        """Test original_keys() returns keys with original casing."""
        d = CaseInsensitiveDict()
        d["firstName"] = 1
        d["LastName"] = 2
        d["AGE"] = 3

        original_keys = list(d.original_keys())
        assert "firstName" in original_keys
        assert "LastName" in original_keys
        assert "AGE" in original_keys
        # Should NOT have lowercase versions
        assert "firstname" not in original_keys

    def test_items_with_original_casing(self):
        """Test items() returns tuples with original key casing."""
        d = CaseInsensitiveDict()
        d["MyParam"] = 10
        d["YourParam"] = 20

        items = dict(d.items())
        assert items == {"MyParam": 10, "YourParam": 20}

    def test_update_preserves_casing(self):
        """Test update() preserves original casing."""
        d = CaseInsensitiveDict()
        d.update({"FirstKey": 1, "SecondKey": 2})

        assert d.get_original_name("firstkey") == "FirstKey"
        assert d.get_original_name("secondkey") == "SecondKey"

    def test_copy_preserves_casing(self):
        """Test copy() preserves original casing."""
        d = CaseInsensitiveDict()
        d["OriginalKey"] = "value"

        d2 = d.copy()
        assert d2["originalkey"] == "value"
        assert d2.get_original_name("originalkey") == "OriginalKey"

    def test_clear(self):
        """Test clear() removes all entries."""
        d = CaseInsensitiveDict()
        d["key1"] = 1
        d["key2"] = 2

        d.clear()
        assert len(d) == 0
        assert "key1" not in d

    def test_repr_uses_original_casing(self):
        """Test __repr__ shows original casing."""
        d = CaseInsensitiveDict()
        d["MyKey"] = "value"

        repr_str = repr(d)
        assert "MyKey" in repr_str
        assert "mykey" not in repr_str

    def test_multiple_updates_preserve_first_casing(self):
        """Test multiple updates preserve first declaration's casing."""
        d = CaseInsensitiveDict()
        d["originalCase"] = 1
        d["ORIGINALCASE"] = 2
        d["OriginalCase"] = 3

        assert d["originalcase"] == 3  # Latest value
        assert d.get_original_name("originalcase") == "originalCase"  # First casing

    def test_empty_dict(self):
        """Test empty dictionary behavior."""
        d = CaseInsensitiveDict()

        assert len(d) == 0
        assert "anything" not in d
        assert list(d.original_keys()) == []
        assert list(d.items()) == []
