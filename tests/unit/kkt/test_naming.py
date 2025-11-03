"""Unit tests for multiplier naming conventions."""

import pytest

from src.kkt.naming import (
    create_bound_lo_multiplier_name,
    create_bound_up_multiplier_name,
    create_eq_multiplier_name,
    create_ineq_multiplier_name,
    detect_naming_collision,
    resolve_collision,
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
