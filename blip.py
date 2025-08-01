import click
import desktop_notifier
import asyncio

@click.group()
def cli():
    pass

@click.command()
@click.option("--special", default="normal", help="special greetings (normal/cat/lolcat/dog/puppy/cowboy/ping)")
def hi(special):
    match special:
        case "normal":
            click.echo("Hi!")
        case "cat":
            click.echo("meow :3")
        case "lolcat":
            click.echo("oh hai!!!")
        case "dog":
            click.echo("Woof!")
        case "puppy":
            click.echo("yip!")
        case "cowboy":
            click.echo("Howdy.")
        case "ping":
            click.echo("blip!")
        case _:
            click.echo("Hello")

cli.add_command(hi)

if __name__ == "__main__":
    cli()