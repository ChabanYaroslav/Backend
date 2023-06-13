
trigger = True

def stop(s: str):
    print(s)
    if s is not "s":
        global trigger
        trigger = False

i = 0
print(trigger)
while trigger:
    stop("s")
    i += 1
    if i > 3:
        stop("x")

print(trigger)

