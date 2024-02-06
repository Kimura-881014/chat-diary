message = [{'type': 'text','text': 'test1'},
                   {'type': 'text',
                    'text': 'test2'}]

test_li = []

def add_quick_replay(message,user_id):
    quick_list = {"quickReply": {
    "items": [
    {
        "type": "action",
        "action": {
                    "type": "uri",
                    "label": "日記を見る",
                    "uri": "https://www.google.com"
                    }
    },
    {
        "type": "action",
        "action": {
                    "type": "message",
                    "label": "保存する",
                    "text": "保存"
                    }
    },
    {
        "type": "action",
        "action": {
                    "type": "message",
                    "label": "違う答えをつくる",
                    "text": "やり直し"
                    }
    }
    ]
    }}

    test_dic = {"test_add":"value_add"}

    message.append(test_dic)
    message[-1]["test_add"] = "hoge","hoge2"
    return message[-1].values()

print(add_quick_replay(message,"ub14"))

# li = []
# dic = {"test":"value"}

# test_add = li.append(dic)
# print(test_add)