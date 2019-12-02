import os
import slack
import sys


@slack.RTMClient.run_on(event='message')
def process_slack_message(**payload):
    print("Received Slack Message")
    data = payload['data']
    web_client = payload['web_client']
    channel_id = data['channel']
    thread_ts = data['ts']
    if "user" not in list(data.keys()):
        return
    user = data['user']

    if '//last' in data['text']:
        with open("{}/{}_scores.txt".format(PROJ_PATH, ML), "r") as f:
            last_line = list(f)[-1].split(',')
        an = last_line[0]
        an = "XXXX" + an[-4:]
        ba_score = float(last_line[1].strip())
        yrs = int(ba_score / 12)
        months = round(ba_score % 12, 2)

        web_client.chat_postMessage(
            channel=channel_id,
            text=f"Last Accession Number: {an}\n" +
                 f"Last Bone Age Score: {yrs} year(s) and {months} month(s)"
        )
    elif '//flush' in data['text']:
        web_client.chat_postMessage(
            channel=channel_id,
            text=f"Flush requested - <@{user}>",
            thread_ts=thread_ts
        )
    elif '//process' in data['text']:
        an = data['text'].split(" ")[1]
        # validate a/n

        with open("{}/{}_scores.txt".format(PROJ_PATH, ML), "r") as f:
            lines = f.readlines()
        with open("{}/{}_scores.txt".format(PROJ_PATH, ML), "w") as f:
            for line in lines:
                if an not in line:
                    f.write(line)
        with open("{}/{}_slack_an.txt".format(PROJ_PATH, ML), "w+") as f:
            f.write(an)
        web_client.chat_postMessage(
            channel=channel_id,
            text=f"Processing of accession number {an} requested - <@{user}>",
            thread_ts=thread_ts
        )


if __name__ == "__main__":
    global PROJ_PATH
    global ML
    PROJ_PATH = sys.argv[1]
    ML = sys.argv[2]
    rtm_client = slack.RTMClient(token=os.environ["SLACK_BOT_TOKEN"])
    rtm_client.start()
