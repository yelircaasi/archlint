import sys

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
)
from .configuration import Configuration, get_config


def main():
    problems = archlint_cli(standalone_mode=False)
    sys.exit(int(problems))


@click.group(invoke_without_command=True)
@click.pass_context
def archlint_cli(ctx: click.Context):
    ctx.ensure_object(dict)["CFG"] = get_config()

    if ctx.invoked_subcommand is None:
        return ctx.invoke(run_all)


@archlint_cli.command(name="all", help="Run all checks: methods, docs, tests, imports.")
@click.pass_context
def run_all(ctx: click.Context) -> bool:
    cfg: Configuration = ctx.obj["CFG"]

    source_objects = collect_source_objects(cfg.module_root_dir, cfg.root_dir)
    tests_objects = collect_source_objects(cfg.tests.unit_dir, cfg.root_dir)
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


@archlint_cli.command(help="Verify documentation presence and formatting.")
@click.pass_context
def docs(ctx: click.Context) -> bool:
    cfg: Configuration = ctx.obj["CFG"]
    source_objects = collect_source_objects(cfg.module_root_dir, cfg.root_dir)
    docs_objects = collect_docs_objects(cfg.docs.md_dir, cfg.root_dir)

    report, problems = check_docs_structure(cfg, source_objects, docs_objects)
    click.echo(report)
    click.echo()

    return problems


@archlint_cli.command(help="Inspect import structures and dependencies.")
@click.pass_context
def imports(ctx: click.Context) -> bool:
    report, problems = check_imports(ctx.obj["CFG"])
    click.echo(report)
    click.echo()

    return problems


@archlint_cli.command(help="Check method structure and naming conventions.")
@click.pass_context
def methods(ctx: click.Context) -> bool:
    cfg: Configuration = ctx.obj["CFG"]
    source_objects = collect_source_objects(cfg.module_root_dir, cfg.root_dir)
    report, problems = check_method_order(cfg, source_objects)
    click.echo(report)
    click.echo()

    return problems


@archlint_cli.command(help="Check test organization and conventions.")
@click.pass_context
def tests(ctx: click.Context) -> bool:
    cfg: Configuration = ctx.obj["CFG"]
    source_objects = collect_source_objects(cfg.module_root_dir, cfg.root_dir)
    tests_objects = collect_source_objects(cfg.tests.unit_dir, cfg.root_dir)

    report, problems = check_tests_structure(cfg, source_objects, tests_objects)
    click.echo(report)
    click.echo()

    return problems
