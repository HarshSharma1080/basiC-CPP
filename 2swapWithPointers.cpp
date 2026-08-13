#include<stdio.h>
void swap(int *x, int *y);

int main(){
    int n1 = 100;
    int n2 = 200;
    printf("n1 = %d, n2 = %d\n", n1, n2);
    swap(&n1, &n2);
    printf("n1 = %d, n2 = %d\n", n1, n2);
}

void swap(int *x, int *y){
    int temp;
    temp = *x;
    *x = *y;
    *y = temp;

}