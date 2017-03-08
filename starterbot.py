import os
import random
import time
from slackclient import SlackClient
import textblob


# starterbot's ID as an environment variable
BOT_ID = os.environ.get("BOT_ID")

# constants
AT_BOT = "<@" + BOT_ID + ">"
EXAMPLE_COMMAND = "do"

#Movie quotes
QUOTES = (
    """Archaeology is the search for fact... not truth. If it's truth you're looking for, Dr. Tyree's philosophy class is right down the hall.""",
    """Nothing shocks me. I'm a scientist.""",
    """I'm like a bad penny, I always turn up.""",
    """DON'T call me Junior!""",
)

# instantiate Slack & Twilio clients
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))

def handle_command(text, channel, bot_mentioned):
    """
    Decide how to process the text that was received.
    """
    respond = False
    if bot_mentioned or random.random() >= 0.5:
        respond = True
        text = text.replace(AT_BOT, "")
    else:
        print("I choose not to respond.")
    if respond: 
        t = textblob.TextBlob(text)
        wl = t.noun_phrases
        if len(wl) > 0:
            np = random.choice(wl).singularize().pluralize()
            response = "{0}!  Why did it have to be {0}?  I hate {0}!".format(np)
        else:
            response = random.choice(QUOTES)
        slack_client.api_call(
            "chat.postMessage", 
            channel=channel,
            text=response, 
            as_user=True)

def parse_slack_output(slack_rtm_output):
    """
    The Slack Real Time Messaging API is an events firehose.

    Yields text, channel, bot_mentioned, user        
    """
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output:
                if AT_BOT in output['text']:
                    bot_mentioned = True
                else:
                    bot_mentioned = False
                user = output.get("user", None)
                result = tuple([
                    output['text'].strip(), 
                    output['channel'],
                    bot_mentioned,
                    user])
                yield result

if __name__ == "__main__":
    print("BOT_ID: {0}".format(BOT_ID))
    print("AT_BOT: {0}".format(AT_BOT))
    READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose
    if slack_client.rtm_connect():
        print("StarterBot connected and running!")
        while True:
            for text, channel, bot_mentioned, user in parse_slack_output(slack_client.rtm_read()):
                print("text: {0}\nchannel:{1}\nbot_mentioned: {2}\nuser: {3}\n".format(
                    text,
                    channel,
                    bot_mentioned,
                    user))
                if user != BOT_ID:
                    if text and channel:
                        handle_command(text, channel, bot_mentioned)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")
