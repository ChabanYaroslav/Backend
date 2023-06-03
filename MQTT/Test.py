import message.json_message as m

message = m.json_message("1000")
print(message)
print(message)
encode = m.loads(message)
if encode["action"] == "1000":
    print("str")
print(encode["action"][0])
s = encode["body"]
print(len(s))


