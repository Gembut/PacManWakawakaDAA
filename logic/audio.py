"""
Small sound wrapper for game events.
"""

from pathlib import Path

import pygame


class SoundManager:
    """Load and play Pac-Man sound effects without crashing if audio is unavailable."""

    def __init__(self):
        self.enabled = False
        self.sounds = {}
        self.waka_channel = None
        self.event_channel = None
        self.ghost_channel = None
        self.effect_channel = None
        self.current_ghost_loop = None
        self.current_event = None
        self.current_effect = None

        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            pygame.mixer.set_num_channels(8)

            self.sounds = {
                "credit": self._load("01. Credit Sound.mp3"),
                "start": self._load("02. Start Music.mp3"),
                "waka": self._load("03. PAC-MAN - Eating The Pac-dots.mp3"),
                "turn_waka": self._load(
                    "04. PAC-MAN - Turning The Corner While Eating The Pac-dots.mp3"
                ),
                "extend": self._load("05. Extend Sound.mp3"),
                "ghost_normal": self._load("06. Ghost - Normal Move.mp3"),
                "ghost_spurt_1": self._load("07. Ghost - Spurt Move #1.mp3"),
                "ghost_spurt_2": self._load("08. Ghost - Spurt Move #2.mp3"),
                "ghost_spurt_3": self._load("09. Ghost - Spurt Move #3.mp3"),
                "ghost_spurt_4": self._load("10. Ghost - Spurt Move #4.mp3"),
                "fruit": self._load("11. PAC-MAN - Eating The Fruit.mp3"),
                "frightened": self._load("12. Ghost - Turn to Blue.mp3"),
                "eat_ghost": self._load("13. PAC-MAN - Eating The Ghost.mp3"),
                "ghost_return": self._load("14. Ghost - Return to Home.mp3"),
                "death": self._load("15. Fail.mp3"),
                "coffee_break": self._load("16. Coffee Break Music.mp3"),
            }
            self.waka_channel = pygame.mixer.Channel(0)
            self.event_channel = pygame.mixer.Channel(1)
            self.ghost_channel = pygame.mixer.Channel(2)
            self.effect_channel = pygame.mixer.Channel(3)
            self.enabled = True
        except pygame.error as error:
            print(f"Audio disabled: {error}")
        except FileNotFoundError as error:
            print(f"Audio disabled: missing {error.filename}")

    def _load(self, filename):
        return pygame.mixer.Sound(str(Path("sounds") / filename))

    def play(self, sound_name):
        """Play a single sound effect."""
        if not self.enabled:
            return

        sound = self.sounds.get(sound_name)
        if sound is not None and self.event_channel is not None:
            if self.current_event == sound_name and self.event_channel.get_busy():
                return
            self.event_channel.play(sound)
            self.current_event = sound_name

    def play_exclusive(self, sound_name):
        """Stop gameplay audio and play one event sound by itself."""
        if not self.enabled:
            return

        self.stop_all()
        self.play(sound_name)

    def loop_event(self, sound_name):
        """Loop one event sound without stacking it."""
        if not self.enabled:
            return

        sound = self.sounds.get(sound_name)
        if sound is not None and self.event_channel is not None:
            if self.current_event == sound_name and self.event_channel.get_busy():
                return
            self.event_channel.play(sound, loops=-1)
            self.current_event = sound_name

    def sound_length(self, sound_name):
        """Return the sound length in seconds, or 0 when unavailable."""
        sound = self.sounds.get(sound_name)
        return sound.get_length() if sound is not None else 0

    def is_event_playing(self, sound_name=None):
        """Check whether an event sound is currently playing."""
        if not self.enabled or self.event_channel is None:
            return False

        if sound_name is not None and self.current_event != sound_name:
            return False

        return self.event_channel.get_busy()

    def play_once(self, sound_name):
        """Play a one-shot effect without stacking the same sound."""
        if not self.enabled:
            return

        sound = self.sounds.get(sound_name)
        if sound is not None and self.effect_channel is not None:
            if self.current_effect == sound_name and self.effect_channel.get_busy():
                return
            self.effect_channel.play(sound)
            self.current_effect = sound_name

    def start_waka(self):
        """Start waka sound while Pac-Man is actively eating pellets."""
        if not self.enabled:
            return

        sound = self.sounds.get("waka")
        if sound is not None and self.waka_channel is not None:
            if not self.waka_channel.get_busy():
                self.waka_channel.play(sound, loops=-1)

    def stop_waka(self):
        """Stop the pellet sound when Pac-Man is no longer eating."""
        if self.enabled and self.waka_channel is not None:
            self.waka_channel.stop()

    def update_ghost_loop(self, game_state, is_frightened, has_eaten_ghosts):
        """Loop the ghost sound that matches the current gameplay state."""
        if not self.enabled or self.ghost_channel is None:
            return

        if game_state != "playing" or self.is_event_playing("start"):
            self.ghost_channel.stop()
            self.current_ghost_loop = None
            return

        if has_eaten_ghosts:
            sound_name = "ghost_return"
        elif is_frightened:
            sound_name = "frightened"
        else:
            sound_name = "ghost_normal"

        if self.current_ghost_loop == sound_name and self.ghost_channel.get_busy():
            return

        sound = self.sounds.get(sound_name)
        if sound is not None:
            self.ghost_channel.play(sound, loops=-1)
            self.current_ghost_loop = sound_name

    def stop_all(self):
        """Stop all managed audio channels."""
        if not self.enabled:
            return

        for channel in (
            self.waka_channel,
            self.event_channel,
            self.ghost_channel,
            self.effect_channel,
        ):
            if channel is not None:
                channel.stop()
        self.current_ghost_loop = None
        self.current_event = None
        self.current_effect = None
