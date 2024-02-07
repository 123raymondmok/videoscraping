import os
import re
import praw
import markdown_to_text
import time
from videoscript import VideoScript
import configparser

# Read configuration from 'config.ini' file
config = configparser.ConfigParser()
config.read('config.ini')
CLIENT_ID = config["Reddit"]["CLIENT_ID"]
CLIENT_SECRET = config["Reddit"]["CLIENT_SECRET"]
USER_AGENT = config["Reddit"]["USER_AGENT"]
SUBREDDIT = config["Reddit"]["SUBREDDIT"]

def getContent(outputDir, postOptionCount) -> VideoScript:
    """
    Get content from top posts in a subreddit and create a VideoScript.

    Parameters:
    - outputDir: Directory where the video script will be saved.
    - postOptionCount: Number of top posts to consider.

    Returns:
    - An instance of VideoScript containing content from the selected post.
    """
    reddit = __getReddit()
    existingPostIds = __getExistingPostIds(outputDir)

    now = int(time.time())
    autoSelect = postOptionCount == 0
    posts = []

    for submission in reddit.subreddit(SUBREDDIT).top(time_filter="day", limit=postOptionCount * 3):
        if f"{submission.id}.mp4" in existingPostIds or submission.over_18:
            continue
        hoursAgoPosted = (now - submission.created_utc) / 3600
        print(f"[{len(posts)}] {submission.title}     {submission.score}    {'{:.1f}'.format(hoursAgoPosted)} hours ago")
        posts.append(submission)
        if autoSelect or len(posts) >= postOptionCount:
            break

    if autoSelect:
        return __getContentFromPost(posts[0])
    else:
        postSelection = int(input("Input: "))
        selectedPost = posts[postSelection]
        return __getContentFromPost(selectedPost)

def getContentFromId(outputDir, submissionId) -> VideoScript:
    """
    Get content from a specific Reddit post by submission ID and create a VideoScript.

    Parameters:
    - outputDir: Directory where the video script will be saved.
    - submissionId: ID of the Reddit post.

    Returns:
    - An instance of VideoScript containing content from the specified post.
    """
    reddit = __getReddit()
    existingPostIds = __getExistingPostIds(outputDir)

    if submissionId in existingPostIds:
        print("Video already exists!")
        exit()
    try:
        submission = reddit.submission(submissionId)
    except praw.exceptions.NotFound:
        print(f"Submission with id '{submissionId}' not found!")
        exit()
    return __getContentFromPost(submission)

def __getReddit():
    """
    Create and return a Reddit instance using praw.

    Returns:
    - A praw.Reddit instance.
    """
    return praw.Reddit(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        user_agent=USER_AGENT
    )

def __getContentFromPost(submission) -> VideoScript:
    """
    Extract content from a Reddit post and create a VideoScript.

    Parameters:
    - submission: A praw.Submission instance.

    Returns:
    - An instance of VideoScript containing content from the post.
    """
    content = VideoScript(submission.url, submission.title, submission.id)
    print(f"Creating video for post: {submission.title}")
    print(f"Url: {submission.url}")

    failedAttempts = 0
    for comment in submission.comments:
        if content.addCommentScene(markdown_to_text.markdown_to_text(comment.body), comment.id):
            failedAttempts += 1
        if content.canQuickFinish() or (failedAttempts > 2 and content.canBeFinished()):
            break
    return content

def __getExistingPostIds(outputDir):
    """
    Get a list of existing post IDs from files in the output directory.

    Parameters:
    - outputDir: Directory where the video scripts are stored.

    Returns:
    - A list of existing post IDs.
    """
    files = os.listdir(outputDir)
    # Filtering only files (ignoring directories)
    files = [f for f in files if os.path.isfile(os.path.join(outputDir, f))]
    return [re.sub(r'.*?-', '', file) for file in files]
