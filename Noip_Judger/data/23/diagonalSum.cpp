#include<iostream>
#include<algorithm>
using namespace std;


int main()
{
    int a[15][15];
    int i, j, n, sum1 = 0, sum2 = 0;
    cin >> n;
    for(i = 0 ; i < n ; i++){
    	for(j = 0 ; j < n ; j++){
    		cin >> a[i][j];
    		if(i == j){
    			sum1 += a[i][j];
    		}
    	}
    }
    
    for(i = 0 ; i < n ; i++){
    	for(j = 0 ; j < n ; j++){
    		if( (i + j) == (n-1) ){
    			sum2 += a[i][j];
    		}
    	}
    }
    cout<< sum1 << " " << sum2 << endl;
    return 0;
}
