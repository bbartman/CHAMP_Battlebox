import kivy, os.path, os
from kivy.config import Config
from kivy.logger import Logger
from kivy.animation import Animation
from kivy.core.audio import SoundLoader
from concurrent.futures import ThreadPoolExecutor
# from multiprocessing.pool import ThreadPool
from functools import partial

class SoundBoard:
    def _load_sound_cfg(self, cfgName):
        path = ""
        try:
            path = os.path.join(self.directory, Config.get("media_sounds", cfgName))
        except ValueError:
            Logger.error(f"SoundBoard: Missing sound configuration {cfgName}")
            raise
        
        if not os.path.exists(path):
            Logger.error(f"SoundBoard: Invalid path to sound Path = {path} Configuration = {cfgName}")
            raise ValueError(f"Invalid path {path}")
        Logger.info(f"SoundBoard: attempting to load sound {cfgName} from path {path}")
        sound = self.loader.load(path)
        if not sound:
            Logger.error(f"SoundBoard: Failed to load sound {path} from {cfgName}")
            raise ValueError(f"Failed to load sound {path} from {cfgName}")

        Logger.info(f"SoundBoard: Loaded {cfgName} from path {path}")
        return sound

    def __init__(self):
        self.soundPlayerPool = ThreadPoolExecutor(max_workers=1) 
        self.loader = SoundLoader
        self.directory = Config.get("media_sounds", "directory", fallback=".")
        Logger.info(f"SoundBoard: seaching for sounds in directory {self.directory}")
        self.cd_three = self._load_sound_cfg("three")
        self.cd_two = self._load_sound_cfg("two")
        self.cd_one = self._load_sound_cfg("one")
        self.cd_fight = self._load_sound_cfg("fight")
        self.cd_go = self._load_sound_cfg("go")
        self.soccer_screen = self._load_sound_cfg("soccer")
        self.deathmatch_screen = self._load_sound_cfg("deathmatch")

    def _play(self, sound):
        Logger.info(f"Attempting to play through aplay {sound.source}")
        os.system(f"aplay {sound.source}")

    def aplay(self, sound):
        self.soundPlayerPool.submit(partial(self._play, sound))

