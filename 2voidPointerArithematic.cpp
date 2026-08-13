//the void pointer arithematic is not possible but we can do it using an extension in GNU
#include<stdio.h>
int main(){
    float integer;
    void *data;

    integer = 42;
    data = &integer;

    for(int i = 0; i < sizeof(integer); i++){
        printf("%d\n", *((unsigned char *)(data)));
        data++;
    }


}