from xyzflow import Parameter

# Define parameters
x = Parameter(value=10, description="XA")
y = Parameter(value=10, description="YA")
  
def main():
    return x + y
       
if __name__ == "__main__":   
    print(main()()) # Execute flow and print the result
  