#include<iostream>
using namespace std;
int main(){
    int age = 10;
    int &r = age;

    cout <<  "age = " << age << endl;
    cout << "r = " << r << endl;

    age ++;
    cout << "age++" << endl;
    cout << "age = " << age << endl;
    cout << "r = " << r << endl;

    r++;
    cout << "r++" << endl; 
    cout << "age = " << age << endl;
    cout << "r = " << r << endl;
}
