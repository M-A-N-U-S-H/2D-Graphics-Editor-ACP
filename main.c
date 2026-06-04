#include<stdio.h>
#define ROWS 10
#define COLS 20
char canvas[ROWS][COLS];
void initializeCanvas()
{
int i,j;
for(int i=0;i<ROWS;i++)
{
for(int j=0;j<COLS;j++)
{
canvas[i][j]='_';
}
}
}
void displayCanvas()
{
int i, j;
for(i = 0; i < ROWS; i++)
{
for(j = 0; j < COLS; j++)
{
printf("%c", canvas[i][j]);
}
printf("\n");
}
}
int main()
{
initializeCanvas();
displayCanvas();

return 0;
}

