"""Unit tests for multiplier naming conventions."""

import pytest

from src.kkt.naming import (
    BOUND_NAME_MAX_LENGTH,
    GAMS_MAX_IDENTIFIER_LENGTH,
    clear_long_identifier_registry,
    create_bound_lo_multiplier_name,
    create_bound_lo_multiplier_name_indexed,
    create_bound_up_multiplier_name,
    create_eq_multiplier_name,
    create_ineq_multiplier_name,
    detect_naming_collision,
    get_long_identifier_registry,
    resolve_collision,
    shorten_identifier,
)


@pytest.mark.unit
class TestMultiplierNaming:
    """Tests for multiplier naming functions."""

    def test_eq_multiplier_scalar(self):
        """Equality multiplier for scalar constraint."""
        name = create_eq_multiplier_name("balance")
        assert name == "nu_balance"

    def test_eq_multiplier_indexed(self):
        """Equality multiplier for indexed constraint.

        Note: The function doesn't use indices - they're inherited from the
        equation domain in GAMS.
        """
        name = create_eq_multiplier_name("balance")
        assert name == "nu_balance"

    def test_ineq_multiplier_scalar(self):
        """Inequality multiplier for scalar constraint."""
        name = create_ineq_multiplier_name("capacity")
        assert name == "lam_capacity"

    def test_ineq_multiplier_indexed(self):
        """Inequality multiplier for indexed constraint.

        Note: The function doesn't use indices - they're inherited from the
        equation domain in GAMS.
        """
        name = create_ineq_multiplier_name("capacity")
        assert name == "lam_capacity"

    def test_bound_lo_multiplier_scalar(self):
        """Lower bound multiplier for scalar variable."""
        name = create_bound_lo_multiplier_name("x")
        assert name == "piL_x"

    def test_bound_lo_multiplier_indexed(self):
        """Lower bound multiplier for indexed variable.

        Note: The function doesn't use indices - they're inherited from the
        bound constraint domain in GAMS.
        """
        name = create_bound_lo_multiplier_name("x")
        assert name == "piL_x"

    def test_bound_up_multiplier_scalar(self):
        """Upper bound multiplier for scalar variable."""
        name = create_bound_up_multiplier_name("x")
        assert name == "piU_x"

    def test_bound_up_multiplier_indexed(self):
        """Upper bound multiplier for indexed variable.

        Note: The function doesn't use indices - they're inherited from the
        bound constraint domain in GAMS.
        """
        name = create_bound_up_multiplier_name("x")
        assert name == "piU_x"

    def test_different_constraints_different_names(self):
        """Different constraints should get different multiplier names."""
        name1 = create_eq_multiplier_name("balance")
        name2 = create_eq_multiplier_name("flow")
        assert name1 != name2

    def test_different_variables_different_bound_names(self):
        """Different variables should get different bound multiplier names."""
        name1 = create_bound_lo_multiplier_name("x")
        name2 = create_bound_lo_multiplier_name("y")
        assert name1 != name2


@pytest.mark.unit
class TestNamingCollision:
    """Tests for naming collision detection and resolution."""

    def test_no_collision(self):
        """No collision when multiplier names don't overlap with variables."""
        mult_names = {"nu_balance", "lam_capacity"}
        var_names = {"x", "y", "z"}

        collisions = detect_naming_collision(mult_names, var_names)

        assert collisions == []

    def test_single_collision(self):
        """Single collision when multiplier name matches variable."""
        mult_names = {"nu_x", "lam_y"}
        var_names = {"x", "y", "nu_x"}

        collisions = detect_naming_collision(mult_names, var_names)

        assert collisions == ["nu_x"]

    def test_multiple_collisions(self):
        """Multiple collisions detected."""
        mult_names = {"nu_x", "lam_y", "piL_z"}
        var_names = {"nu_x", "lam_y", "w"}

        collisions = detect_naming_collision(mult_names, var_names)

        assert set(collisions) == {"nu_x", "lam_y"}

    def test_resolve_collision_first_suffix(self):
        """Resolve collision with _1 suffix."""
        result = resolve_collision("nu_x", {"nu_x"})
        assert result == "nu_x_1"

    def test_resolve_collision_second_suffix(self):
        """Resolve collision when _1 is also taken."""
        result = resolve_collision("nu_x", {"nu_x", "nu_x_1"})
        assert result == "nu_x_2"

    def test_resolve_collision_finds_first_available(self):
        """Resolve collision by finding first available suffix."""
        result = resolve_collision("lam_y", {"lam_y", "lam_y_1", "lam_y_2"})
        assert result == "lam_y_3"


@pytest.mark.unit
class TestIdentifierShortening:
    """Issue #1290: deterministic shortening for over-length identifiers."""

    def setup_method(self):
        clear_long_identifier_registry()

    def test_short_name_unchanged(self):
        assert shorten_identifier("nu_balance") == "nu_balance"

    def test_exactly_at_limit_unchanged(self):
        name = "x" * GAMS_MAX_IDENTIFIER_LENGTH
        assert shorten_identifier(name) == name
        assert get_long_identifier_registry() == {}

    def test_over_limit_is_shortened_to_max_length(self):
        name = "x" * (GAMS_MAX_IDENTIFIER_LENGTH + 5)
        out = shorten_identifier(name)
        assert len(out) == GAMS_MAX_IDENTIFIER_LENGTH

    def test_shortening_is_deterministic(self):
        name = "x" * 80
        a = shorten_identifier(name)
        b = shorten_identifier(name)
        assert a == b

    def test_shortening_records_mapping(self):
        original = "y" * 80
        shortened = shorten_identifier(original)
        registry = get_long_identifier_registry()
        assert registry[shortened] == original

    def test_shortening_preserves_head_and_appends_hex_hash(self):
        # Format is `<head>_<8-hex>` totaling exactly max_length.
        original = "longprefix_" + ("z" * 80)
        shortened = shorten_identifier(original, max_length=63)
        assert len(shortened) == 63
        # Last 9 chars are `_<8-hex>`
        assert shortened[-9] == "_"
        # The 8 trailing chars are valid lowercase hex
        assert all(c in "0123456789abcdef" for c in shortened[-8:])
        # Head is the original prefix
        assert original.startswith(shortened[:-9])

    def test_distinct_names_get_distinct_shortenings(self):
        a = shorten_identifier("a" * 80)
        b = shorten_identifier("b" * 80)
        assert a != b

    def test_ferts_style_67char_name(self):
        # Issue #1290 reproducer
        original = "nu_xi_fx_sulf_acid_c8324d9c_kafr_el_zt_4b0342d5_kafr_el_zt_4b0342d5"
        assert len(original) == 67
        out = shorten_identifier(original)
        assert len(out) == 63
        assert get_long_identifier_registry()[out] == original

    def test_eq_multiplier_with_long_eq_name_is_shortened(self):
        long_eq = "y" * 70
        out = create_eq_multiplier_name(long_eq)
        assert len(out) <= GAMS_MAX_IDENTIFIER_LENGTH

    def test_bound_indexed_multiplier_with_long_indices_is_shortened(self):
        out = create_bound_lo_multiplier_name_indexed(
            "x", tuple("element_" + "z" * 30 for _ in range(3))
        )
        assert len(out) <= GAMS_MAX_IDENTIFIER_LENGTH

    def test_clear_registry(self):
        shorten_identifier("a" * 80)
        assert get_long_identifier_registry()
        clear_long_identifier_registry()
        assert get_long_identifier_registry() == {}

    def test_bound_name_max_leaves_room_for_multiplier_prefix(self):
        # Wrapping with `nu_`/`lam_`/`piL_`/`piU_` (max 4 chars) must not
        # push the result past the GAMS limit.
        assert BOUND_NAME_MAX_LENGTH + 4 <= GAMS_MAX_IDENTIFIER_LENGTH
