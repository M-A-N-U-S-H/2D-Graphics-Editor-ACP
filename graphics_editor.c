#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define WIDTH 80
#define HEIGHT 40
#define MAX_OBJECTS 100

typedef enum { OBJ_LINE, OBJ_RECTANGLE, OBJ_CIRCLE, OBJ_TRIANGLE } ObjectType;

typedef struct {
  int id, x1, y1, x2, y2, x3, y3, radius;
  ObjectType type;
} GraphicObject;

GraphicObject objects[MAX_OBJECTS];
int num_objects = 0, next_id = 1;
char grid[HEIGHT][WIDTH];

void plot(int x, int y) {
  if (x >= 0 && x < WIDTH && y >= 0 && y < HEIGHT)
    grid[y][x] = '*';
}

void draw_line(int x0, int y0, int x1, int y1) {
  int dx = abs(x1 - x0), sx = x0 < x1 ? 1 : -1;
  int dy = -abs(y1 - y0), sy = y0 < y1 ? 1 : -1;
  int err = dx + dy, e2;
  for (;;) {
    plot(x0, y0);
    if (x0 == x1 && y0 == y1)
      break;
    e2 = 2 * err;
    if (e2 >= dy) {
      err += dy;
      x0 += sx;
    }
    if (e2 <= dx) {
      err += dx;
      y0 += sy;
    }
  }
}

void draw_rectangle(int x, int y, int w, int h) {
  draw_line(x, y, x + w - 1, y);
  draw_line(x, y + h - 1, x + w - 1, y + h - 1);
  draw_line(x, y, x, y + h - 1);
  draw_line(x + w - 1, y, x + w - 1, y + h - 1);
}

void draw_circle(int xc, int yc, int r) {
  int x = 0, y = r, d = 3 - 2 * r;
  while (y >= x) {
    plot(xc + x, yc + y);
    plot(xc - x, yc + y);
    plot(xc + x, yc - y);
    plot(xc - x, yc - y);
    plot(xc + y, yc + x);
    plot(xc - y, yc + x);
    plot(xc + y, yc - x);
    plot(xc - y, yc - x);
    x++;
    d += (d > 0) ? (y--, 4 * (x - y) + 10) : (4 * x + 6);
  }
}

void draw_triangle(int x1, int y1, int x2, int y2, int x3, int y3) {
  draw_line(x1, y1, x2, y2);
  draw_line(x2, y2, x3, y3);
  draw_line(x3, y3, x1, y1);
}

// Helper: Find object by ID
int find_object(int id) {
  for (int i = 0; i < num_objects; i++)
    if (objects[i].id == id)
      return i;
  return -1;
}

// Helper: Shared input logic for adding/modifying
void read_shape_data(GraphicObject *obj) {
  switch (obj->type) {
  case OBJ_LINE:
    printf("Enter x1 y1 x2 y2: ");
    scanf("%d %d %d %d", &obj->x1, &obj->y1, &obj->x2, &obj->y2);
    break;
  case OBJ_RECTANGLE:
    printf("Enter top-left x y, w, h: ");
    scanf("%d %d %d %d", &obj->x1, &obj->y1, &obj->x2, &obj->y2);
    break;
  case OBJ_CIRCLE:
    printf("Enter center x y, r: ");
    scanf("%d %d %d", &obj->x1, &obj->y1, &obj->radius);
    break;
  case OBJ_TRIANGLE:
    printf("Enter x1 y1 x2 y2 x3 y3: ");
    scanf("%d %d %d %d %d %d", &obj->x1, &obj->y1, &obj->x2, &obj->y2, &obj->x3,
          &obj->y3);
    break;
  }
}

void display_picture() {
  memset(grid, '_', sizeof(grid)); // Fast clear
  for (int i = 0; i < num_objects; i++) {
    GraphicObject *o = &objects[i];
    if (o->type == OBJ_LINE)
      draw_line(o->x1, o->y1, o->x2, o->y2);
    else if (o->type == OBJ_RECTANGLE)
      draw_rectangle(o->x1, o->y1, o->x2, o->y2);
    else if (o->type == OBJ_CIRCLE)
      draw_circle(o->x1, o->y1, o->radius);
    else if (o->type == OBJ_TRIANGLE)
      draw_triangle(o->x1, o->y1, o->x2, o->y2, o->x3, o->y3);
  }
  for (int y = 0; y < HEIGHT; y++) {
    for (int x = 0; x < WIDTH; x++)
      putchar(grid[y][x]);
    putchar('\n');
  }
}

void add_object() {
  if (num_objects >= MAX_OBJECTS) {
    printf("Max objects reached!\n");
    return;
  }
  printf("1.Line 2.Rectangle 3.Circle 4.Triangle\nChoice: ");
  int choice;
  if (scanf("%d", &choice) != 1 || choice < 1 || choice > 4)
    return;

  GraphicObject obj = {.id = next_id++, .type = (ObjectType)(choice - 1)};
  read_shape_data(&obj);
  objects[num_objects++] = obj;
  printf("Object added with ID %d\n", obj.id);
}

void delete_object() {
  printf("Enter ID to delete: ");
  int id;
  if (scanf("%d", &id) != 1)
    return;
  int idx = find_object(id);
  if (idx != -1) {
    for (int i = idx; i < num_objects - 1; i++)
      objects[i] = objects[i + 1];
    num_objects--;
    printf("Object %d deleted.\n", id);
  } else
    printf("Object not found!\n");
}

void modify_object() {
  printf("Enter ID to modify: ");
  int id;
  if (scanf("%d", &id) != 1)
    return;
  int idx = find_object(id);
  if (idx != -1) {
    printf("Modifying object %d.\n", id);
    read_shape_data(&objects[idx]);
    printf("Object %d modified.\n", id);
  } else
    printf("Object not found!\n");
}

void list_objects() {
  if (num_objects == 0) {
    printf("No objects.\n");
    return;
  }
  for (int i = 0; i < num_objects; i++) {
    GraphicObject *o = &objects[i];
    printf("ID: %d, ", o->id);
    if (o->type == OBJ_LINE)
      printf("Line (%d,%d) to (%d,%d)\n", o->x1, o->y1, o->x2, o->y2);
    else if (o->type == OBJ_RECTANGLE)
      printf("Rect at (%d,%d), %dx%d\n", o->x1, o->y1, o->x2, o->y2);
    else if (o->type == OBJ_CIRCLE)
      printf("Circle at (%d,%d), r=%d\n", o->x1, o->y1, o->radius);
    else if (o->type == OBJ_TRIANGLE)
      printf("Triangle (%d,%d), (%d,%d), (%d,%d)\n", o->x1, o->y1, o->x2, o->y2,
             o->x3, o->y3);
  }
}

int main() {
  int choice, running = 1;
  while (running) {
    printf("\n--- 2D Graphics Editor ---\n1. Add 2. Delete 3. Modify 4. List "
           "5. Display 6. Exit\nChoice: ");
    if (scanf("%d", &choice) != 1) {
      char c;
      while (scanf("%c", &c) == 1 && c != '\n')
        ;
      continue;
    }
    switch (choice) {
    case 1:
      add_object();
      break;
    case 2:
      delete_object();
      break;
    case 3:
      modify_object();
      break;
    case 4:
      list_objects();
      break;
    case 5:
      display_picture();
      break;
    case 6:
      running = 0;
      break;
    default:
      printf("Invalid choice!\n");
    }
  }
  return 0;
}