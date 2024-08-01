"""
Given a list nums_list,  return all the subarrays which contains the max element of nums_list atleast k times. 
Example: 
test case 1
nums_list = [2,4,1,4,4]    #4 
k = 2 
Output :  [2, 4, 1, 4], [4, 1, 4], [4, 1, 4, 4], [1, 4, 4], [4, 4], [2, 4, 1, 4, 4]

test case 2

Example 2:
nums_list = [5,3,5,1,5]

k = 3

Output: [5, 3, 5, 1, 5]
 
"""


num_list=input("Enter the array").str.split(",")
temp=num_list[0]
max_value_index=0 # #4 
max_rep= 2 # k 

arr=[]
count_max=0
# max(mnum_list)

# To get the max value from the array O(n)
for i in range(len(num_list)):
    if temp < num_list[i]:
        temp=num_list[i]
        max_value_index=i

for i in range(len(num_list)):
    arr=[]
    for j in range(i, len(num_list)):
        if temp == num_list[j]:
            count_max=count_max+1
            if count_max == max_rep:
                arr.append(num_list(j))
                print(arr)
                break;
        arr.append(num_list(j))






