#include<iostream>
#include<stdio.h>
#include<stdlib.h>

using namespace std;
int main() {
    int n{};
    cin >> n;
    int arr[n];
    arr[0] = 2;
    arr[1] = 1;
    arr[2] = 4;
    cout << arr[2] << endl;
    cout << arr[0] << endl;
    printf("%d\n", arr[1]);
    cout << sizeof(arr) << endl;

    cout << "___________________________________" << endl;
    for (auto x: arr) {
        cout << x << endl;
    }
    return 0;
}