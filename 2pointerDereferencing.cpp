#include<stdio.h>
int main(){
    int n;
    int *pn;
    int **ppn;
    int ***pppn;

    n = 42;
    pn = &n;
    ppn = &pn;
    pppn = &ppn;

    printf("n = %d, pppn = %p\n", n, ***pppn);
    printf("%p = %p\n", *pppn, &pn);
    printf("%p = %p\n", **pppn, &n);
    printf("%d = %d", *pn, n);

}