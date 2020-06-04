from cleo import Application

from .commands.concat import ConcatCommand


application = Application()

# add commands
application.add(ConcatCommand())


if __name__ == "__main__":
    application().run()