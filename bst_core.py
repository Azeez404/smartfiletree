# bst/bst_core.py

class FileNode:
    def __init__(self, filename):
        self.filename = filename
        self.left = None
        self.right = None

class FileBST:
    def __init__(self):
        self.root = None

    def insert(self, root, filename):
        if root is None:
            return FileNode(filename)

        if filename < root.filename:
            root.left = self.insert(root.left, filename)
        elif filename > root.filename:
            root.right = self.insert(root.right, filename)
        else:
            # Duplicate file
            pass
        return root

    def search(self, root, filename):
        if root is None or root.filename == filename:
            return root

        if filename < root.filename:
            return self.search(root.left, filename)
        else:
            return self.search(root.right, filename)

    def inorder(self, root):
        if root is not None:
            return self.inorder(root.left) + [root.filename] + self.inorder(root.right)
        else:
            return []
    
    def delete(self, root, filename):
        if root is None:
            return root

        if filename < root.filename:
            root.left = self.delete(root.left, filename)
        elif filename > root.filename:
            root.right = self.delete(root.right, filename)
        else:
            # Node to be deleted found
            if root.left is None:
                return root.right
            elif root.right is None:
                return root.left

            # Node with two children: Get inorder successor
            temp = self.get_min_node(root.right)
            root.filename = temp.filename
            root.right = self.delete(root.right, temp.filename)

        return root

    def get_min_node(self, root):
        while root.left is not None:
            root = root.left
        return root

