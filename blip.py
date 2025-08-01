import click
import desktop_notifier
import asyncio
import dateparser
import re

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

@click.command()
@click.option("--title", prompt="title of notification", help="big notification title", required=True)
@click.option("--message", prompt="message of notification", help="little notification message", required=True)
@click.option("--urgency", default="normal", help="urgency of notification (low/normal/critical)")
@click.option("--time", prompt="notification date & time", help="datetime of notification", required=True)
def new(title, message, urgency, time):
    dt = dateparser.parse(time)
    if dt == None:
        click.echo(click.BadParameter(f'{time} is not a valid date and/or time!'))
    else:
        click.echo(f"Parsed datetime: {dt}")
    click.echo("Done")


cli.add_command(hi)
cli.add_command(new)

if __name__ == "__main__":
    cli()