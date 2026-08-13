#include<stdio.h>
int main(){
    // Fake Array //
    int *ptr;
    *(ptr + 0) = 11;
    *(ptr + 1) = 22;
    *(ptr + 2) = 33;
    *(ptr + 3) = 44;
    
/////////   Values   //////////////
    printf("%d\n", *(ptr+0));
    printf("%d\n", *(ptr+1));
    printf("%d\n", *(ptr+2));
    printf("%d\n", *(ptr+3));

//////////   address   ////////////
    printf("%d\n", (ptr+0));
    printf("%d\n", (ptr+1));
    printf("%d\n", (ptr+2));
    printf("%d\n", (ptr+3));
    
    return 0;
}