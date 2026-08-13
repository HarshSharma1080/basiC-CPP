#include<stdio.h>

int main(){
    int arr[10];
    //the address of arr and the arr[0] (the first element of arr) is the same.  
    printf("%p == %p\n", arr, &arr[0]);

    // But the size of arr pointer is not the same as arr[0] pointer, 
    // because the arr is the container for the whole array and it acts as the constant pointer for that container.
    // but the arr[0] is just points to the first element of the array.
    // so the sizeof(arr) = sizeof(int)*10 and the sizeof(arr[0]) = sizeof(int) 
    printf("%zu != %zu\n", sizeof(arr), sizeof(arr[0]));

    int *p;
    p = arr;
    for(int i = 0; i <= 10; i++){
        ptr[i] = i;
        printf("%d\n", ptr[i]);
    }
    return 0;
}



