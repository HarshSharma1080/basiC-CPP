#include<stdio.h>
void printData(void *x, char i){
    if(i == 'i'){
        printf("the type of the x is int: %d\n", *((int *)x));
    }
    else if(i == 'c'){
        printf("the type of the x is char: %c\n", *((char *)x));
    }
    else if(i == 'f'){
        printf("the type of the x is float: %e\n", *((int *)x));
    }
    else{
        printf("Invalid data type");
    }
}
int main(){
    int value = 123;
    printData(&value, 'i');
    printData(&value, 'c');
    printData(&value, 'f');
    return 0;
}