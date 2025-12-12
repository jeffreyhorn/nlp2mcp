"""Tests for GAMS execute statement parsing (Sprint 12 - Issue #456).

The execute statement is used for running external programs/commands in GAMS.
We parse but don't process since external execution is not relevant for NLP model extraction.
"""

from src.ir.parser import parse_model_text


class TestExecuteBasic:
    """Test basic execute statement parsing."""

    def test_execute_simple_command(self):
        """Test execute with simple command: execute 'echo hello';"""
        source = "execute 'echo hello';"
        model = parse_model_text(source)
        assert model is not None

    def test_execute_program_call(self):
        """Test execute calling a program: execute 'gnuplot input.txt';"""
        source = "execute 'gnuplot input.txt';"
        model = parse_model_text(source)
        assert model is not None

    def test_execute_file_operation(self):
        """Test execute with file operation: execute 'rm tempfile.txt';"""
        source = "execute 'rm tempfile.txt';"
        model = parse_model_text(source)
        assert model is not None

    def test_execute_double_quotes(self):
        """Test execute with double-quoted string: execute \"command\";"""
        source = 'execute "echo hello";'
        model = parse_model_text(source)
        assert model is not None


class TestExecuteModifiers:
    """Test execute statement with modifiers."""

    def test_execute_async(self):
        """Test execute.async: execute.async 'long_running_script.sh';"""
        source = "execute.async 'long_running_script.sh';"
        model = parse_model_text(source)
        assert model is not None

    def test_execute_checkErrorLevel(self):
        """Test execute.checkErrorLevel: execute.checkErrorLevel 'command';"""
        source = "execute.checkErrorLevel 'make build';"
        model = parse_model_text(source)
        assert model is not None

    def test_execute_wait(self):
        """Test execute with wait modifier."""
        source = "execute.wait 'background_job.sh';"
        model = parse_model_text(source)
        assert model is not None


class TestExecuteWithoutSemicolon:
    """Test execute statement without trailing semicolon."""

    def test_execute_no_semicolon(self):
        """Test execute without semicolon (valid in some contexts)."""
        source = """
Scalar x / 1 /;
execute 'echo test'
"""
        model = parse_model_text(source)
        assert model is not None


class TestExecuteInControlFlow:
    """Test execute statement inside control flow structures."""

    def test_execute_in_if_block(self):
        """Test execute inside if block."""
        source = """
Scalar x / 1 /;
if(x > 0, execute 'script.sh';);
"""
        model = parse_model_text(source)
        assert model is not None

    def test_execute_in_if_block_no_semicolon(self):
        """Test execute as final statement in if block (no semicolon)."""
        source = """
Scalar x / 1 /;
if(x > 0, execute 'script.sh');
"""
        model = parse_model_text(source)
        assert model is not None

    def test_execute_in_loop(self):
        """Test execute inside loop."""
        source = """
Set i / 1*3 /;
loop(i, execute 'iteration_script.sh';);
"""
        model = parse_model_text(source)
        assert model is not None

    def test_execute_in_loop_final(self):
        """Test execute as final statement in loop (no semicolon)."""
        source = """
Set i / 1*3 /;
loop(i, execute 'iteration_script.sh');
"""
        model = parse_model_text(source)
        assert model is not None

    def test_execute_with_modifier_in_if(self):
        """Test execute with modifier inside if block."""
        source = """
Scalar x / 1 /;
if(x > 0, execute.async 'long_task.sh';);
"""
        model = parse_model_text(source)
        assert model is not None


class TestExecuteCaseInsensitive:
    """Test case insensitivity of execute statements."""

    def test_execute_uppercase(self):
        """Test uppercase EXECUTE."""
        source = "EXECUTE 'echo hello';"
        model = parse_model_text(source)
        assert model is not None

    def test_execute_mixedcase(self):
        """Test mixed case Execute."""
        source = "Execute 'echo hello';"
        model = parse_model_text(source)
        assert model is not None

    def test_execute_modifier_mixedcase(self):
        """Test mixed case with modifier."""
        source = "EXECUTE.Async 'script.sh';"
        model = parse_model_text(source)
        assert model is not None


class TestExecuteCompileTimeVariables:
    """Test execute statement with compile-time variables."""

    def test_execute_with_gams_scrdir(self):
        """Test execute with %gams.scrdir% compile-time variable."""
        source = "execute 'gnuplot %gams.scrdir%gnuplot.in';"
        model = parse_model_text(source)
        assert model is not None

    def test_execute_rm_with_compile_time_var(self):
        """Test execute rm with compile-time variable."""
        source = "execute 'rm %gams.scrdir%gnuplot.in';"
        model = parse_model_text(source)
        assert model is not None


class TestExecuteMultipleStatements:
    """Test multiple execute statements."""

    def test_execute_sequence(self):
        """Test sequence of execute statements."""
        source = """
execute 'echo step1';
execute 'echo step2';
execute 'echo step3';
"""
        model = parse_model_text(source)
        assert model is not None

    def test_execute_with_other_statements(self):
        """Test execute mixed with other statements."""
        source = """
Scalar x / 5 /;
execute 'prepare_data.sh';
x = x + 1;
execute 'process_results.sh';
"""
        model = parse_model_text(source)
        assert model is not None


class TestExecuteInscribedsquarePattern:
    """Test patterns from inscribedsquare.gms (the blocking model)."""

    def test_inscribedsquare_execute_pattern(self):
        """Test the exact pattern from inscribedsquare.gms."""
        source = """
execute 'gnuplot %gams.scrdir%gnuplot.in'
execute 'rm %gams.scrdir%gnuplot.in'
"""
        model = parse_model_text(source)
        assert model is not None

    def test_inscribedsquare_with_context(self):
        """Test execute in context similar to inscribedsquare.gms."""
        source = """
Set i / 1*10 /;
Parameter data(i);
data(i) = ord(i);

file f / 'gnuplot.in' /;
put f;
put 'plot data' /;
putclose f;

execute 'gnuplot gnuplot.in'
execute 'rm gnuplot.in'
"""
        model = parse_model_text(source)
        assert model is not None
