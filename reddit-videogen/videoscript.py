from datetime import datetime
from moviepy.editor import AudioFileClip
import voiceover

MAX_WORDS_PER_COMMENT = 100
MIN_COMMENTS_FOR_FINISH = 4
MIN_DURATION = 20
MAX_DURATION = 58

class VideoScript:
    """
    Represents a video script generated from comments.
    """
    title = ""
    fileName = ""
    titleSCFile = ""
    url = ""
    totalDuration = 0
    frames = []

    def __init__(self, url, title, fileId) -> None:
        """
        Initializes a VideoScript instance.

        Parameters:
        - url: The URL associated with the video.
        - title: The title of the video.
        - fileId: An identifier for the file.
        """
        self.fileName = f"{datetime.today().strftime('%Y-%m-%d')}-{fileId}"
        self.url = url
        self.title = title
        self.titleAudioClip = self.__createVoiceOver("title", title)

    def canBeFinished(self) -> bool:
        """
        Checks if the video can be considered finished.

        Returns:
        - True if there are frames and the total duration is above a minimum threshold.
        """
        return (len(self.frames) > 0) and (self.totalDuration > MIN_DURATION)

    def canQuickFinish(self) -> bool:
        """
        Checks if the video can be quickly finished.

        Returns:
        - True if there are enough frames and the total duration is above a minimum threshold.
        """
        return (len(self.frames) >= MIN_COMMENTS_FOR_FINISH) and (self.totalDuration > MIN_DURATION)

    def addCommentScene(self, text, commentId) -> None:
        """
        Adds a comment scene to the video script.

        Parameters:
        - text: The text content of the comment.
        - commentId: The identifier for the comment.
        """
        wordCount = len(text.split())
        if wordCount > MAX_WORDS_PER_COMMENT:
            return  # Comment exceeds word limit

        frame = ScreenshotScene(text, commentId)
        frame.audioClip = self.__createVoiceOver(commentId, text)
        if frame.audioClip is None:
            return  # Voiceover creation failed

        self.frames.append(frame)

    def getDuration(self):
        """
        Gets the total duration of the video script.

        Returns:
        - The total duration in seconds.
        """
        return self.totalDuration

    def getFileName(self):
        """
        Gets the generated filename for the video script.

        Returns:
        - The filename.
        """
        return self.fileName

    def __createVoiceOver(self, name, text):
        """
        Creates a voiceover for a given name and text.

        Parameters:
        - name: The name identifier.
        - text: The text content for the voiceover.

        Returns:
        - An AudioFileClip instance for the voiceover or None if duration exceeds limit.
        """
        file_path = voiceover.create_voice_over(f"{self.fileName}-{name}", text)
        audioClip = AudioFileClip(file_path)
        if self.totalDuration + audioClip.duration > MAX_DURATION:
            return None  # Voiceover exceeds maximum duration

        self.totalDuration += audioClip.duration
        return audioClip


class ScreenshotScene:
    """
    Represents a scene in the video script with text content.
    """
    text = ""
    screenShotFile = ""
    commentId = ""

    def __init__(self, text, commentId) -> None:
        """
        Initializes a ScreenshotScene instance.

        Parameters:
        - text: The text content of the scene.
        - commentId: The identifier for the comment associated with the scene.
        """
        self.text = text
        self.commentId = commentId
