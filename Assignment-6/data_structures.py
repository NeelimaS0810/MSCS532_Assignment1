"""
Assignment 6 – Part 2: Elementary Data Structures
===================================================
Implements the following data structures from scratch:
  1. DynamicArray   – resizable array with O(1) amortised append
  2. Matrix         – 2-D array with basic operations
  3. Stack          – LIFO via array
  4. Queue          – FIFO via circular array
  5. SinglyLinkedList
  6. RootedTree     – general rooted tree via linked nodes (optional)

Every operation documents its time and space complexity.
"""

from __future__ import annotations
from typing import Any, Optional, List


# ─────────────────────────────────────────────────────────────
# 1.  DYNAMIC ARRAY
# ─────────────────────────────────────────────────────────────

class DynamicArray:
    """
    Resizable array that doubles capacity when full and halves
    capacity when less than 1/4 full (table doubling / halving).

    Complexities
    ────────────
    access   : O(1)
    append   : O(1) amortised  /  O(n) worst-case (resize)
    insert   : O(n)
    delete   : O(n)
    search   : O(n)
    """

    def __init__(self):
        self._capacity = 1
        self._size     = 0
        self._data     = [None] * self._capacity

    # ── helpers ──────────────────────────────────────────────

    def _resize(self, new_cap: int):
        """Copy data into a new backing store of size new_cap.  O(n)"""
        new_data = [None] * new_cap
        for i in range(self._size):
            new_data[i] = self._data[i]
        self._data     = new_data
        self._capacity = new_cap

    def _check_index(self, index: int):
        if not (0 <= index < self._size):
            raise IndexError(f"Index {index} out of range [0, {self._size})")

    # ── public interface ──────────────────────────────────────

    def __len__(self) -> int:                        # O(1)
        return self._size

    def __getitem__(self, index: int) -> Any:        # O(1)
        self._check_index(index)
        return self._data[index]

    def __setitem__(self, index: int, value: Any):   # O(1)
        self._check_index(index)
        self._data[index] = value

    def append(self, value: Any):                    # O(1) amortised
        if self._size == self._capacity:
            self._resize(self._capacity * 2)
        self._data[self._size] = value
        self._size += 1

    def insert(self, index: int, value: Any):        # O(n)
        if not (0 <= index <= self._size):
            raise IndexError(f"Index {index} out of range [0, {self._size}]")
        if self._size == self._capacity:
            self._resize(self._capacity * 2)
        # Shift elements right
        for i in range(self._size, index, -1):
            self._data[i] = self._data[i - 1]
        self._data[index] = value
        self._size += 1

    def delete(self, index: int) -> Any:             # O(n)
        self._check_index(index)
        value = self._data[index]
        # Shift elements left
        for i in range(index, self._size - 1):
            self._data[i] = self._data[i + 1]
        self._data[self._size - 1] = None
        self._size -= 1
        # Shrink if ≤ 1/4 full
        if self._size > 0 and self._size == self._capacity // 4:
            self._resize(self._capacity // 2)
        return value

    def search(self, value: Any) -> int:             # O(n)
        """Return index of first occurrence, or -1."""
        for i in range(self._size):
            if self._data[i] == value:
                return i
        return -1

    def __repr__(self) -> str:
        items = [str(self._data[i]) for i in range(self._size)]
        return f"DynamicArray([{', '.join(items)}])  cap={self._capacity}"


# ─────────────────────────────────────────────────────────────
# 2.  MATRIX
# ─────────────────────────────────────────────────────────────

class Matrix:
    """
    2-D matrix backed by a list-of-lists.

    Complexities
    ────────────
    access   (get/set cell) : O(1)
    add / subtract           : O(rows × cols)
    multiply                 : O(rows × cols × inner)
    transpose                : O(rows × cols)
    """

    def __init__(self, rows: int, cols: int, fill: Any = 0):
        if rows <= 0 or cols <= 0:
            raise ValueError("Dimensions must be positive")
        self._rows = rows
        self._cols = cols
        self._data = [[fill] * cols for _ in range(rows)]

    @classmethod
    def from_list(cls, data: List[List[Any]]) -> "Matrix":
        rows = len(data)
        cols = len(data[0]) if rows else 0
        m = cls(rows, cols)
        for i in range(rows):
            for j in range(cols):
                m._data[i][j] = data[i][j]
        return m

    # ── basic access ─────────────────────────────────────────

    def get(self, row: int, col: int) -> Any:        # O(1)
        return self._data[row][col]

    def set(self, row: int, col: int, val: Any):     # O(1)
        self._data[row][col] = val

    @property
    def shape(self):
        return (self._rows, self._cols)

    # ── arithmetic ───────────────────────────────────────────

    def __add__(self, other: "Matrix") -> "Matrix":  # O(r·c)
        if self.shape != other.shape:
            raise ValueError("Shape mismatch for addition")
        result = Matrix(self._rows, self._cols)
        for i in range(self._rows):
            for j in range(self._cols):
                result._data[i][j] = self._data[i][j] + other._data[i][j]
        return result

    def __sub__(self, other: "Matrix") -> "Matrix":  # O(r·c)
        if self.shape != other.shape:
            raise ValueError("Shape mismatch for subtraction")
        result = Matrix(self._rows, self._cols)
        for i in range(self._rows):
            for j in range(self._cols):
                result._data[i][j] = self._data[i][j] - other._data[i][j]
        return result

    def __matmul__(self, other: "Matrix") -> "Matrix":  # O(r·c·k)
        if self._cols != other._rows:
            raise ValueError(
                f"Cannot multiply ({self._rows}×{self._cols}) "
                f"by ({other._rows}×{other._cols})"
            )
        result = Matrix(self._rows, other._cols)
        for i in range(self._rows):
            for k in range(self._cols):
                for j in range(other._cols):
                    result._data[i][j] += self._data[i][k] * other._data[k][j]
        return result

    def transpose(self) -> "Matrix":                # O(r·c)
        result = Matrix(self._cols, self._rows)
        for i in range(self._rows):
            for j in range(self._cols):
                result._data[j][i] = self._data[i][j]
        return result

    def __repr__(self) -> str:
        rows_str = "\n  ".join(str(row) for row in self._data)
        return f"Matrix({self._rows}×{self._cols}):\n  {rows_str}"


# ─────────────────────────────────────────────────────────────
# 3.  STACK  (array-backed)
# ─────────────────────────────────────────────────────────────

class Stack:
    """
    LIFO stack backed by a Python list (dynamic array).

    Complexities
    ────────────
    push  : O(1) amortised
    pop   : O(1) amortised
    peek  : O(1)
    empty : O(1)
    """

    def __init__(self):
        self._data: List[Any] = []

    def push(self, value: Any):          # O(1) amortised
        self._data.append(value)

    def pop(self) -> Any:                # O(1) amortised
        if self.is_empty():
            raise IndexError("Pop from empty stack")
        return self._data.pop()

    def peek(self) -> Any:               # O(1)
        if self.is_empty():
            raise IndexError("Peek on empty stack")
        return self._data[-1]

    def is_empty(self) -> bool:          # O(1)
        return len(self._data) == 0

    def __len__(self) -> int:            # O(1)
        return len(self._data)

    def __repr__(self) -> str:
        return f"Stack(top→{self._data[::-1]})"


# ─────────────────────────────────────────────────────────────
# 4.  QUEUE  (circular array)
# ─────────────────────────────────────────────────────────────

class Queue:
    """
    FIFO queue implemented with a fixed-capacity circular array.
    Auto-doubles capacity when full.

    Complexities
    ────────────
    enqueue : O(1) amortised
    dequeue : O(1)
    peek    : O(1)
    empty   : O(1)
    """

    def __init__(self, initial_capacity: int = 8):
        self._capacity = initial_capacity
        self._data     = [None] * self._capacity
        self._head     = 0      # index of the front element
        self._size     = 0

    def _resize(self, new_cap: int):
        """Re-layout elements into a new backing array.  O(n)"""
        new_data = [None] * new_cap
        for i in range(self._size):
            new_data[i] = self._data[(self._head + i) % self._capacity]
        self._data     = new_data
        self._head     = 0
        self._capacity = new_cap

    def enqueue(self, value: Any):       # O(1) amortised
        if self._size == self._capacity:
            self._resize(self._capacity * 2)
        tail = (self._head + self._size) % self._capacity
        self._data[tail] = value
        self._size += 1

    def dequeue(self) -> Any:            # O(1)
        if self.is_empty():
            raise IndexError("Dequeue from empty queue")
        value = self._data[self._head]
        self._data[self._head] = None
        self._head = (self._head + 1) % self._capacity
        self._size -= 1
        return value

    def peek(self) -> Any:               # O(1)
        if self.is_empty():
            raise IndexError("Peek on empty queue")
        return self._data[self._head]

    def is_empty(self) -> bool:          # O(1)
        return self._size == 0

    def __len__(self) -> int:            # O(1)
        return self._size

    def __repr__(self) -> str:
        items = [self._data[(self._head + i) % self._capacity]
                 for i in range(self._size)]
        return f"Queue(front→{items})"


# ─────────────────────────────────────────────────────────────
# 5.  SINGLY LINKED LIST
# ─────────────────────────────────────────────────────────────

class _Node:
    __slots__ = ("value", "next")

    def __init__(self, value: Any):
        self.value: Any          = value
        self.next:  Optional[_Node] = None


class SinglyLinkedList:
    """
    Singly linked list with a sentinel head for cleaner logic.

    Complexities
    ────────────
    insert at head   : O(1)
    insert at tail   : O(n)  [O(1) with tail pointer — see append]
    insert at index  : O(n)
    delete at head   : O(1)
    delete by value  : O(n)
    search           : O(n)
    traverse         : O(n)
    """

    def __init__(self):
        self._head: Optional[_Node] = None
        self._tail: Optional[_Node] = None
        self._size: int             = 0

    def prepend(self, value: Any):       # O(1)
        node = _Node(value)
        node.next  = self._head
        self._head = node
        if self._tail is None:
            self._tail = node
        self._size += 1

    def append(self, value: Any):        # O(1)  (tail pointer)
        node = _Node(value)
        if self._tail:
            self._tail.next = node
        else:
            self._head = node
        self._tail = node
        self._size += 1

    def insert_at(self, index: int, value: Any):  # O(n)
        if index < 0 or index > self._size:
            raise IndexError(f"Index {index} out of range [0, {self._size}]")
        if index == 0:
            self.prepend(value)
            return
        if index == self._size:
            self.append(value)
            return
        curr = self._head
        for _ in range(index - 1):
            curr = curr.next
        node      = _Node(value)
        node.next = curr.next
        curr.next = node
        self._size += 1

    def delete_head(self) -> Any:        # O(1)
        if self._head is None:
            raise IndexError("Delete from empty list")
        value      = self._head.value
        self._head = self._head.next
        if self._head is None:
            self._tail = None
        self._size -= 1
        return value

    def delete_value(self, value: Any) -> bool:  # O(n)
        """Remove first occurrence of value; return True if found."""
        if self._head is None:
            return False
        if self._head.value == value:
            self.delete_head()
            return True
        curr = self._head
        while curr.next:
            if curr.next.value == value:
                if curr.next is self._tail:
                    self._tail = curr
                curr.next  = curr.next.next
                self._size -= 1
                return True
            curr = curr.next
        return False

    def search(self, value: Any) -> int:  # O(n)
        """Return 0-based index of first occurrence, or -1."""
        curr  = self._head
        index = 0
        while curr:
            if curr.value == value:
                return index
            curr  = curr.next
            index += 1
        return -1

    def to_list(self) -> List[Any]:       # O(n)
        result = []
        curr   = self._head
        while curr:
            result.append(curr.value)
            curr = curr.next
        return result

    def __len__(self) -> int:
        return self._size

    def __repr__(self) -> str:
        return " → ".join(str(x) for x in self.to_list()) + " → None"


# ─────────────────────────────────────────────────────────────
# 6.  ROOTED TREE  (optional)
# ─────────────────────────────────────────────────────────────

class TreeNode:
    """A node in a rooted tree – stores value, parent, and children."""

    __slots__ = ("value", "parent", "children")

    def __init__(self, value: Any):
        self.value:    Any           = value
        self.parent:   Optional[TreeNode] = None
        self.children: List[TreeNode]     = []

    def add_child(self, child: "TreeNode"):
        child.parent = self
        self.children.append(child)

    def __repr__(self) -> str:
        return f"TreeNode({self.value})"


class RootedTree:
    """
    General rooted tree.

    Complexities
    ────────────
    add_child      : O(1)
    depth(node)    : O(depth)
    height         : O(n)
    bfs_traversal  : O(n)
    dfs_traversal  : O(n)
    """

    def __init__(self, root_value: Any):
        self.root = TreeNode(root_value)

    def depth(self, node: TreeNode) -> int:          # O(depth)
        d    = 0
        curr = node
        while curr.parent:
            d   += 1
            curr = curr.parent
        return d

    def height(self, node: Optional[TreeNode] = None) -> int:  # O(n)
        if node is None:
            node = self.root
        if not node.children:
            return 0
        return 1 + max(self.height(c) for c in node.children)

    def bfs(self) -> List[Any]:                       # O(n)
        """Breadth-first traversal; returns list of values."""
        result = []
        queue  = [self.root]
        while queue:
            node   = queue.pop(0)
            result.append(node.value)
            queue.extend(node.children)
        return result

    def dfs_preorder(self, node: Optional[TreeNode] = None) -> List[Any]:  # O(n)
        """Pre-order DFS; returns list of values."""
        if node is None:
            node = self.root
        result = [node.value]
        for child in node.children:
            result.extend(self.dfs_preorder(child))
        return result

    def __repr__(self) -> str:
        return f"RootedTree(root={self.root.value}, height={self.height()})"


# ─────────────────────────────────────────────────────────────
# 7.  TESTS & DEMO
# ─────────────────────────────────────────────────────────────

def _separator(title: str):
    print(f"\n{'─'*55}")
    print(f"  {title}")
    print(f"{'─'*55}")


def demo_dynamic_array():
    _separator("DynamicArray")
    da = DynamicArray()
    for v in [10, 20, 30, 40, 50]:
        da.append(v)
    print("After appending 10-50:", da)
    da.insert(2, 99)
    print("After insert(2, 99):  ", da)
    removed = da.delete(2)
    print(f"After delete(2) [{removed}]:  ", da)
    print(f"Search 30 → index {da.search(30)}")
    print(f"da[1] = {da[1]}")


def demo_matrix():
    _separator("Matrix")
    A = Matrix.from_list([[1, 2], [3, 4]])
    B = Matrix.from_list([[5, 6], [7, 8]])
    print("A:", A)
    print("B:", B)
    print("A + B:", A + B)
    print("A @ B:", A @ B)
    print("A.T:  ", A.transpose())


def demo_stack():
    _separator("Stack")
    s = Stack()
    for v in [1, 2, 3]:
        s.push(v)
    print("Stack:", s)
    print("Pop:", s.pop())
    print("Peek:", s.peek())
    print("Stack:", s)


def demo_queue():
    _separator("Queue (circular array)")
    q = Queue(4)
    for v in [10, 20, 30]:
        q.enqueue(v)
    print("Queue:", q)
    print("Dequeue:", q.dequeue())
    q.enqueue(40)
    q.enqueue(50)   # triggers resize
    print("After dequeue+2 enqueues:", q)


def demo_linked_list():
    _separator("SinglyLinkedList")
    ll = SinglyLinkedList()
    for v in [1, 2, 3, 4, 5]:
        ll.append(v)
    print("List:", ll)
    ll.prepend(0)
    print("After prepend(0):", ll)
    ll.insert_at(3, 99)
    print("After insert_at(3, 99):", ll)
    ll.delete_value(99)
    print("After delete_value(99):", ll)
    print("Search 4 → index:", ll.search(4))


def demo_rooted_tree():
    _separator("RootedTree")
    t = RootedTree(1)
    n2 = TreeNode(2); n3 = TreeNode(3); n4 = TreeNode(4)
    n5 = TreeNode(5); n6 = TreeNode(6)
    t.root.add_child(n2)
    t.root.add_child(n3)
    n2.add_child(n4)
    n2.add_child(n5)
    n3.add_child(n6)
    print(t)
    print("BFS:           ", t.bfs())
    print("DFS pre-order: ", t.dfs_preorder())
    print("Height:        ", t.height())
    print("Depth of n6:   ", t.depth(n6))


if __name__ == "__main__":
    print("=" * 55)
    print("  Assignment 6 – Part 2: Elementary Data Structures")
    print("=" * 55)

    demo_dynamic_array()
    demo_matrix()
    demo_stack()
    demo_queue()
    demo_linked_list()
    demo_rooted_tree()