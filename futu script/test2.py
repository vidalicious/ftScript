import Queue

q = []

q.insert(0, 1)
q.insert(0, 2)
q.insert(0, 3)
q.insert(0, 4)
if len(q) > 3:
    q = q[:3]

for i in q:

    print i
print len(q)
