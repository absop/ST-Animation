import os
import re
import random

import sublime
import sublime_plugin


__playing__ = '__z{|}~__'


class PlayAnimationCommand(sublime_plugin.WindowCommand):
    def run(self):
        if not hasattr(self, 'cards'):
            self.cards = self.find_cards()
            self.index = 0
        if not self.cards:
            sublime.error_message('No cards found!')
        elif view := self.find_or_new_view():
            view.settings().set(__playing__, True)
            view.run_command('play_card', {'card': self.next_card()})

    def next_card(self):
        card = self.cards[self.index]
        self.index = (self.index + 1) % len(self.cards)
        return card

    def find_or_new_view(self):
        for view in self.window.views():
            play = view.settings().get(__playing__)
            if play is None:
                continue
            self.window.focus_view(view)
            if play is True:
                sublime.status_message('busying...')
                return None
            else:
                return view
        view = self.window.new_file()
        view.settings().set('draw_white_space', None)
        view.settings().set('draw_indent_guides', False)
        view.settings().set('line_numbers', False)
        view.settings().set('highlight_line', False)
        view.settings().set('highlight_gutter', False)
        # view.settings().set('block_caret', True)
        view.settings().set(__playing__, False)
        view.set_scratch(True)
        return view

    def find_cards(self):
        cards = []
        for path in sublime.find_resources('*.ca'):
            if path[8:].startswith('/Animation/pics/'):
                cards.append(path)
        return cards


class PlayCardCommand(sublime_plugin.TextCommand):
    def run(self, edit, card):
        view = self.view
        view.set_name(os.path.basename(card))
        text = sublime.load_resource(card)
        fill = re.sub('.', ' ', text)
        chars = list(filter(lambda c: not c[1].isspace(), enumerate(text)))
        random.shuffle(chars)
        view.set_read_only(False)
        view.replace(edit, sublime.Region(0, view.size()), fill)
        view.run_command('play_chars', {'chars': chars})


class PlayCharsCommand(sublime_plugin.TextCommand):
    def run(self, edit, chars=[], delay=16):
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
                lambda: self.view.run_command(self.name(), {'delay': delay}),
                delay)
        else:
            self.view.sel().clear()
            self.view.settings().set(__playing__, False)
