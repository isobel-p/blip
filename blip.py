import click
import desktop_notifier
import dateparser
import json
import os
import sys
import subprocess
import asyncio
import datetime

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
@click.option("--title", prompt="title of blip", help="big notification title", required=True)
@click.option("--message", prompt="message of blip", help="little notification message", required=True)
@click.option("--time", prompt="blip date & time", help="datetime of notification", required=True)
def new(title, message, time):
    click.echo("parsing datetime...")
    dt = dateparser.parse(time)
    if dt is None:
        click.echo(click.BadParameter(f'{time} is not a valid date and/or time!'))
        return
    else:
        click.echo(f"parsed datetime: {dt}")
    click.echo("saving to user notifications...")
    if not os.path.exists("blips.json"):
        with open("blips.json", "w") as f:
            json.dump([], f)
    try:
        with open("blips.json", "r") as f:
            alarms = json.load(f)
    except Exception as e:
        return click.echo(click.ClickException(e))
    alarms.append({
        "title": title,
        "message": message,
        "time": dt.isoformat(),
    })
    with open("blips.json", "w") as f:
        json.dump(alarms, f, indent=2)
    click.echo("new blip created successfully!")

async def notify(blip_title, blip_message) -> None:
    notifier = desktop_notifier.DesktopNotifier(app_name="blip")
    await notifier.send(
        title=blip_title,
        message=blip_message,
        sound=desktop_notifier.DEFAULT_SOUND
    )

@click.command()
def run():
    if not os.path.exists("blips.json"):
        return
    with open("blips.json", "r") as f:
        try:
            alarms = json.load(f)
        except Exception as e:
            alarms = []
    now = datetime.datetime.now().replace(second=0, microsecond=0)
    due = []
    remaining = []
    for alarm in alarms:
        alarm_time = dateparser.parse(alarm["time"])
        if alarm_time is not None and alarm_time.replace(second=0, microsecond=0) == now:
            due.append(alarm)
        else:
            remaining.append(alarm)
    with open("blips.json", "w") as f:
        json.dump(remaining, f, indent=2)
    for alarm in due:
        asyncio.run(notify(alarm["title"], alarm["message"]))

@click.command()
def activate():
    if sys.platform == "win32":
        click.echo("setting up background notifications - do not close the app!")
        cmd = [
            "schtasks", "/Create", "/TN", "Blip",
            "/TR", f'"{os.path.abspath(sys.argv[0])}" run',
            "/SC", "MINUTE",
            "/F"
        ]
        subprocess.run(cmd, creationflags=subprocess.CREATE_NO_WINDOW)
        click.echo("blip notifications activated! pings will now begin >:)")
        asyncio.run(notify("testing!", "blip is working!"))
    else:
        click.echo(click.ClickException("only for windows rn!"))

@click.command()
def deactivate():
    if sys.platform == "win32":
        if click.confirm("are you sure? you WILL NOT receive notifications from blip until you reactivate.", abort=True):
            click.echo("deleting background notifications - do not close the app!")
            cmd = ["schtasks", "/Delete", "/TN", "Blip", "/F"]
            subprocess.run(cmd, creationflags=subprocess.CREATE_NO_WINDOW)
            click.echo("done. no more blip notifications :_(")
    else:
        click.echo(click.ClickException("only for windows rn!"))

@click.command()
def status():
    if sys.platform == "win32":
        click.echo("checking background notifications - do not close the app!")
        cmd = ["schtasks", "/Query", "/TN", "Blip"]
        result = subprocess.run(cmd, creationflags=subprocess.CREATE_NO_WINDOW, capture_output=True, text=True)
        click.echo("blip has been activated!" if result.returncode==0 else "blip has been deactivated")
        asyncio.run(notify("testing!", "blip is working!"))
    else:
        click.echo(click.ClickException("only for windows rn!"))

cli.add_command(hi)
cli.add_command(new)
cli.add_command(run)
cli.add_command(activate)
cli.add_command(status)
cli.add_command(deactivate)

if __name__ == "__main__":
    cli()