import client
import action
import time

action_sender = client.client(5052)

action = action.action()

ACTION_NAMES = (
    "surprise_continue", 
    "Kick",
    "jump",
    "sit_continue",
    "clap",
    "tpose_continue",
    "kamehameha_continue",
    "swing",
    "upper",
    "cross_continue"
)

def send_message(messages: dict) : 
    for key, value in messages.items() :
        if (value) :
            action_sender.send_command(key)

for msg in ACTION_NAMES :
    for i in range(3) :
        action.change_message(msg)
        send_message(action.message)
        action.reset_message()
        time.sleep(1)