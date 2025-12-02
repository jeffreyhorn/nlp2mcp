"""Case-insensitive dictionary for GAMS symbol storage.

GAMS is case-insensitive, so 'myParam', 'MYPARAM', and 'MyParam' all refer
to the same symbol. This module provides a dictionary that preserves the
original casing for display while performing case-insensitive lookups.
"""

from collections.abc import Iterator
from typing import TypeVar

T = TypeVar("T")


class CaseInsensitiveDict(dict[str, T]):
    """Dictionary with case-insensitive string keys.

    Stores values with lowercase keys internally but preserves the original
    casing for display. The first declaration's casing is preserved.

    Example:
        >>> d = CaseInsensitiveDict()
        >>> d['myParam'] = 1
        >>> d['MYPARAM']  # Returns 1 (case-insensitive)
        1
        >>> d.get_original_name('myparam')  # Returns original casing
        'myParam'
    """

    def __init__(self):
        super().__init__()
        self._original_names: dict[str, str] = {}  # lowercase -> original casing

    def __setitem__(self, key: str, value: T) -> None:
        """Set item with case-insensitive key."""
        canonical = key.lower()
        super().__setitem__(canonical, value)
        # Preserve first declaration's casing
        if canonical not in self._original_names:
            self._original_names[canonical] = key

    def __getitem__(self, key: str) -> T:
        """Get item with case-insensitive key."""
        return super().__getitem__(key.lower())

    def __delitem__(self, key: str) -> None:
        """Delete item with case-insensitive key."""
        canonical = key.lower()
        super().__delitem__(canonical)
        if canonical in self._original_names:
            del self._original_names[canonical]

    def __contains__(self, key: object) -> bool:
        """Check if key exists (case-insensitive)."""
        if not isinstance(key, str):
            return False
        return super().__contains__(key.lower())

    def get(self, key: str, default=None):  # type: ignore[override]
        """Get item with case-insensitive key, returning default if not found."""
        return super().get(key.lower(), default)

    def pop(self, key: str, *args) -> T:
        """Remove and return item with case-insensitive key."""
        canonical = key.lower()
        if canonical in self._original_names:
            del self._original_names[canonical]
        return super().pop(canonical, *args)

    def get_original_name(self, key: str) -> str:
        """Get the original casing of a key as first declared.

        Args:
            key: The key to look up (any casing)

        Returns:
            The original casing from first declaration, or the key itself
            if not found.
        """
        return self._original_names.get(key.lower(), key)

    def keys(self):  # type: ignore[override]
        """Return view of lowercase keys (for internal use)."""
        return super().keys()

    def original_keys(self) -> Iterator[str]:
        """Return iterator of keys with original casing.

        This should be used when displaying symbol names to users or
        generating code output.
        """
        for canonical_key in super().keys():
            yield self._original_names.get(canonical_key, canonical_key)

    def values(self):  # type: ignore[override]
        """Return view of values."""
        return super().values()

    def items(self):
        """Return iterator of (original_key, value) pairs."""
        for canonical_key, value in super().items():
            original_key = self._original_names.get(canonical_key, canonical_key)
            yield (original_key, value)

    def clear(self) -> None:
        """Remove all items."""
        super().clear()
        self._original_names.clear()

    def copy(self) -> "CaseInsensitiveDict[T]":
        """Return a shallow copy."""
        new_dict = CaseInsensitiveDict[T]()
        for canonical_key, value in super().items():
            original_key = self._original_names.get(canonical_key, canonical_key)
            new_dict[original_key] = value
        return new_dict

    def update(self, other=None, **kwargs):
        """Update dictionary from another dict or keywords."""
        if other is not None:
            if isinstance(other, dict):
                for key, value in other.items():
                    self[key] = value
            else:
                for key, value in other:
                    self[key] = value
        for key, value in kwargs.items():
            self[key] = value

    def __repr__(self) -> str:
        """Return string representation using original keys."""
        items = ", ".join(f"{k!r}: {v!r}" for k, v in self.items())
        return f"{{{items}}}"
