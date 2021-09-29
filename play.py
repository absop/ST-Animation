import os
import re
import random

import sublime
import sublime_plugin


class PlayAnimationCommand(sublime_plugin.WindowCommand):
    def run(self):
        cards = self.find_resource()
        if len(cards) > 0:
            view = self.window.new_file()
            view.set_name("animation")
            view.settings().set('draw_white_space', None)
            view.settings().set('draw_indent_guides', False)
            view.settings().set('line_numbers', False)
            view.settings().set('highlight_line', False)
            view.settings().set('highlight_gutter', False)
            # view.settings().set('block_caret', True)
            view.set_scratch(True)
            view.run_command("play_cards", { "cards": cards,})
        else:
            sublime.error_message(
                "There are no text-animation files under directory pics!")

    def find_resource(self):
        resources = []
        for path in sublime.find_resources('*.ca'):
            if path[8:].startswith('/Animation/pics/'):
                resources.append(path)
        return resources


class PlayCardsCommand(sublime_plugin.TextCommand):
    def run(self, edit, cards=[]):
        if cards:
            self.cards = cards
            self.index = 0
        if hasattr(self, 'cards') and self.index < len(self.cards):
            card = self.cards[self.index]
            self.index += 1
            text = sublime.load_resource(card)
            self.view.set_name(os.path.basename(card))
            fill = re.sub('.', ' ', text)
            chars = list(filter(lambda c: not c[1].isspace(), enumerate(text)))
            random.shuffle(chars)
            self.view.set_read_only(False)
            self.view.replace(edit, sublime.Region(0, self.view.size()), fill)
            self.view.run_command('play_chars', {'chars': chars})
        else:
            sublime.message_dialog('All cards have been played!')


class PlayCharsCommand(sublime_plugin.TextCommand):
    def run(self, edit, chars=[], delay=0):
        if chars:
            self.chars = chars
            self.index = 0
        if hasattr(self, 'chars') and self.index < len(self.chars):
            point, char = self.chars[self.index]
            self.index += 1
            caret = sublime.Region(point, point + 1)
            self.view.sel().clear()
            # self.view.sel().add(point)
            self.view.set_read_only(False)
            self.view.replace(edit, caret, char)
            # self.view.sel().clear()
            # self.view.sel().add(point + 1)
            self.view.set_read_only(True)
            sublime.set_timeout_async(
                lambda: self.view.run_command('play_chars'),
                delay)
        else:
            full_text = sublime.Region(0, self.view.size())
            self.view.erase(edit, full_text)
            self.view.sel().clear()
            choice = sublime.yes_no_cancel_dialog(
                'This card has played done, play next?',
                yes_title='next card',
                no_title='',
                title='Sublime Play Animation')
            if choice == sublime.DIALOG_YES:
                self.view.run_command('play_cards')
