def replace(string, index, replace, char="%"):
    s, count = list(string), []
    for i, character in enumerate(s):
        if character == char: count.append(i)
    s[count[index]] = replace
    return "".join(s)

n = "hello %!"

print(replace(n, 0, "[idkman]"))
