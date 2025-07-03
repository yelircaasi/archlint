import sys
from typing import cast

import click

from . import (
    check_docs_structure,
    check_imports,
    check_method_order,
    check_tests_structure,
)
from .collection import (
    collect_docs_objects,
    collect_source_objects,
    collect_tests_objects,
)
from .configuration import Configuration, get_config


@click.group(invoke_without_command=True)
@click.pass_context
def archlint_cli(ctx: click.Context):
    ctx.ensure_object(dict)["CFG"] = get_config()

    if ctx.invoked_subcommand is None:
        return ctx.invoke(_)


@archlint_cli.command(help="Check test organization and conventions.")
@click.option("--fail-fast", is_flag=True, help="Stop on first failure.")
@click.pass_context
def tests(ctx: click.Context, fail_fast: bool) -> bool:
    cfg: Configuration = ctx.obj["CFG"]
    source_objects = collect_source_objects(cfg.module_root_dir)
    tests_objects = collect_tests_objects(cfg.tests.unit_dir, cfg.root_dir)

    report, problems = check_tests_structure(cfg, source_objects, tests_objects)
    click.echo(report)
    click.echo()

    return problems


@archlint_cli.command(help="Verify documentation presence and formatting.")
@click.option("--check-links", is_flag=True, help="Check for broken links.")
@click.pass_context
def docs(ctx: click.Context, check_links: bool) -> bool:
    cfg: Configuration = ctx.obj["CFG"]
    source_objects = collect_source_objects(cfg.module_root_dir)
    docs_objects = collect_docs_objects(cfg.docs.md_dir, cfg.root_dir)

    report, problems = check_docs_structure(cfg, source_objects, docs_objects)
    click.echo(report)
    click.echo()

    return problems


@archlint_cli.command(help="Inspect import structures and dependencies.")
@click.option("--allow-cycles", is_flag=True, help="Allow circular imports.")
@click.pass_context
def imports(ctx: click.Context, allow_cycles: bool) -> bool:
    report, problems = check_imports(ctx.obj["CFG"])
    click.echo(report)
    click.echo()

    return problems


@archlint_cli.command(help="Check method structure and naming conventions.")
@click.option("--max-lines", type=int, default=50, help="Max lines per method.")
@click.pass_context
def methods(ctx: click.Context, max_lines: int) -> bool:
    cfg: Configuration = ctx.obj["CFG"]
    source_objects = collect_source_objects(cfg.module_root_dir)
    report, problems = check_method_order(cfg, source_objects)
    click.echo(report)
    click.echo()

    return problems


@archlint_cli.command(name="all", help="Check method structure and naming conventions.")
@click.option("--max-lines", type=int, default=50, help="Max lines per method.")
@click.pass_context
def _(ctx: click.Context, max_lines: int) -> bool:
    cfg: Configuration = ctx.obj["CFG"]

    source_objects = collect_source_objects(cfg.module_root_dir)
    tests_objects = collect_tests_objects(cfg.tests.unit_dir, cfg.root_dir)
    docs_objects = collect_docs_objects(cfg.docs.md_dir, cfg.root_dir)

    mo_report, mo_problems = check_method_order(cfg, source_objects)
    docs_report, docs_problems = check_docs_structure(cfg, source_objects, docs_objects)
    tests_report, tests_problems = check_tests_structure(cfg, source_objects, tests_objects)
    imports_report, imports_problems = check_imports(cfg)

    click.echo(mo_report)
    click.echo(docs_report)
    click.echo(tests_report)
    click.echo(imports_report)
    click.echo()

    return any((mo_problems, docs_problems, tests_problems, imports_problems))


def main():
    problems = archlint_cli(standalone_mode=False)
    sys.exit(int(problems))
