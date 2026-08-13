#include<iostream>
#include<stdio.h>
using namespace std;
struct playingCards {
    int face;
    int shape;
    int color;
};
struct complexNo {
    int real;
    int img;
}z1;
struct rectangle {
        int length;
        int breadth;
    };
int main() {
    // struct playingCards x{13, 4, 2};
    struct playingCards x[52];
    x[0].face = 3;
    x[0].shape = 2;
    x[0].color = 1;
    struct complexNo z{11, 13};
    struct rectangle r{10,15};
    z.real = 111;
    z.img = 222;
    z1.real = 3323;
    z1.img = 4343;
    r.length = 20;
    r.breadth = 10;
    printf("the Playing cards has %d faces, %d shapes and %d color\n", x[0].face, x[0].shape, x[0].color);
    printf("the real part of z is %d, and the img part of z is %d\n", z.real, z.img);
    cout << "the real part of the z1 is: " << z1.real << endl;
    cout << "the img part of the z2 is: " << z1.img << endl;
    printf("the area rectangle is %d", r.length * r.breadth);
    return 0;
}