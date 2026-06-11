# 2D Graphics Editor

This is a simple menu-driven 2D graphics editor written in C.

It uses a 2D character array to store the picture, `_` for empty space, and `*`
to draw objects.

## Features

- Draw a line
- Draw a rectangle
- Draw a circle
- Draw a triangle
- Add objects to the picture
- Delete objects by ID
- Modify objects by ID
- Display the current picture

## Build and Run

```powershell
gcc graphics_editor.c -o graphics_editor
.\graphics_editor
```

## Menu

```text
1. Add
2. Delete
3. Modify
4. List
5. Display
6. Exit
```
