def s_to_l(s):
    return [item.strip() for item in s.strip("[]").split(",")]

line = "call x [1, 3]"

print(s_to_l(line.split("[")[1]))