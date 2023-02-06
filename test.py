# Definition for singly-linked list.
from typing import Optional


class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


class Solution:
    def removeNodes(self, head: Optional[ListNode]) -> Optional[ListNode]:
        vals = []
        nodes = []
        res = []
        l = head
        vals.append(l.val)
        nodes.append(l)
        while l.next:
            l = l.next
            vals.append(l.val)
            nodes.append(l)

        root = None
        prev = None
        index = -1
        while index < len(vals) - 1:
            max_value = max(vals[index + 1:])
            res.append(ListNode(max_value))
            index = vals[index + 1:].index(max_value) + index + 1

            if not prev is None:
                prev.next = nodes[index]
            nodes[index].next = None
            prev = nodes[index]
            if root is None:
                root = nodes[index]

        return root


pp = [1, 5, 1, 1]
test = []
for p in pp:
    test.append(ListNode(p))

for i in range(len(test) - 1):
    test[i].next = test[i + 1]

x = Solution().removeNodes(test[0])

while x:
    print(x.val)
    x = x.next
