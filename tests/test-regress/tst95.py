a = b = c = 1
exec "a = 2"
exec ("b = " +
    "c = " +
    "2")
assert a == 2 and b == 2 and c == 2
