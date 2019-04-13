import os

import sublime
import sublime_plugin


class PlayAnimationCommand(sublime_plugin.WindowCommand):
    def run(self, delay=500):
        dire = os.path.join(os.path.dirname(__file__), "pics")
        files = os.listdir(dire)
        if len(files) > 0:
            view = self.window.new_file()
            view.run_command("play_text_animation",
                { "dir": dire, "files": files, "delay": delay })
        else:
            sublime.error_message(
                "There are no text-animation files under directory pics!")


class PlayTextAnimationCommand(sublime_plugin.TextCommand):
    def run(self, edit, dir, files, delay):
        if len(files) > 0:
            file = os.path.join(dir, files.pop(0))
            self.view.set_read_only(False)
            self.view.set_scratch(True)
            self.view.sel().clear()
            self.view.set_name("animation")
            self.load_animation(edit, file)
            self.view.set_read_only(True)
            sublime.set_timeout(lambda: self.view.run_command(self.name(),
                {"dir": dir , "files": files, "delay": delay}), delay)
        else:
            sublime.message_dialog("Done!")

    def load_animation(self, edit, file):
        region = sublime.Region(0, self.view.size())
        with open(file, encoding="utf8") as f:
            self.view.replace(edit, region, f.read())
