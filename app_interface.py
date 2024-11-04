from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput


class Example(App):
    def build(self):
        self.window = GridLayout()
        self.window.cols = 1

        self.comments = Label(text='Your comments:')
        self.window.add_widget(self.comments)

        self.user = TextInput(multiline=True)
        self.window.add_widget(self.user)
        return self.window


if __name__ == "__main__":
    Example().run()
