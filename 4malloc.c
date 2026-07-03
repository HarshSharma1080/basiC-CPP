#include<stdio.h>
#include<stdlib.h>

///////This program allocated 10*4 = 40 bytes in the heap memory using malloc and then 
///////the for loop puts 10 values in the pointers
int main(){
    int *ptr;
    ptr = (int *)malloc(10*sizeof(int));
    for(int i = 0; i <= 40; i+=4){
        *(ptr + i) = i;
        printf("%d\n", *(ptr + i));
    }
    free(ptr);
}
//////////////////printing and storing numbers 1 to n in the heap using malloc and pointers /////////////////////
// int main(){
//     int *ptr;
//     int length = 100, num = 1;
//     ptr = (int *)malloc(length*sizeof(int));
//     for(int i = 0; i <= length*sizeof(int); i+=sizeof(int)){
//         *(ptr + i) = num;
//         printf("%d\n", *(ptr + i));
//         num++;
//     }
// }