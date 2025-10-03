import click


@click.group()
def myapp() -> None:
    pass


@myapp.command()
@click.option(
    "-t",
    "--tenant-name",
    required=True,
    help="Name of the tenant to add",
    type=str,
)
@click.option(
    "-a",
    "--active",
    help="Flag to indicate whether the tenant is active",
    type=bool,
    default=True,
)
def add_tenant(
    tenant_name: str,
    active: bool,
) -> None:
    click.echo(f"{tenant_name=}-{active=}")


@myapp.command()
@click.option(
    "-u",
    "--user-name",
    required=True,
    help="Name of the user to add",
    type=str,
)
@click.option(
    "-p",
    "--password",
    required=True,
    help="Password",
    type=str,
)
@click.option(
    "-t",
    "--tenant",
    required=True,
    help="Name of the tenant user to be associated with",
    type=str,
)
def add_user(
    user_name: str,
    password: str,
    tenant: str,
) -> None:
    click.echo(f"{user_name=}-{password=}-{tenant=}")