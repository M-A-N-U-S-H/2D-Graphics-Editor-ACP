#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>

#define WIDTH 50
#define HEIGHT 20
#define MAX_SHAPES 100

// --- 1. Data Structures ---
typedef enum { LINE, RECT, TRIANGLE, CIRCLE } ShapeType;

typedef struct {
  int id;
  bool active;
  ShapeType type;
  int x[3], y[3]; // Stores up to 3 points (for triangles)
  int r;          // Radius for circles
} Shape;

Shape shapes[MAX_SHAPES];
int shape_count = 0;
int next_id = 1;

// --- 2. Object Management ---
// Get a shape's pointer so you can modify it
Shape *get_shape(int id) {
  for (int i = 0; i < shape_count; i++) {
    if (shapes[i].id == id && shapes[i].active)
      return &shapes[i];
  }
  return NULL;
}

int add_line(int x1, int y1, int x2, int y2) {
  Shape s = {next_id++, true, LINE, {x1, x2, 0}, {y1, y2, 0}, 0};
  shapes[shape_count++] = s;
  return s.id;
}

int add_rect(int x, int y, int w, int h) {
  Shape s = {next_id++, true, RECT, {x, w, 0}, {y, h, 0}, 0};
  shapes[shape_count++] = s;
  return s.id;
}

int add_triangle(int x1, int y1, int x2, int y2, int x3, int y3) {
  Shape s = {next_id++, true, TRIANGLE, {x1, x2, x3}, {y1, y2, y3}, 0};
  shapes[shape_count++] = s;
  return s.id;
}

int add_circle(int xc, int yc, int r) {
  Shape s = {next_id++, true, CIRCLE, {xc, 0, 0}, {yc, 0, 0}, r};
  shapes[shape_count++] = s;
  return s.id;
}

void delete_shape(int id) {
  Shape *s = get_shape(id);
  if (s)
    s->active = false;
}

// --- 3. Drawing Algorithms ---
void put_pixel(char canvas[HEIGHT][WIDTH], int x, int y) {
  if (x >= 0 && x < WIDTH && y >= 0 && y < HEIGHT)
    canvas[y][x] = '*';
}

void draw_line(char canvas[HEIGHT][WIDTH], int x0, int y0, int x1, int y1) {
  int dx = abs(x1 - x0), dy = abs(y1 - y0);
  int sx = x0 < x1 ? 1 : -1, sy = y0 < y1 ? 1 : -1;
  int err = dx - dy;
  while (1) {
    put_pixel(canvas, x0, y0);
    if (x0 == x1 && y0 == y1)
      break;
    int e2 = 2 * err;
    if (e2 > -dy) {
      err -= dy;
      x0 += sx;
    }
    if (e2 < dx) {
      err += dx;
      y0 += sy;
    }
  }
}

void draw_rect(char canvas[HEIGHT][WIDTH], int x, int y, int w, int h) {
  draw_line(canvas, x, y, x + w - 1, y);
  draw_line(canvas, x, y + h - 1, x + w - 1, y + h - 1);
  draw_line(canvas, x, y, x, y + h - 1);
  draw_line(canvas, x + w - 1, y, x + w - 1, y + h - 1);
}

void draw_triangle(char canvas[HEIGHT][WIDTH], int x1, int y1, int x2, int y2,
                   int x3, int y3) {
  draw_line(canvas, x1, y1, x2, y2);
  draw_line(canvas, x2, y2, x3, y3);
  draw_line(canvas, x3, y3, x1, y1);
}

void draw_circle(char canvas[HEIGHT][WIDTH], int xc, int yc, int r) {
  int x = 0, y = r, d = 3 - 2 * r;
  while (y >= x) {
    put_pixel(canvas, xc + x, yc + y);
    put_pixel(canvas, xc - x, yc + y);
    put_pixel(canvas, xc + x, yc - y);
    put_pixel(canvas, xc - x, yc - y);
    put_pixel(canvas, xc + y, yc + x);
    put_pixel(canvas, xc - y, yc + x);
    put_pixel(canvas, xc + y, yc - x);
    put_pixel(canvas, xc - y, yc - x);
    x++;
    if (d > 0) {
      y--;
      d += 4 * (x - y) + 10;
    } else
      d += 4 * x + 6;
  }
}

// --- 4. Display the Picture ---
void display() {
  char canvas[HEIGHT][WIDTH];

  // Clear canvas
  for (int i = 0; i < HEIGHT; i++)
    for (int j = 0; j < WIDTH; j++)
      canvas[i][j] = '_';

  // Draw active shapes
  for (int i = 0; i < shape_count; i++) {
    if (!shapes[i].active)
      continue;
    Shape s = shapes[i];
    if (s.type == LINE)
      draw_line(canvas, s.x[0], s.y[0], s.x[1], s.y[1]);
    else if (s.type == RECT)
      draw_rect(canvas, s.x[0], s.y[0], s.x[1], s.y[1]);
    else if (s.type == TRIANGLE)
      draw_triangle(canvas, s.x[0], s.y[0], s.x[1], s.y[1], s.x[2], s.y[2]);
    else if (s.type == CIRCLE)
      draw_circle(canvas, s.x[0], s.y[0], s.r);
  }

  // Print to console
  printf("\n");
  for (int i = 0; i < HEIGHT; i++) {
    for (int j = 0; j < WIDTH; j++)
      putchar(canvas[i][j]);
    putchar('\n');
  }
  for (int j = 0; j < WIDTH; j++)
    putchar('=');
  printf("\n");
}

// --- 5. Main Execution / Testing ---
int main() {
  printf("1. Adding a Rectangle and a Circle:\n");
  int rect_id = add_rect(2, 2, 10, 5);
  int circle_id = add_circle(30, 7, 5);
  display();

  printf("2. Adding a Triangle:\n");
  int tri_id = add_triangle(15, 10, 20, 2, 25, 10);
  display();

  printf("3. Modifying the Rectangle (Moving it and making it bigger):\n");
  Shape *rect = get_shape(rect_id);
  if (rect != NULL) {
    rect->x[0] = 5;  // new x
    rect->y[0] = 5;  // new y
    rect->x[1] = 15; // new width
    rect->y[1] = 8;  // new height
  }
  display();

  printf("4. Deleting the Circle:\n");
  delete_shape(circle_id);
  display();

  return 0;
}