import xbmc
import xbmcgui
import xbmcaddon


class MediaIterator:
    def __init__(self):
        pass

    def forward(self):
        raise NotImplementedError("This method must be overridden.")

    def back(self):
        raise NotImplementedError("This method must be overridden.")

    def getCurrUrl(self):
        raise NotImplementedError("This method must be overridden.")

    def isCurrVideo(self):
        raise NotImplementedError("This method must be overridden.")

    def getVideoUrl(self):
        raise NotImplementedError("This method must be overridden.")


class MediaWindow(xbmcgui.WindowXMLDialog):
    ACTION_MAP = {
        xbmcgui.ACTION_MOVE_LEFT: 'back',
        xbmcgui.ACTION_MOVE_RIGHT: 'forward',
        xbmcgui.ACTION_SELECT_ITEM: 'playVideo',
        xbmcgui.ACTION_ENTER: 'playVideo',
        xbmcgui.ACTION_PLAY: 'playVideo'
    }

    BLACK_OVERLAY = 1
    IMG_CONTROL = 2
    PLAY_BUTTON = 3

    def __init__(self, iterator):
        super().__init__("ViewerWindow.xml", xbmcaddon.Addon(
            id='script.module.mediaviewer').getAddonInfo('path'))
        self.iterator = iterator
        self.img = None
        self.blackOverlay = None
        self.playButton = None
        self.player = MediaWindowPlayer(self)
        self.isVideoPlaying = False

    def onInit(self):
        self.blackOverlay = self.getControl(self.BLACK_OVERLAY)
        self.img = self.getControl(self.IMG_CONTROL)
        self.playButton = self.getControl(self.PLAY_BUTTON)
        self.setContent()

    def onAction(self, action):
        func_name = self.ACTION_MAP.get(action)
        if not self.isVideoPlaying and func_name:
            getattr(self, func_name)()
            self.setContent()

        if action in (xbmcgui.ACTION_STOP, xbmcgui.ACTION_PREVIOUS_MENU, xbmcgui.ACTION_NAV_BACK):
            if self.isVideoPlaying:
                self.stopVideo()
            else:
                self.close()

    def playVideo(self):
        if self.iterator.isCurrVideo():
            self.playButton.setVisible(False)
            self.player.play(item=self.iterator.getVideoUrl())

    def stopVideo(self):
        self.player.stop()

    def onPlayBackStarted(self):
        self.blackOverlay.setVisible(False)
        self.img.setVisible(False)
        self.isVideoPlaying = True

    def onPlayBackStopped(self):
        self.isVideoPlaying = False
        self.playButton.setVisible(True)
        self.img.setVisible(True)
        self.blackOverlay.setVisible(True)

    def setContent(self):
        self.img.setImage(self.iterator.getCurrUrl(), True)
        self.playButton.setVisible(self.iterator.isCurrVideo())


class MediaWindowPlayer(xbmc.Player):
    def __init__(self, mediaWindow, *args, **kwargs):
        self.mediaWindow = mediaWindow
        super(MediaWindowPlayer, self).__init__(*args, **kwargs)

    def onPlayBackStarted(self):
        self.mediaWindow.onPlayBackStarted()

    def onPlayBackStopped(self):
        self.mediaWindow.onPlayBackStopped()

    def onPlayBackEnded(self):
        self.mediaWindow.onPlayBackStopped()
